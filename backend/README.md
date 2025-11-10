# Backend - AI Chart Generator

FastAPI backend with Pydantic AI for intelligent chart generation.

## Setup

### 1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── agents/          # Pydantic AI agents
│   ├── services/        # Business logic
│   ├── models/          # Pydantic schemas
│   ├── config/          # Settings
│   └── main.py          # FastAPI app
├── tests/               # Evaluation tests
├── charts/              # Generated charts
├── data/                # Session persistence
└── requirements.txt     # Python dependencies
```
