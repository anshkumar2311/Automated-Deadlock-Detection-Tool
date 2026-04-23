# Render Deployment Configuration

## Render Settings

**Root Directory:** (leave empty)

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
gunicorn backend.app:app
```

## Environment Variables
None required

## Deployment Checklist
- ✅ matplotlib.use('Agg') at top of backend/app.py
- ✅ gunicorn in requirements.txt
- ✅ Dynamic API_BASE using window.location.origin
- ✅ CORS enabled
- ✅ backend.app:app is importable
- ✅ All dependencies listed in requirements.txt
