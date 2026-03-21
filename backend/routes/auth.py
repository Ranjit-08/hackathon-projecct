from flask import Blueprint, request, jsonify
import bcrypt
from database import query
from utils.jwt_helper import generate_token

auth_bp = Blueprint('auth', __name__)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ── Company Auth ──────────────────────────────────────────────────────────────

@auth_bp.route('/company/register', methods=['POST'])
def company_register():
    d = request.get_json() or {}
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

    cid = query(
        'INSERT INTO companies (name, email, password_hash, phone) VALUES (%s,%s,%s,%s)',
        (name, email, _hash(pwd), phone), fetch=False
    )
    token = generate_token({'id': cid, 'role': 'company', 'name': name, 'email': email})
    return jsonify({'token': token, 'user': {'id': cid, 'name': name, 'email': email, 'role': 'company'}}), 201

@auth_bp.route('/company/login', methods=['POST'])
def company_login():
    d = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    pwd   = d.get('password', '')

    rows = query('SELECT * FROM companies WHERE email=%s', (email,))
    if not rows or not _verify(pwd, rows[0]['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    c = rows[0]
    token = generate_token({'id': c['id'], 'role': 'company', 'name': c['name'], 'email': c['email']})
    return jsonify({'token': token, 'user': {'id': c['id'], 'name': c['name'], 'email': c['email'], 'role': 'company'}})

# ── User Auth ─────────────────────────────────────────────────────────────────

@auth_bp.route('/user/register', methods=['POST'])
def user_register():
    d = request.get_json() or {}
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

    uid = query(
        'INSERT INTO users (name, email, password_hash, phone, skills) VALUES (%s,%s,%s,%s,%s)',
        (name, email, _hash(pwd), phone, skills), fetch=False
    )
    token = generate_token({'id': uid, 'role': 'user', 'name': name, 'email': email})
    return jsonify({'token': token, 'user': {'id': uid, 'name': name, 'email': email, 'role': 'user'}}), 201

@auth_bp.route('/user/login', methods=['POST'])
def user_login():
    d = request.get_json() or {}
    email = d.get('email', '').strip().lower()
    pwd   = d.get('password', '')

    rows = query('SELECT * FROM users WHERE email=%s', (email,))
    if not rows or not _verify(pwd, rows[0]['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    u = rows[0]
    token = generate_token({'id': u['id'], 'role': 'user', 'name': u['name'], 'email': u['email']})
    return jsonify({'token': token, 'user': {'id': u['id'], 'name': u['name'], 'email': u['email'], 'role': 'user'}})