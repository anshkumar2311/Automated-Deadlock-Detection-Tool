# Automated Deadlock Detection Tool

A full-stack Operating Systems simulation project for detecting deadlocks using:

- Resource Allocation Graph (RAG) cycle detection
- Banker's Algorithm safety analysis
- Recovery and prevention recommendations
- Interactive frontend simulation and graph visualization
- Downloadable PDF reports

The backend is built with Flask and serves both API endpoints and the frontend UI.

## Key Features

- Detects deadlocks from user-defined processes and resources
- Uses two detection strategies:
  - Graph cycle detection (NetworkX)
  - Banker's Algorithm safety check
- Applies consistency rule to avoid contradictory outcomes across algorithms
- Generates Resource Allocation Graph image (`/api/graph`)
- Produces step-by-step simulation timeline (`/api/simulate` and included in `/api/detect`)
- Suggests deadlock recovery actions and prevention strategies
- Exports professional PDF report (`/api/report`)
- Includes unit tests for algorithms, detection flow, and strategy modules

## Tech Stack

- Python 3
- Flask + Flask-CORS
- NetworkX
- Matplotlib (headless/Agg)
- ReportLab (PDF generation)
- Gunicorn (production server)
- Vanilla HTML/CSS/JavaScript frontend

## Project Structure

```text
.
├── backend/
│   ├── app.py                      # Flask app entrypoint + static serving
│   ├── requirements.txt            # Python dependencies
│   ├── algorithms/
│   │   ├── rag_builder.py          # Builds Resource Allocation Graph
│   │   ├── cycle_detection.py      # Deadlock cycle detection logic
│   │   ├── bankers_algorithm.py    # Safety-state analysis
│   │   └── detection_engine.py     # Orchestrates all detection pipelines
│   ├── api/
│   │   └── routes.py               # REST endpoints
│   ├── models/
│   │   ├── process.py
│   │   ├── resource.py
│   │   └── system_state.py
│   ├── resolution/
│   │   ├── recovery.py             # Recovery actions (terminate/preempt/suggest)
│   │   └── prevention.py           # Prevention condition analysis
│   ├── utils/
│   │   ├── input_parser.py
│   │   ├── validator.py
│   │   ├── logger.py
│   │   └── report_generator.py
│   └── tests/
│       ├── test_detection.py
│       └── test_algorithms.py
├── frontend/
│   ├── index.html                  # UI shell
│   ├── app.js                      # Interaction logic and API integration
│   └── style.css                   # Dashboard styling
└── RENDER_DEPLOYMENT.md            # Render deployment notes
```

## How It Works

1. User defines resources (with instance counts) and processes (allocated/requested/max_need).
2. Backend validates and parses input into system-state models.
3. Detection engine runs:
   - RAG build + cycle detection
   - Banker's Algorithm safe/unsafe analysis
4. Backend returns:
   - final deadlock verdict
   - involved processes
   - algorithm-level details
   - graph metrics and generated graph URL
   - simulation steps
   - recovery and prevention recommendations

## API Reference

Base path: `/api`

### `POST /detect`
Runs full deadlock detection and returns all analysis data.

Request body:

```json
{
  "processes": [
    {
      "pid": "P1",
      "allocated": ["R1"],
      "requested": ["R2"],
      "max_need": ["R1", "R2"]
    }
  ],
  "resources": [
    { "rid": "R1", "instances": 1 },
    { "rid": "R2", "instances": 1 }
  ]
}
```

Response includes:

- `deadlock`
- `involved_processes`
- `cycle_detection`
- `bankers_algorithm`
- `graph_info`
- `resolution`
- `prevention`
- `simulation`
- `graph_url`

### `POST /simulate`
Returns simulation steps only.

### `POST /report`
Generates and downloads a PDF report for the submitted system state.

### `GET /graph`
Returns latest generated graph image (`image/png`).

### `GET /sample`
Returns sample input payload for quick testing.

### `GET /health`
Health endpoint.

## Local Development Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd Automated-Deadlock-Detection-Tool-Teja
```

### 2. Create virtual environment

Windows (PowerShell):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run the application

```bash
cd backend
python app.py
```

App URLs:

- Frontend: `http://localhost:5000`
- API health check: `http://localhost:5000/api/health`

## Running Tests

From `backend/`:

```bash
python -m unittest discover tests
```

## Deployment (Render)

Use the same settings documented in `RENDER_DEPLOYMENT.md`:

- Build Command:

```bash
pip install -r backend/requirements.txt
```

- Start Command:

```bash
gunicorn backend.app:app
```

Notes:

- Matplotlib is configured for headless environments (`Agg` backend).
- No environment variables are required for basic deployment.

## Fastest Deployment (No Setup Headache)

If you just want a live URL quickly, use Render or Railway with these settings.

### Option A: Render (recommended)

1. Push this repo to your fork branch `ansh`.
2. In Render, click **New +** -> **Web Service** -> connect your GitHub repo.
3. Render will auto-read `render.yaml` from repo root.
4. Click **Create Web Service**.

If Render asks for manual commands, use:

```bash
pip install -r backend/requirements.txt
```

```bash
gunicorn app:app --chdir backend
```

Health check path:

```text
/api/health
```

### Option B: Railway

1. Create a new project from GitHub repo.
2. Select branch `ansh`.
3. Railway will detect Python.
4. Set start command to:

```bash
gunicorn app:app --chdir backend
```

5. Deploy and open generated URL.

### Why this works

- Backend serves frontend files directly.
- Same domain hosts UI and API.
- You only run one process (`gunicorn`) and everything is live.

## Input Modeling Notes

- Multi-instance resources are represented via `instances` in the resource list.
- Per-process resource quantities are represented by repeating resource IDs in arrays.
  - Example: `"allocated": ["R1", "R1"]` means 2 units of `R1` are allocated.

## Roadmap Ideas

- Add process priorities and starvation-aware recovery policies
- Persist simulation runs and generated reports
- Add authentication and role-based access for shared environments
- Add CI pipeline for tests and linting
