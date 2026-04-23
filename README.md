# OS Simulation Tool — Deadlock Detection System

Professional operating system simulation tool for detecting and analyzing deadlocks using multiple algorithms.

## 🎯 Features

### Core Detection
- **Banker's Algorithm** — Safe state analysis with proper vector comparison
- **Cycle Detection** — RAG-based circular wait identification using NetworkX
- **Consistency Enforcement** — Cycle detection overrides Banker's for accuracy

### Smart Input System
- **Dropdown Resource Selection** — No manual typing, prevents invalid entries
- **Multi-Select Interface** — Visual resource allocation with tags
- **Real-time Validation** — Client + server-side checks
- **Max Need ≥ Allocation** — Enforced constraint validation

### Visualization
- **Enhanced RAG Graph** — Professional matplotlib rendering
  - Circles = Processes (blue)
  - Squares = Resources (green)
  - Dashed red = Request edges
  - Solid blue = Allocation edges
- **Interactive Tabs** — Results / Simulation / Graph views

### Step-by-Step Simulation
- **Modal Interface** — Walkthrough of execution steps
- **Highlighted Nodes** — Visual tracking of involved processes/resources
- **Step Navigation** — Previous/Next controls with progress counter
- **Detailed Explanations** — Each step includes context

### PDF Report Export
- **Professional Layout** — ReportLab-generated reports
- **Complete Documentation** — System config, graph, results, recommendations
- **One-Click Download** — Instant PDF generation

### UX Improvements
- **Loading States** — Clear feedback during operations
- **Error Messages** — Detailed validation feedback
- **Responsive Design** — Mobile-friendly interface
- **Accessibility** — ARIA labels, keyboard navigation

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start server
python app.py
```

Server runs on `http://localhost:5000`

## 📖 Usage

### 1. Configure System
- Add resources with instance counts
- Add processes with:
  - **Allocated** — Currently held resources
  - **Requested** — Resources being waited for
  - **Max Need** — Maximum resource requirements

### 2. Run Detection
Click **Run Detection** to analyze the system state.

### 3. View Results
- **Results Tab** — Algorithm outputs, cycles, recommendations
- **Simulation Tab** — Step-by-step execution walkthrough
- **Graph Tab** — Visual RAG representation

### 4. Export Report
Click **Report** to download a comprehensive PDF analysis.

## 🏗️ Architecture

### Backend (`/backend`)

```
backend/
├── algorithms/
│   ├── bankers_algorithm.py    # Safe state detection
│   ├── cycle_detection.py      # RAG cycle finder
│   ├── detection_engine.py     # Main orchestrator
│   └── rag_builder.py          # Graph construction
├── api/
│   └── routes.py               # REST endpoints
├── models/
│   ├── process.py              # Process entity
│   ├── resource.py             # Resource entity
│   └── system_state.py         # State container
├── resolution/
│   ├── recovery.py             # Deadlock recovery strategies
│   └── prevention.py           # Prevention recommendations
├── utils/
│   ├── input_parser.py         # JSON validation
│   ├── validator.py            # Business logic validation
│   ├── logger.py               # Logging utility
│   └── report_generator.py     # PDF generation
└── app.py                      # Flask application
```

### Frontend (`/frontend`)

```
frontend/
├── index.html    # Semantic HTML structure
├── style.css     # Professional UI styling
└── app.js        # Modular JavaScript logic
```

## 🔌 API Endpoints

### `POST /api/detect`
Detect deadlocks and return full analysis.

**Request:**
```json
{
  "resources": [
    {"rid": "R1", "instances": 2}
  ],
  "processes": [
    {
      "pid": "P1",
      "allocated": ["R1"],
      "requested": ["R2"],
      "max_need": ["R1", "R2"]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "deadlock": false,
  "involved_processes": [],
  "cycle_detection": {...},
  "bankers_algorithm": {...},
  "graph_info": {...},
  "resolution": {...},
  "prevention": {...},
  "simulation": [...]
}
```

### `POST /api/report`
Generate and download PDF report.

### `GET /api/sample`
Get sample deadlock scenario.

### `GET /api/graph`
Retrieve generated RAG image.

### `GET /api/health`
Health check endpoint.

## 🧪 Testing

```bash
cd backend
python -m pytest tests/
```

## 🎨 Design Principles

### Correctness
- **Strict Banker's Algorithm** — Proper Available = Total - Allocated
- **Vector Comparison** — Need[i] ≤ Work for ALL resources
- **Consistency Rule** — Cycle detected → system MUST be unsafe

### Usability
- **Smart Inputs** — Dropdowns prevent typos
- **Visual Feedback** — Loading states, validation errors
- **Progressive Disclosure** — Tabs organize complex information

### Maintainability
- **Modular Code** — Separated concerns (API, algorithms, UI)
- **No Duplication** — Reusable components
- **Clear Naming** — Self-documenting code

## 📊 Example Scenarios

### Classic Deadlock
```
Resources: R1(1), R2(1)
P1: holds R1, wants R2
P2: holds R2, wants R1
→ DEADLOCK (circular wait)
```

### Safe State
```
Resources: R1(2), R2(2)
P1: holds R1(1), max R1(1)+R2(1)
P2: holds R2(1), max R1(1)+R2(1)
→ SAFE (sequence: P1 → P2)
```

## 🛠️ Technologies

- **Backend:** Flask, NetworkX, Matplotlib, ReportLab
- **Frontend:** Vanilla JavaScript, CSS Grid/Flexbox
- **Algorithms:** Banker's Algorithm, DFS Cycle Detection

## 📝 License

MIT License — Free for educational and commercial use.

## 👥 Contributing

Contributions welcome! Please ensure:
- Banker's algorithm correctness is maintained
- All tests pass
- Code follows existing style

## 🐛 Known Issues

None — fully functional professional tool.

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Built with precision for OS education and research.**
