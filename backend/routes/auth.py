from flask import Blueprint, request, jsonify
import bcrypt, random, time
from database import query
from utils.jwt_helper import generate_token
from utils.email import send_otp_email

auth_bp = Blueprint('auth', __name__)

# In-memory OTP store {email: {otp, name, password, phone, skills, expires}}
otp_store = {}

def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def _gen_otp():
    return str(random.randint(100000, 999999))

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
    otp_store[f'company_{email}'] = {
        'otp': otp, 'name': name, 'password': pwd,
        'phone': phone, 'expires': time.time() + 600
    }
    sent = send_otp_email(email, name, otp)
    if not sent:
        return jsonify({'error': 'Failed to send OTP email. Check SMTP settings.'}), 500
    return jsonify({'message': f'OTP sent to {email}'})

@auth_bp.route('/company/verify-otp', methods=['POST'])
def company_verify_otp():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    otp   = d.get('otp', '').strip()
    key   = f'company_{email}'

    if key not in otp_store:
        return jsonify({'error': 'No OTP found. Please register again.'}), 400
    rec = otp_store[key]
    if time.time() > rec['expires']:
        del otp_store[key]
        return jsonify({'error': 'OTP expired. Please register again.'}), 400
    if rec['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    cid = query(
        'INSERT INTO companies (name, email, password_hash, phone) VALUES (%s,%s,%s,%s)',
        (rec['name'], email, _hash(rec['password']), rec['phone']), fetch=False
    )
    del otp_store[key]
    token = generate_token({'id': cid, 'role': 'company', 'name': rec['name'], 'email': email})
    return jsonify({'token': token, 'user': {'id': cid, 'name': rec['name'], 'email': email, 'role': 'company'}}), 201

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
    otp_store[f'user_{email}'] = {
        'otp': otp, 'name': name, 'password': pwd,
        'phone': phone, 'skills': skills, 'expires': time.time() + 600
    }
    sent = send_otp_email(email, name, otp)
    if not sent:
        return jsonify({'error': 'Failed to send OTP email. Check SMTP settings.'}), 500
    return jsonify({'message': f'OTP sent to {email}'})

@auth_bp.route('/user/verify-otp', methods=['POST'])
def user_verify_otp():
    d     = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    otp   = d.get('otp', '').strip()
    key   = f'user_{email}'

    if key not in otp_store:
        return jsonify({'error': 'No OTP found. Please register again.'}), 400
    rec = otp_store[key]
    if time.time() > rec['expires']:
        del otp_store[key]
        return jsonify({'error': 'OTP expired. Please register again.'}), 400
    if rec['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    uid = query(
        'INSERT INTO users (name, email, password_hash, phone, skills) VALUES (%s,%s,%s,%s,%s)',
        (rec['name'], email, _hash(rec['password']), rec['phone'], rec['skills']), fetch=False
    )
    del otp_store[key]
    token = generate_token({'id': uid, 'role': 'user', 'name': rec['name'], 'email': email})
    return jsonify({'token': token, 'user': {'id': uid, 'name': rec['name'], 'email': email, 'role': 'user'}}), 201

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