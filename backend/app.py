from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth          import auth_bp
from routes.interviews    import interviews_bp
from routes.bookings      import bookings_bp
from routes.mock_interview import mock_bp

app = Flask(__name__)
CORS(app, origins=Config.FRONTEND_URL, supports_credentials=True)

app.register_blueprint(auth_bp,       url_prefix='/api/auth')
app.register_blueprint(interviews_bp, url_prefix='/api/interviews')
app.register_blueprint(bookings_bp,   url_prefix='/api/bookings')
app.register_blueprint(mock_bp,       url_prefix='/api/mock')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Walk-in Interview Platform'})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)