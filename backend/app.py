import matplotlib
matplotlib.use('Agg')

from flask import Flask, send_from_directory
from flask_cors import CORS
from api.routes import api
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app, origins=["*"])

app.register_blueprint(api, url_prefix='/api')

# Add debug route to list all routes
@app.route('/debug/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {'routes': routes}

# Add health check at root level
@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'Deadlock Detection API'}


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_frontend(path):
    # Handle static files
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, path)
    
    # For all other routes, serve index.html (SPA routing)
    return send_from_directory(FRONTEND_DIR, 'index.html')


if __name__ == '__main__':
    try:
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
        print("  GET  /health      - Health check (root)")
        print("  GET  /debug/routes - List all routes")
        print("=" * 60)
        print("Frontend: http://localhost:5000")
        print("=" * 60)

        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
