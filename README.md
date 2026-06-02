# ⚡ DSA Visualizer

> Step-by-step Python code execution visualizer for learning Data Structures & Algorithms.
> Unlike Python Tutor, every intermediate expression evaluation is shown — not just variable assignments.

![DSA Visualizer](https://img.shields.io/badge/Stack-Next.js_15_%7C_FastAPI_%7C_Python_3.12-blue)
![Tests](https://img.shields.io/badge/Tests-10%2F10_passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What Makes It Different

Traditional visualizers like Python Tutor skip intermediate steps. DSA Visualizer shows **every sub-expression**:

```python
need = target - nums[i]
# With: target=9, nums=[2,7,11,15], i=0
```

**Visualization Timeline:**
| Step | Event | Expression |
|------|-------|-----------|
| 1 | Read `target` | `target` → `9` |
| 2 | Read `nums` | `nums` → `[2,7,11,15]` |
| 3 | Evaluate subscript | `nums[i]` → `nums[0]` |
| 4 | Resolve index | `nums[0]` → `2` |
| 5 | Evaluate binary op | `9 - 2` |
| 6 | Result | `9 - 2` → `7` |
| 7 | Assign | `need = 7` |

---

## 🏗️ Architecture

```
dsa-visualizer/
├── backend/                    # FastAPI + Python AST Engine
│   ├── app/
│   │   ├── main.py             # FastAPI app + CORS
│   │   ├── api/
│   │   │   └── routes.py       # /execute, /problems endpoints
│   │   ├── core/
│   │   │   └── ast_engine.py   # 🧠 Core: AST walker + event emitter
│   │   ├── models/
│   │   │   └── events.py       # Pydantic models (EventType, ExecutionEvent, etc.)
│   │   └── services/
│   │       └── problems.py     # Built-in DSA problem library
│   ├── tests/
│   │   └── test_ast_engine.py  # 10 pytest tests
│   ├── Dockerfile
│   ├── railway.toml
│   └── requirements.txt
│
├── frontend/                   # Next.js 15 + Framer Motion
│   ├── app/
│   │   ├── page.tsx            # 🎨 Main visualizer UI (all panels)
│   │   ├── layout.tsx          # Root layout with JetBrains Mono font
│   │   ├── globals.css         # Tailwind + custom scrollbars
│   │   ├── types/index.ts      # TypeScript interfaces
│   │   ├── lib/api.ts          # API client
│   │   └── hooks/
│   │       ├── usePlayback.ts  # ⏯ Step/play/pause/speed control
│   │       └── useExecution.ts # API call + state management
│   ├── Dockerfile
│   ├── vercel.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
├── docker-compose.yml          # Local full-stack dev
└── README.md
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/your-org/dsa-visualizer
cd dsa-visualizer
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
npm run dev
```

---

## 📡 API Reference

### `POST /api/execute`

Execute arbitrary Python code and receive execution events.

**Request:**
```json
{
  "code": "nums = [2, 7, 11, 15]\ntarget = 9\nneed = target - nums[0]",
  "initial_vars": {}
}
```

**Response:**
```json
{
  "success": true,
  "total_steps": 13,
  "events": [
    {
      "step": 11,
      "event_type": "binop_eval",
      "description": "Evaluate `9 - 2`",
      "expression": "9 - 2",
      "result": null,
      "color": "#f97316",
      "icon": "🔢",
      "memory": { "variables": { ... }, "call_stack": ["<module>"], "output": [] }
    }
  ]
}
```

### `GET /api/problems`

List all built-in DSA problems.

### `GET /api/problems/{id}`

Get a specific problem (id: `two_sum`, `binary_search`, `bubble_sort`, `fibonacci`, `max_subarray`, `palindrome_check`, `stack_operations`, `count_occurrences`).

### `POST /api/problems/{id}/execute`

Execute a built-in problem.

---

## 🧠 AST Engine

The core of DSA Visualizer is `backend/app/core/ast_engine.py`. It:

1. **Parses** Python source code using the built-in `ast` module
2. **Walks** every AST node recursively
3. **Emits events** at every sub-expression level:
   - `ASSIGNMENT_START` → starting to evaluate RHS
   - `VARIABLE_READ` → reading a variable
   - `SUBSCRIPT_EVAL` → `arr[i]` before index resolution
   - `SUBSCRIPT_RESULT` → `arr[0]` after index resolution with value
   - `BINOP_EVAL` → showing `9 - 2` with concrete values
   - `BINOP_RESULT` → showing `9 - 2 = 7`
   - `COMPARISON_EVAL/RESULT` → comparisons step-by-step
   - `IF_TEST` / `IF_BRANCH` → condition + which branch taken
   - `LOOP_START` / `LOOP_ITER` / `LOOP_END` → loop lifecycle
   - `FUNCTION_CALL` / `FUNCTION_RETURN` → function tracing
   - `ARRAY_INIT` / `DICT_INIT` → data structure creation

Each event includes a **full memory snapshot** (all variables + their current values + call stack).

---

## 🎨 Frontend UI

The frontend is a single-page Next.js app with four panels:

| Panel | Description |
|-------|-------------|
| **Code Editor** | Editable Python code with line highlighting |
| **Execution Timeline** | All events as clickable cards, color-coded by category |
| **Variables Panel** | Live variable state with array/dict visualization |
| **Memory Panel** | Current event detail + call stack + line number |

### Playback Controls
- ▶ **Play** — auto-advance through steps
- ⏸ **Pause** — stop at current step
- ⏪ **Previous** — go one step back
- ⏩ **Next** — go one step forward
- ⏮ **Reset** — jump to beginning
- **Progress bar** — click to jump to any step
- **Speed selector** — 0.5×, 1×, 2×, 4×

---

## 🚢 Deployment

### Deploy Backend to Railway

1. Create a Railway account at https://railway.app
2. New project → Deploy from GitHub → select `backend/` folder
3. Set `PORT` environment variable (Railway sets this automatically)
4. Copy the deployment URL (e.g., `https://dsa-visualizer-backend.railway.app`)

### Deploy Frontend to Vercel

1. Push to GitHub
2. Import project in Vercel → select `frontend/` folder
3. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app/api
   ```
4. Deploy

### GitHub Actions Secrets Required

| Secret | Description |
|--------|-------------|
| `RAILWAY_TOKEN` | Railway API token |
| `VERCEL_TOKEN` | Vercel API token |

---

## 🧪 Running Tests

```bash
cd backend
pip install pytest
python -m pytest tests/ -v
```

Expected output: **10 passed** in ~0.15s

---

## 🛡️ Security

- Code execution uses Python's `ast` module — **no `eval()` on untrusted code**
- Only safe built-ins are available in function calls (`len`, `range`, `print`, etc.)
- Code length is limited to 5,000 characters per request
- No file system or network access in executed code

---

## 📦 Supported DSA Problems

| Problem | Algorithm | Difficulty |
|---------|-----------|------------|
| Two Sum | Hash Map | Easy |
| Binary Search | Divide & Conquer | Easy |
| Bubble Sort | Sorting | Easy |
| Fibonacci | Dynamic Programming | Easy |
| Maximum Subarray | Kadane's Algorithm | Medium |
| Palindrome Check | Two Pointers | Easy |
| Stack Operations | Data Structures | Easy |
| Count Occurrences | Hash Map | Easy |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/add-problem`
3. Add your DSA problem to `backend/app/services/problems.py`
4. Add tests in `backend/tests/`
5. Submit a pull request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
