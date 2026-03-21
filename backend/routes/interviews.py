from flask import Blueprint, request, jsonify
from database import query
from utils.jwt_helper import token_required

interviews_bp = Blueprint('interviews', __name__)

def _serialize(interview):
    interview['interview_date'] = str(interview['interview_date'])
    interview['created_at']     = str(interview['created_at'])
    return interview

@interviews_bp.route('/', methods=['GET'])
def get_all():
    """Public — browse active upcoming interviews."""
    rows = query('''
        SELECT i.*, c.name AS company_name
        FROM interviews i
        JOIN companies c ON i.company_id = c.id
        WHERE i.status = 'active' AND i.interview_date >= CURDATE()
        ORDER BY i.interview_date ASC
    ''')
    for r in rows:
        _serialize(r)
        r['slots'] = query('SELECT * FROM time_slots WHERE interview_id=%s', (r['id'],))
    return jsonify({'interviews': rows})

@interviews_bp.route('/<int:iid>', methods=['GET'])
def get_one(iid):
    rows = query('''
        SELECT i.*, c.name AS company_name
        FROM interviews i JOIN companies c ON i.company_id = c.id
        WHERE i.id=%s
    ''', (iid,))
    if not rows:
        return jsonify({'error': 'Not found'}), 404
    r = _serialize(rows[0])
    r['slots'] = query('SELECT * FROM time_slots WHERE interview_id=%s', (iid,))
    return jsonify({'interview': r})

@interviews_bp.route('/', methods=['POST'])
@token_required(role='company')
def create():
    d    = request.get_json() or {}
    cid  = request.user['id']
    required = ['role', 'job_description', 'package', 'interview_date', 'candidates_required', 'slots']
    if not all(k in d for k in required):
        return jsonify({'error': f'Required fields: {", ".join(required)}'}), 400
    if not d['slots']:
        return jsonify({'error': 'At least one time slot required'}), 400

    iid = query('''
        INSERT INTO interviews
          (company_id, role, job_description, package, interview_date, location, candidates_required)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    ''', (cid, d['role'], d['job_description'], d['package'],
          d['interview_date'], d.get('location',''), d['candidates_required']), fetch=False)

    for s in d['slots']:
        query(
            'INSERT INTO time_slots (interview_id, slot_time, total_capacity) VALUES (%s,%s,%s)',
            (iid, s['time'], s.get('capacity', 10)), fetch=False
        )
    return jsonify({'message': 'Interview posted!', 'interview_id': iid}), 201

@interviews_bp.route('/company/mine', methods=['GET'])
@token_required(role='company')
def company_interviews():
    cid  = request.user['id']
    rows = query('''
        SELECT i.*,
          (SELECT COUNT(*) FROM bookings b WHERE b.interview_id=i.id AND b.status='confirmed') AS total_bookings
        FROM interviews i
        WHERE i.company_id=%s
        ORDER BY i.created_at DESC
    ''', (cid,))
    for r in rows:
        _serialize(r)
        r['slots'] = query('SELECT * FROM time_slots WHERE interview_id=%s', (r['id'],))
    return jsonify({'interviews': rows})

@interviews_bp.route('/<int:iid>/close', methods=['PUT'])
@token_required(role='company')
def close_interview(iid):
    cid = request.user['id']
    rows = query('SELECT id FROM interviews WHERE id=%s AND company_id=%s', (iid, cid))
    if not rows:
        return jsonify({'error': 'Not found or unauthorized'}), 404
    query("UPDATE interviews SET status='closed' WHERE id=%s", (iid,), fetch=False)
    return jsonify({'message': 'Interview closed'})