# DSA Visualizer

A step-by-step Python code execution visualizer for Data Structures and Algorithms learning.

## 🎯 Features

- **Real-time Code Execution Visualization** - Watch your Python code execute step-by-step
- **Memory State Tracking** - See variable values, call stack, and output at each step
- **Timeline View** - Navigate through execution events with detailed descriptions
- **Speed Control** - Adjust playback speed from 0.25× to 4× or custom rates
- **Inline Annotations** - View current variable values right beside the code
- **Multiple Problem Sets** - Pre-built DSA problems (Two Sum, Binary Search, etc.)
- **Beautiful UI** - Dark theme with amber/gold color scheme for optimal visibility

## 🏗️ Architecture

### Backend
- **Framework:** FastAPI with Python 3.12
- **Core Engine:** AST-based Python code execution tracker
- **Features:**
  - Granular step-by-step event tracking
  - Variable state snapshots at each step
  - Memory management visualization
  - Safe code execution sandbox
  - 115+ execution events per algorithm

### Frontend
- **Framework:** Next.js 15.3.0 with React 19
- **UI Components:** Framer Motion for animations
- **Styling:** Tailwind CSS with custom amber theme
- **Features:**
  - Real-time event timeline
  - Interactive code editor with highlighting
  - Variables panel with type information
  - Memory panel with call stack
  - Playback controls (play, pause, step, speed)

## 📂 Project Structure

```
dsa-visualizer/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # REST API endpoints
│   │   ├── core/ast_engine.py     # AST execution engine
│   │   ├── models/events.py       # Data models for events
│   │   ├── services/problems.py   # DSA problem definitions
│   │   └── main.py                # FastAPI app
│   ├── tests/                     # Unit tests
│   ├── Dockerfile                 # Container configuration
│   └── requirements.txt           # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── hooks/                 # React hooks
│   │   ├── lib/api.ts             # API client
│   │   ├── types/index.ts         # TypeScript types
│   │   ├── page.tsx               # Main UI component
│   │   └── globals.css            # Global styles
│   ├── public/                    # Static assets
│   ├── package.json               # Node dependencies
│   ├── tailwind.config.js         # Tailwind configuration
│   └── Dockerfile                 # Container configuration
│
└── .gitignore
```

## 🚀 Getting Started

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Server runs on `http://localhost:8000`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
App runs on `http://localhost:3000`

### Environment Variables

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔧 Key Technologies

### Backend
- FastAPI - Modern async web framework
- Pydantic - Data validation
- Python AST - Abstract Syntax Tree parsing
- Uvicorn - ASGI server

### Frontend
- Next.js - React framework with optimization
- Framer Motion - Animation library
- Tailwind CSS - Utility-first CSS
- TypeScript - Type safety

## 📊 Execution Events Tracked

The AST engine tracks 20+ types of events:
- Variable assignment and reads
- Binary operations (math, comparisons)
- Control flow (if/else branches)
- Loops (for/while with iterations)
- Function calls and returns
- Data structure initialization
- Array/dictionary operations
- Print output

## 🎨 UI Features

- **Amber/Gold Color Scheme** - High visibility on dark background
- **Inline Code Annotations** - See values next to code lines
- **Variable Highlighting** - Animated dots mark active variables
- **Speed Controls** - 8 speed options from 0.25× to 4×
- **Tab Navigation** - Timeline, Variables, and Memory views
- **Sidebar Toggle** - Collapse problem list for more space
- **Responsive Design** - Works on desktop and tablets

## 🔐 Security

- **CVE-2025-66478 Fixed** - Next.js upgraded to 15.3.0
- **Safe Code Execution** - AST-based execution with limits
- **Input Validation** - Code length limited to 5000 characters
- **No External Dependencies** - Self-contained execution

## 📝 API Endpoints

- `POST /api/execute` - Execute custom Python code
- `GET /api/problems` - List all DSA problems
- `GET /api/problems/{id}` - Get specific problem
- `POST /api/problems/{id}/execute` - Execute problem code
- `GET /health` - Health check

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend type checking
cd frontend
npm run type-check

# Frontend build
npm run build
```

## 🌐 Deployment

### Render.com (Backend)
1. Connect GitHub repository
2. Select `backend` directory
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Use free tier

### Vercel (Frontend)
1. Import GitHub repository
2. Select `frontend` as root directory
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Auto-deploys on push to main

## 📈 Performance

- **Backend:** ~50ms per execution event generation
- **Frontend:** Smooth 60fps animations with Framer Motion
- **Bundle Size:** ~120KB (Next.js optimized)
- **Cold Start:** <2 seconds on Render.com free tier

## 🤝 Contributing

This is an educational project for learning DSA concepts. Feel free to:
- Add more DSA problem examples
- Improve the visualization UI
- Add more event types to track
- Optimize performance

## 📚 Learning Resources

- FastAPI docs: https://fastapi.tiangolo.com
- Next.js docs: https://nextjs.org/docs
- Python AST: https://docs.python.org/3/library/ast.html
- Framer Motion: https://www.framer.com/motion/

## 📄 License

This project is open source and available for educational purposes.

## 🎯 Future Enhancements

- [ ] Support for more languages (JavaScript, Java, C++)
- [ ] Recursive function visualization with tree diagrams
- [ ] Custom problem creation and sharing
- [ ] Dark/Light theme toggle
- [ ] Export visualization as videos
- [ ] Collaborative debugging with real-time sharing
- [ ] Integration with online judges
- [ ] Mobile app for iOS/Android

---

**Created by:** Shruti Chavda  
**Last Updated:** June 2026
