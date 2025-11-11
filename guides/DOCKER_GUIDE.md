# 🐳 Docker Compose Quick Start Guide

## Prerequisites Checklist

### 1. ✅ Docker Desktop Running
Make sure Docker Desktop is running:
- **Mac**: Look for Docker whale icon in menu bar
- **Windows**: Check system tray for Docker icon
- **Linux**: Run `sudo systemctl status docker`

To start Docker Desktop on Mac:
```bash
open -a Docker
# Wait 30-60 seconds for Docker to fully start
```

Verify Docker is running:
```bash
docker info
# Should show Docker information without errors
```

### 2. ✅ OpenAI API Key Set

Edit `/Users/obouman/Documents/learning/AI-agents/backend/.env`:
```bash
# Replace 'sk-proj-your-key-here' with your actual OpenAI API key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

Get your API key from: https://platform.openai.com/api-keys

## Running with Docker Compose

### Option 1: Development Mode (Recommended for Testing)
**Features**: Hot-reload, source code mounting, easier debugging

```bash
cd /Users/obouman/Documents/learning/AI-agents

# Start services (will build first time)
docker compose -f docker-compose.dev.yml up --build

# Or run in background
docker compose -f docker-compose.dev.yml up -d --build

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop services
docker compose -f docker-compose.dev.yml down
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Production Mode
**Features**: Optimized builds, Nginx serving, smaller images

```bash
cd /Users/obouman/Documents/learning/AI-agents

# Start services
docker compose up --build

# Or run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Access**:
- Application: http://localhost (port 80)
- Backend API: http://localhost:8000

## Step-by-Step First Run

### Step 1: Start Docker Desktop
```bash
# On macOS
open -a Docker

# Wait until you see the Docker whale icon in your menu bar
# It should say "Docker Desktop is running"
```

### Step 2: Verify Docker is Ready
```bash
docker info
# Should output Docker system information
```

### Step 3: Set Your OpenAI API Key
```bash
# Edit the .env file
code /Users/obouman/Documents/learning/AI-agents/backend/.env

# Or use nano
nano /Users/obouman/Documents/learning/AI-agents/backend/.env
```

Replace `sk-proj-your-key-here` with your actual key.

### Step 4: Navigate to Project Directory
```bash
cd /Users/obouman/Documents/learning/AI-agents
```

### Step 5: Start Development Environment
```bash
docker compose -f docker-compose.dev.yml up --build
```

**Expected output**:
```
[+] Building ...
[+] Running 2/2
 ✔ Container chart-backend-dev   Started
 ✔ Container chart-frontend-dev  Started
```

### Step 6: Wait for Services to Start
Look for these messages:
- Backend: `Application startup complete`
- Frontend: `VITE ready in ... ms`

### Step 7: Open Browser
Navigate to: http://localhost:5173

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"
**Solution**: Docker Desktop is not running
```bash
# Start Docker Desktop
open -a Docker

# Wait 30-60 seconds, then verify
docker info
```

### Issue: "OPENAI_API_KEY variable is not set"
**Solution**: Add your API key to `/backend/.env`
```bash
# Edit the file
nano backend/.env

# Add this line (replace with your key)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### Issue: "Port already in use"
**Solution**: Stop conflicting services
```bash
# Check what's using port 8000
lsof -ti:8000

# Kill the process (if it's the old backend)
lsof -ti:8000 | xargs kill -9

# Check port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Or stop your local dev servers if running
```

### Issue: Build errors or outdated cache
**Solution**: Clean rebuild
```bash
# Stop all containers
docker compose -f docker-compose.dev.yml down

# Remove all containers and volumes
docker compose -f docker-compose.dev.yml down -v

# Rebuild from scratch
docker compose -f docker-compose.dev.yml up --build --force-recreate
```

### Issue: Backend health check failing
**Solution**: Check logs for errors
```bash
# View backend logs
docker compose -f docker-compose.dev.yml logs backend

# Common issues:
# - Missing OPENAI_API_KEY
# - Python dependency errors
# - Port conflicts
```

## Useful Docker Commands

### View running containers
```bash
docker ps
```

### View all containers (including stopped)
```bash
docker ps -a
```

### View logs for specific service
```bash
# Development
docker compose -f docker-compose.dev.yml logs backend
docker compose -f docker-compose.dev.yml logs frontend

# Production
docker compose logs backend
docker compose logs frontend
```

### Follow logs in real-time
```bash
docker compose -f docker-compose.dev.yml logs -f
```

### Restart a specific service
```bash
docker compose -f docker-compose.dev.yml restart backend
```

### Stop all services
```bash
docker compose -f docker-compose.dev.yml down
```

### Remove all data (fresh start)
```bash
docker compose -f docker-compose.dev.yml down -v
```

### Access container shell
```bash
# Backend
docker exec -it chart-backend-dev sh

# Frontend
docker exec -it chart-frontend-dev sh
```

## What Each Service Does

### Backend Container (`chart-backend-dev`)
- Runs FastAPI server on port 8000
- Processes chat requests with OpenAI
- Generates charts with matplotlib
- Parses Excel files
- Serves chart images

### Frontend Container (`chart-frontend-dev`)
- Runs Vite dev server on port 5173
- Hot-reload for instant updates
- Proxies API requests to backend
- Serves React application

## Development Workflow

### Making Changes

**Frontend changes**:
1. Edit files in `/frontend/src/`
2. Changes auto-reload in browser (hot module replacement)
3. No restart needed

**Backend changes**:
1. Edit files in `/backend/app/`
2. FastAPI auto-reloads on file changes
3. No restart needed

### Viewing Changes
- Frontend: Instant in browser
- Backend: Check logs for reload confirmation

### Debugging
```bash
# View backend logs
docker compose -f docker-compose.dev.yml logs -f backend

# View frontend logs
docker compose -f docker-compose.dev.yml logs -f frontend

# Access backend shell for debugging
docker exec -it chart-backend-dev sh
python
>>> import app.agents.chart_agent as agent
>>> # Debug interactively
```

## Production Deployment

### For Production Use:
```bash
# Use the production compose file
docker compose up -d --build

# This will:
# - Build optimized frontend (minified JS/CSS)
# - Serve frontend with Nginx on port 80
# - Run backend with production settings
# - Set up health checks and auto-restart
```

### Scaling Services
```bash
# Run multiple backend instances
docker compose up -d --scale backend=3
```

## Clean Up

### Remove everything
```bash
# Stop and remove containers
docker compose -f docker-compose.dev.yml down

# Remove volumes too (clears data)
docker compose -f docker-compose.dev.yml down -v

# Remove images
docker rmi ai-agents-backend ai-agents-frontend

# Or nuclear option - remove all unused Docker resources
docker system prune -a
```

## Summary of Commands

### Quick Reference
| Action | Command |
|--------|---------|
| Start dev environment | `docker compose -f docker-compose.dev.yml up --build` |
| Start in background | `docker compose -f docker-compose.dev.yml up -d --build` |
| View logs | `docker compose -f docker-compose.dev.yml logs -f` |
| Stop services | `docker compose -f docker-compose.dev.yml down` |
| Restart service | `docker compose -f docker-compose.dev.yml restart backend` |
| Fresh start | `docker compose -f docker-compose.dev.yml down -v && docker compose -f docker-compose.dev.yml up --build` |

---

**Once Docker is running and your API key is set, simply run:**
```bash
docker compose -f docker-compose.dev.yml up --build
```

**Then open:** http://localhost:5173

🎉 You're ready to create AI-powered charts!
