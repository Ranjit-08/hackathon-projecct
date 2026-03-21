import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from config import Config

def generate_token(payload: dict) -> str:
    payload['exp'] = datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS)
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def decode_token(token: str) -> dict:
    return jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])

def token_required(role=None):
    """Decorator — pass role='company' or role='user' to restrict access."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '').strip()
            if not token:
                return jsonify({'error': 'Authentication token required'}), 401
            try:
                data = decode_token(token)
                if role and data.get('role') != role:
                    return jsonify({'error': 'Access denied: wrong role'}), 403
                request.user = data
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Session expired, please login again'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator