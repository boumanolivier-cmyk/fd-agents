# AI-Powered Chart Generation Tool - Project Plan

## Overview
Build an AI agent that generates bar/line charts from text or Excel input, with FD/BNR color schemes, session memory, and refusal capabilities for non-chart tasks.

## Tech Stack
- **Frontend**: React + TypeScript, Vite, Jotai, MUI
- **Backend**: Python, FastAPI, Pydantic AI
- **Charts**: Matplotlib
- **Containerization**: Docker + Docker Compose

## Project Structure
```
AI-agents/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── chart_agent.py   # Pydantic AI agent
│   │   │   └── prompts.py       # Agent prompts
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chart_generator.py
│   │   │   ├── excel_parser.py
│   │   │   └── persistence.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic models
│   │   └── config/
│   │       ├── __init__.py
│   │       └── settings.py
│   ├── tests/
│   │   ├── eval_refusal.py
│   │   └── eval_chart_data.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ChartDisplay.tsx
│   │   │   └── StyleSelector.tsx
│   │   ├── state/
│   │   │   └── atoms.ts         # Jotai atoms
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml           # Development
├── Dockerfile.prod              # Production (FE + BE)
├── nginx.conf                   # For production
└── README.md
```

## Step-by-Step Implementation Plan

### Phase 1: Backend Foundation (Steps 1-7)

#### Step 1: Project Setup & Backend Initialization
**Goal**: Create project structure and initialize Python backend

**Tasks**:
- Create directory structure
- Initialize Python virtual environment
- Create `requirements.txt` with dependencies:
  ```
  fastapi[all]
  pydantic-ai
  matplotlib
  pandas
  openpyxl
  python-multipart
  pillow
  python-dotenv
  ```
- Create basic FastAPI app with CORS
- Set up environment configuration

**Deliverable**: Running FastAPI server on `localhost:8000`

---

#### Step 2: AI Agent Implementation
**Goal**: Create Pydantic AI agent for request validation and data extraction

**Key Components**:
- **Agent Prompts**: Define system prompt for chart-only tasks
- **Request Classification**: Identify if request is chart-related or not
- **Data Extraction**: Parse text/data into structured format
- **Chart Type Detection**: Determine bar vs line chart
- **Refusal Logic**: Politely decline non-chart requests

**Pydantic Models**:
```python
class ChartRequest(BaseModel):
    is_valid: bool
    reason: str | None
    chart_type: Literal["bar", "line"] | None
    title: str | None
    x_labels: list[str] | None
    y_values: list[float] | None
    y_label: str | None
    x_label: str | None
```

**Deliverable**: Agent that validates and extracts chart data

---

#### Step 3: Chart Generation Service
**Goal**: Generate PNG/SVG charts with FD/BNR colors

**Color Schemes**:
```python
COLORS = {
    "fd": {
        "primary": "#379596",
        "content": "#191919",
        "background": "#ffeadb"
    },
    "bnr": {
        "primary": "#ffd200",
        "content": "#000",
        "background": "#fff"
    }
}
```

**Features**:
- Bar chart generation
- Line chart generation
- Apply color schemes
- Export as PNG and SVG
- Proper labeling and formatting

**Deliverable**: Function that generates styled charts

---

#### Step 4: Excel Processing
**Goal**: Parse Excel files to extract chart data

**Features**:
- Read Excel files (xlsx, xls)
- Auto-detect data structure
- Extract headers and values
- Handle various formats
- Send to AI agent for interpretation

**Deliverable**: Excel parser integrated with agent

---

#### Step 5: Session & Persistence
**Goal**: Remember user style preferences across sessions

**Implementation**:
- Simple JSON file storage or SQLite
- Session ID generation
- Store/retrieve style preference (FD/BNR)
- Session management middleware

**Deliverable**: Persistent style preferences

---

#### Step 6: API Endpoints
**Goal**: Create REST API for frontend

**Endpoints**:
```python
POST /api/chat
  Body: { "message": str, "session_id": str }
  Returns: { "response": str, "chart_url": str | null }

POST /api/upload
  Body: FormData (excel file)
  Returns: { "response": str, "chart_url": str | null }

GET /api/charts/{chart_id}
  Returns: Image file (PNG/SVG)

GET /api/preferences/{session_id}
  Returns: { "style": "fd" | "bnr" }

POST /api/preferences/{session_id}
  Body: { "style": "fd" | "bnr" }
  Returns: { "success": bool }
```

**Deliverable**: Complete REST API

---

#### Step 7: Evaluation Tests
**Goal**: Create automated tests for agent behavior

**Eval 1 - Request Validation**:
```python
test_cases = [
    ("Make a bar chart of sales data", True),
    ("Create a line chart for temperature", True),
    ("What's the weather today?", False),
    ("Write me a poem", False),
    ("Help me with my homework", False),
]
```

**Eval 2 - Chart Data Accuracy**:
```python
# Test that extracted data matches input
# Verify chart contains correct values
# Check labels are properly assigned
```

**Deliverable**: Passing eval tests

---

### Phase 2: Frontend Development (Steps 8-13)

