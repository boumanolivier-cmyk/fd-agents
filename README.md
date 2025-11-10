# 📊 AI Chart Generator

An intelligent chart generation tool powered by OpenAI that creates beautiful bar and line charts from text or Excel input. Built with FastAPI, React, and TypeScript.

## ✨ Features

- 🤖 **AI-Powered**: Uses OpenAI to understand chart requests and extract data
- 📈 **Multiple Chart Types**: Bar charts and line charts
- 🎨 **Custom Color Schemes**: FD (teal/beige) and BNR (yellow/white) themes
- 📁 **Excel Support**: Upload Excel files for automatic data extraction
- 💬 **Chat Interface**: Natural language chart requests
- 🔄 **Session Memory**: Remembers your style preferences
- 🚫 **Smart Refusal**: Politely declines non-chart requests
- 💾 **Download Options**: Export as PNG or SVG
- 🐳 **Docker Ready**: Development and production Docker configurations

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI** for REST API
- **OpenAI SDK** for intelligent request processing
- **Matplotlib** for chart generation
- **Pandas** for Excel parsing
- **Pydantic** for data validation

### Frontend (React + TypeScript)
- **React 18** with TypeScript
- **Vite** for blazing fast development
- **MUI Material** for UI components
- **Jotai** for state management
- **Axios** for API communication

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- OpenAI API key
- Docker & Docker Compose (optional)

### Option 1: Local Development

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
API Docs: http://localhost:8000/docs

#### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:5173

### Option 2: Docker Development

```bash
# Copy environment template
cp .env.example backend/.env
# Add your OPENAI_API_KEY to backend/.env

# Start all services
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 3: Docker Production

```bash
# Add your OPENAI_API_KEY to backend/.env
cp .env.example backend/.env

# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Application: http://localhost
- Backend API: http://localhost:8000

## 📖 Usage Examples

### Chat Interface
```
User: "Create a bar chart showing Q1: 100, Q2: 150, Q3: 200, Q4: 175"
→ Generates a bar chart with quarterly data

User: "Make a line chart with Jan: 50, Feb: 75, Mar: 60, Apr: 90"
→ Generates a line chart with monthly trend

User: "What's the weather today?"
→ Politely refuses non-chart requests
```

### Excel Upload
1. Click "Upload Excel" tab
2. Drag & drop or select an Excel file
3. AI analyzes the data and generates appropriate chart
4. Download as PNG or SVG

### Style Selection
- **FD Theme**: Teal (#379596) on beige (#ffeadb) background
- **BNR Theme**: Yellow (#ffd200) on white background
- Preference is saved for future sessions

## 🧪 Testing

### Run Backend Tests
```bash
cd backend

# Test request validation (refusal logic)
python tests/eval_refusal.py

# Test chart data extraction accuracy
python tests/eval_chart_data.py
```

### Manual Testing Checklist
- [ ] Chat: Create bar chart with text input
- [ ] Chat: Create line chart with text input
- [ ] Upload: Parse Excel file and generate chart
- [ ] Style: Toggle between FD and BNR themes
- [ ] Download: Export chart as PNG
- [ ] Download: Export chart as SVG
- [ ] Refusal: Request non-chart task (should refuse)
- [ ] Session: Verify style preference persists

## 📁 Project Structure

```
AI-agents/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config/
│   │   │   └── settings.py      # Configuration & color schemes
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── agents/
│   │   │   └── chart_agent.py   # OpenAI agent logic
│   │   ├── services/
│   │   │   ├── chart_generator.py   # Matplotlib charts
│   │   │   ├── excel_parser.py      # Excel processing
│   │   │   └── persistence.py       # Session management
│   │   └── api/
│   │       └── routes.py        # API endpoints
│   ├── tests/
│   │   ├── eval_refusal.py      # Refusal validation
│   │   └── eval_chart_data.py   # Data accuracy tests
│   ├── data/                     # Session data (JSON)
│   ├── charts/                   # Generated charts
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main application
│   │   ├── types/index.ts       # TypeScript types
│   │   ├── state/atoms.ts       # Jotai atoms
│   │   ├── api/client.ts        # API client
│   │   └── components/
│   │       ├── ChatInterface.tsx    # Chat UI
│   │       ├── FileUpload.tsx       # Excel upload
│   │       ├── ChartDisplay.tsx     # Chart preview
│   │       └── StyleSelector.tsx    # Style toggle
│   ├── Dockerfile               # Production build
│   ├── Dockerfile.dev           # Development build
│   ├── nginx.conf               # Nginx configuration
│   └── package.json
├── docker-compose.yml           # Production compose
├── docker-compose.dev.yml       # Development compose
└── README.md
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
OPENAI_API_KEY=sk-your-key-here  # REQUIRED
PYTHONUNBUFFERED=1
```

### Color Schemes

Defined in `backend/app/config/settings.py`:

**FD Scheme**
- Primary: #379596 (teal)
- Content: #191919 (dark gray)
- Background: #ffeadb (beige)

**BNR Scheme**
- Primary: #ffd200 (yellow)
- Content: #000000 (black)
- Background: #ffffff (white)

## 🌐 API Endpoints

### Chat
```
POST /api/chat
Body: { "message": "Create a bar chart...", "session_id": "abc123" }
Response: { "status": "success", "chart_id": "xyz789", ... }
```

### Upload Excel
```
POST /api/upload
Body: FormData with "file" field
Response: { "status": "success", "chart_id": "xyz789", ... }
```

### Preferences
```
GET /api/preferences/{session_id}
POST /api/preferences
Body: { "session_id": "abc123", "color_scheme": "FD" }
```

### Download Chart
```
GET /api/charts/{chart_id}.png
GET /api/charts/{chart_id}.svg
```

Full API documentation: http://localhost:8000/docs

## 🐳 Docker Commands

### Development
```bash
# Start services
docker-compose -f docker-compose.dev.yml up

# Rebuild after changes
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Start services
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f

# Stop and remove
docker-compose down -v
```

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development
```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## 🎯 Design Decisions

1. **OpenAI over Pydantic AI**: Initially used pydantic-ai but switched to direct OpenAI SDK due to dependency conflicts (griffe module issues)

2. **Jotai over Redux**: Lightweight atomic state management perfect for this use case

3. **MUI Material**: Comprehensive component library with excellent TypeScript support

4. **Multi-stage Docker Builds**: Optimized production images with minimal size

5. **Nginx for Frontend**: Efficient static file serving with proper proxy configuration

## 🤝 Contributing

This is a learning project built as a demonstration of AI-powered tooling. Feel free to fork and modify!

## 📝 License

MIT License - Feel free to use this project for learning and development.

## 🙏 Acknowledgments

- Built during an AI-assisted development session
- Uses OpenAI's GPT-4 for intelligent chart request processing
- Color schemes based on FD and BNR branding guidelines

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the test files in `backend/tests/`
3. Ensure your OpenAI API key is valid and has credits

---

**Built with ❤️ using FastAPI, React, and OpenAI**
