from flask import Blueprint, request, jsonify
from database import get_connection, query
from utils.jwt_helper import token_required
from utils.email import send_booking_confirmation

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/', methods=['POST'])
@token_required(role='user')
def book():
    d            = request.get_json() or {}
    user_id      = request.user['id']
    interview_id = d.get('interview_id')
    slot_id      = d.get('slot_id')

    if not interview_id or not slot_id:
        return jsonify({'error': 'interview_id and slot_id required'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. One active booking constraint
            cur.execute('''
                SELECT b.id, i.role, c.name AS company_name, i.interview_date
                FROM bookings b
                JOIN interviews i ON b.interview_id = i.id
                JOIN companies c  ON i.company_id   = c.id
                WHERE b.user_id=%s AND b.status='confirmed' AND i.interview_date >= CURDATE()
            ''', (user_id,))
            active = cur.fetchone()
            if active:
                return jsonify({
                    'error': 'You already have an active booking. Cancel or complete it first.',
                    'active_booking': {**active, 'interview_date': str(active['interview_date'])}
                }), 409

            # 2. Slot availability (lock row)
            cur.execute(
                'SELECT * FROM time_slots WHERE id=%s AND interview_id=%s FOR UPDATE',
                (slot_id, interview_id)
            )
            slot = cur.fetchone()
            if not slot:
                return jsonify({'error': 'Slot not found'}), 404
            if slot['booked_count'] >= slot['total_capacity']:
                return jsonify({'error': 'Slot is fully booked'}), 409

            # 3. No duplicate booking for same interview
            cur.execute(
                'SELECT id FROM bookings WHERE user_id=%s AND interview_id=%s',
                (user_id, interview_id)
            )
            if cur.fetchone():
                return jsonify({'error': 'You already booked this interview'}), 409

            # 4. Create booking + increment count
            cur.execute(
                "INSERT INTO bookings (user_id, interview_id, slot_id, status) VALUES (%s,%s,%s,'confirmed')",
                (user_id, interview_id, slot_id)
            )
            booking_id = cur.lastrowid
            cur.execute(
                'UPDATE time_slots SET booked_count = booked_count + 1 WHERE id=%s', (slot_id,)
            )
            conn.commit()

            # 5. Fetch details for email
            cur.execute('''
                SELECT u.name, u.email, c.name AS company_name,
                       i.role, i.interview_date, ts.slot_time
                FROM bookings b
                JOIN users      u  ON b.user_id      = u.id
                JOIN interviews i  ON b.interview_id  = i.id
                JOIN companies  c  ON i.company_id    = c.id
                JOIN time_slots ts ON b.slot_id       = ts.id
                WHERE b.id=%s
            ''', (booking_id,))
            det = cur.fetchone()

        if det:
            send_booking_confirmation(
                det['name'], det['email'],
                det['company_name'], det['role'],
                str(det['interview_date']), det['slot_time']
            )
        return jsonify({'message': 'Booking confirmed!', 'booking_id': booking_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bookings_bp.route('/my', methods=['GET'])
@token_required(role='user')
def my_bookings():
    rows = query('''
        SELECT b.*, i.role, i.package, i.interview_date, i.location,
               c.name AS company_name, ts.slot_time
        FROM bookings b
        JOIN interviews i  ON b.interview_id = i.id
        JOIN companies  c  ON i.company_id   = c.id
        JOIN time_slots ts ON b.slot_id      = ts.id
        WHERE b.user_id=%s
        ORDER BY b.booked_at DESC
    ''', (request.user['id'],))
    for r in rows:
        r['interview_date'] = str(r['interview_date'])
        r['booked_at']      = str(r['booked_at'])
    return jsonify({'bookings': rows})

@bookings_bp.route('/<int:bid>/cancel', methods=['PUT'])
@token_required(role='user')
def cancel(bid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM bookings WHERE id=%s AND user_id=%s AND status='confirmed'",
                (bid, request.user['id'])
            )
            bk = cur.fetchone()
            if not bk:
                return jsonify({'error': 'Booking not found or already cancelled'}), 404
            cur.execute("UPDATE bookings SET status='cancelled' WHERE id=%s", (bid,))
            cur.execute('UPDATE time_slots SET booked_count = booked_count - 1 WHERE id=%s', (bk['slot_id'],))
            conn.commit()
        return jsonify({'message': 'Booking cancelled'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bookings_bp.route('/interview/<int:iid>', methods=['GET'])
@token_required(role='company')
def interview_bookings(iid):
    owned = query('SELECT id FROM interviews WHERE id=%s AND company_id=%s', (iid, request.user['id']))
    if not owned:
        return jsonify({'error': 'Unauthorized'}), 403
    rows = query('''
        SELECT b.id, b.status, b.booked_at,
               u.name AS user_name, u.email AS user_email, u.phone AS user_phone, u.skills,
               ts.slot_time
        FROM bookings b
        JOIN users      u  ON b.user_id = u.id
        JOIN time_slots ts ON b.slot_id = ts.id
        WHERE b.interview_id=%s
        ORDER BY ts.slot_time, b.booked_at
    ''', (iid,))
    for r in rows:
        r['booked_at'] = str(r['booked_at'])
    return jsonify({'bookings': rows})