#### Step 8: React + Vite Setup
**Goal**: Initialize frontend project

**Tasks**:
- Create Vite project: `npm create vite@latest frontend -- --template react-ts`
- Install dependencies:
  ```
  @mui/material @emotion/react @emotion/styled
  jotai
  axios
  ```
- Configure Vite for proxy to backend
- Set up basic routing (if needed)

**Deliverable**: Running React dev server

---

#### Step 9: State Management (Jotai)
**Goal**: Set up global state

**Atoms**:
```typescript
// atoms.ts
export const sessionIdAtom = atom<string>(generateSessionId())
export const chatHistoryAtom = atom<Message[]>([])
export const stylePreferenceAtom = atom<'fd' | 'bnr'>('fd')
export const currentChartAtom = atom<string | null>(null)
```

**Deliverable**: Centralized state management

---

#### Step 10: Chat Interface Component
**Goal**: Build conversational UI

**Features**:
- Message list display
- Text input field
- Send button
- Loading states
- Error handling
- MUI styling

**Deliverable**: Functional chat UI

---

#### Step 11: File Upload Component
**Goal**: Excel file upload with drag-and-drop

**Features**:
- Drag-and-drop zone
- File type validation (.xlsx, .xls)
- Upload progress
- Preview uploaded file name
- MUI styling

**Deliverable**: Working file upload

---

#### Step 12: Chart Display Component
**Goal**: Show generated charts

**Features**:
- Display PNG/SVG images
- Download button
- Zoom/preview
- Responsive sizing
- Loading skeleton

**Deliverable**: Chart viewer with download

---

#### Step 13: API Integration
**Goal**: Connect frontend to backend

**API Client**:
```typescript
// client.ts
export const sendMessage = async (message: string, sessionId: string)
export const uploadExcel = async (file: File, sessionId: string)
export const getPreferences = async (sessionId: string)
export const savePreferences = async (sessionId: string, style: string)
```

**Deliverable**: Full frontend-backend integration

---

### Phase 3: Docker & Deployment (Steps 14-17)

#### Step 14: Backend Dockerfile
**Goal**: Containerize Python backend

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deliverable**: Working backend container

---

#### Step 15: Frontend Dockerfile
**Goal**: Containerize React frontend

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Deliverable**: Optimized frontend container

---

#### Step 16: Development Docker Compose
**Goal**: Local development environment

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - ENV=development
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

**Deliverable**: `docker-compose up` works locally

---

#### Step 17: Production Dockerfile
**Goal**: Single container for both FE and BE

```dockerfile
# Multi-stage: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Build backend + serve frontend
FROM python:3.11-slim
WORKDIR /app

# Install nginx
RUN apt-get update && apt-get install -y nginx

# Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/app ./app

# Copy built frontend
COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

**Deliverable**: Production-ready container

---

### Phase 4: Testing & Documentation (Step 18-20)

#### Step 18: End-to-End Testing
**Goal**: Test with provided prompts

**Test Cases**:
1. Public transport check-ins prompt
2. Student debt prompt
3. Excel file uploads
4. Refusal scenarios
5. Style preference persistence

**Deliverable**: All test cases passing

---

#### Step 19: Documentation
**Goal**: Complete README and setup guide

**Content**:
- Project overview
- Prerequisites
- Setup instructions (local & Docker)
- Environment variables
- API documentation
- Testing guide
- Troubleshooting

**Deliverable**: Comprehensive README.md

---

#### Step 20: Final Polish
**Goal**: Code cleanup and optimization

**Tasks**:
- Code formatting and linting
- Remove console.logs
- Optimize bundle sizes
- Add error boundaries
- Performance testing
- Security review

**Deliverable**: Production-ready application

---

## Estimated Timeline
- **Phase 1** (Backend): ~2 hours
- **Phase 2** (Frontend): ~1.5 hours
- **Phase 3** (Docker): ~30 minutes
- **Phase 4** (Testing/Docs): ~30 minutes

**Total**: ~4.5 hours (with buffer)

## Key Technical Decisions

### 1. AI Agent Design
- Use Pydantic AI's structured outputs for reliable data extraction
- System prompt focused on chart-only tasks
- Few-shot examples for refusal scenarios

### 2. Chart Generation
- Matplotlib for reliable Python-based charting
- Custom styling functions for FD/BNR themes
- Export both PNG (raster) and SVG (vector)

### 3. Session Management
- Generate UUID for each session
- Store in localStorage (frontend) and simple JSON/SQLite (backend)
- Future: Could upgrade to Redis for scalability

### 4. Frontend Architecture
- Jotai for lightweight, atomic state
- MUI for rapid UI development
- Axios for API calls with interceptors

### 5. Docker Strategy
- Development: separate containers with volume mounts
- Production: nginx serves static frontend, proxies /api to FastAPI
- Single container simplifies deployment

## Next Steps

Ready to start implementation! We can proceed in order through the phases, or you can tell me which step you'd like to begin with.

**Suggested starting point**: Step 1 - Project Setup & Backend Initialization

Would you like me to begin with Step 1, or would you prefer to start elsewhere?
