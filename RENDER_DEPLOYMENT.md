# Render Deployment Configuration

## Render Settings

**Root Directory:** (leave empty)

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

## Environment Variables
None required

## Deployment Checklist
- ✅ matplotlib.use('Agg') at top of backend/app.py
- ✅ gunicorn in requirements.txt
- ✅ Dynamic API_BASE using window.location.origin
- ✅ CORS enabled with origins=["*"]
- ✅ app:app is importable from backend directory
- ✅ All dependencies listed in requirements.txt
- ✅ SPA routing fallback to index.html
- ✅ PORT environment variable support
- ✅ Error handling and logging in all routes
