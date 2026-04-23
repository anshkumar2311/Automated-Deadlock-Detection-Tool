from flask import Flask, send_from_directory
from flask_cors import CORS
from api.routes import api
import os

# Absolute path to the frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

# Use frontend as the static folder so /style.css, /app.js are served automatically
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

app.register_blueprint(api, url_prefix='/api')


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_frontend(path):
    """Serve any file from the frontend directory."""
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, path)
    return {'error': 'Not found'}, 404


if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

    print("=" * 60)
    print("Deadlock Detection Tool - Server Starting")
    print("=" * 60)
    print(f"Frontend directory: {FRONTEND_DIR}")
    print("API Endpoints:")
    print("  POST /api/detect  - Detect deadlocks")
    print("  GET  /api/sample  - Get sample input")
    print("  GET  /api/graph   - Get graph visualization")
    print("  GET  /api/health  - Health check")
    print("=" * 60)
    print("Frontend: http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
