from flask import Blueprint, request, jsonify
import bcrypt, random, json
from datetime import datetime, timedelta
from database import query
from utils.jwt_helper import generate_token
from utils.email import send_otp_email

auth_bp = Blueprint('auth', __name__)

def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def _gen_otp():
    return str(random.randint(100000, 999999))

def _save_otp(key, otp, data):
    expires = (datetime.utcnow() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    # Delete existing
    query('DELETE FROM otp_store WHERE key_name=%s', (key,), fetch=False)
    # Insert new
    query(
        'INSERT INTO otp_store (key_name, otp, data, expires_at) VALUES (%s,%s,%s,%s)',
        (key, otp, json.dumps(data), expires), fetch=False
    )

def _get_otp(key):
    rows = query('SELECT * FROM otp_store WHERE key_name=%s', (key,))
    if not rows:
        return None, 'No OTP found. Please register again.'
    rec = rows[0]
    if datetime.utcnow() > rec['expires_at']:
        query('DELETE FROM otp_store WHERE key_name=%s', (key,), fetch=False)
        return None, 'OTP expired. Please register again.'
    return rec, None

def _delete_otp(key):
    query('DELETE FROM otp_store WHERE key_name=%s', (key,), fetch=False)

# ── Company Auth ──────────────────────────────────────────────────────────────

@auth_bp.route('/company/send-otp', methods=['POST'])
def company_send_otp():
    d     = request.get_json() or {}
    name  = d.get('name', '').strip()
    email = d.get('email', '').strip().lower()
    pwd   = d.get('password', '')
    phone = d.get('phone', '')

    if not all([name, email, pwd]):
        return jsonify({'error': 'Name, email and password are required'}), 400
    if len(pwd) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if query('SELECT id FROM companies WHERE email=%s', (email,)):
        return jsonify({'error': 'Email already registered'}), 409

    otp = _gen_otp()
    _save_otp(f'company_{email}', otp, {
        'name': name, 'password': pwd, 'phone': phone
    })

    sent = send_otp_email(email, name, otp)
    if not sent:
        return jsonify({'error': 'Failed to send OTP. Check SMTP settings.'}), 500
    return jsonify({'message': f'OTP sent to {email}'})

@auth_bp.route('/company/verify-otp', methods=['POST'])
def company_verify_otp():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    otp   = d.get('otp', '').strip()

    rec, err = _get_otp(f'company_{email}')
    if err:
        return jsonify({'error': err}), 400
    if rec['otp'] != otp:
        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

    data = json.loads(rec['data'])
    _delete_otp(f'company_{email}')

    cid = query(
        'INSERT INTO companies (name, email, password_hash, phone) VALUES (%s,%s,%s,%s)',
        (data['name'], email, _hash(data['password']), data['phone']), fetch=False
    )
    token = generate_token({'id': cid, 'role': 'company', 'name': data['name'], 'email': email})
    return jsonify({
        'token': token,
        'user': {'id': cid, 'name': data['name'], 'email': email, 'role': 'company'}
    }), 201

@auth_bp.route('/company/login', methods=['POST'])
def company_login():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    pwd   = d.get('password', '')
    rows  = query('SELECT * FROM companies WHERE email=%s', (email,))
    if not rows or not _verify(pwd, rows[0]['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401
    c = rows[0]
    token = generate_token({'id': c['id'], 'role': 'company', 'name': c['name'], 'email': c['email']})
    return jsonify({'token': token, 'user': {'id': c['id'], 'name': c['name'], 'email': c['email'], 'role': 'company'}})

# ── User Auth ─────────────────────────────────────────────────────────────────

@auth_bp.route('/user/send-otp', methods=['POST'])
def user_send_otp():
    d      = request.get_json() or {}
    name   = d.get('name', '').strip()
    email  = d.get('email', '').strip().lower()
    pwd    = d.get('password', '')
    phone  = d.get('phone', '')
    skills = d.get('skills', '')

    if not all([name, email, pwd]):
        return jsonify({'error': 'Name, email and password are required'}), 400
    if len(pwd) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if query('SELECT id FROM users WHERE email=%s', (email,)):
        return jsonify({'error': 'Email already registered'}), 409

    otp = _gen_otp()
    _save_otp(f'user_{email}', otp, {
        'name': name, 'password': pwd, 'phone': phone, 'skills': skills
    })

    sent = send_otp_email(email, name, otp)
    if not sent:
        return jsonify({'error': 'Failed to send OTP. Check SMTP settings.'}), 500
    return jsonify({'message': f'OTP sent to {email}'})

@auth_bp.route('/user/verify-otp', methods=['POST'])
def user_verify_otp():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    otp   = d.get('otp', '').strip()

    rec, err = _get_otp(f'user_{email}')
    if err:
        return jsonify({'error': err}), 400
    if rec['otp'] != otp:
        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

    data = json.loads(rec['data'])
    _delete_otp(f'user_{email}')

    uid = query(
        'INSERT INTO users (name, email, password_hash, phone, skills) VALUES (%s,%s,%s,%s,%s)',
        (data['name'], email, _hash(data['password']), data['phone'], data['skills']), fetch=False
    )
    token = generate_token({'id': uid, 'role': 'user', 'name': data['name'], 'email': email})
    return jsonify({
        'token': token,
        'user': {'id': uid, 'name': data['name'], 'email': email, 'role': 'user'}
    }), 201

@auth_bp.route('/user/login', methods=['POST'])
def user_login():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    pwd   = d.get('password', '')
    rows  = query('SELECT * FROM users WHERE email=%s', (email,))
    if not rows or not _verify(pwd, rows[0]['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401
    u = rows[0]
    token = generate_token({'id': u['id'], 'role': 'user', 'name': u['name'], 'email': u['email']})
    return jsonify({'token': token, 'user': {'id': u['id'], 'name': u['name'], 'email': u['email'], 'role': 'user'}})