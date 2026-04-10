# Jobsy - WhatsApp Job Automation Platform

A WhatsApp-native job search assistant that finds, optimizes, and applies to jobs automatically.

## Features

- ✅ WhatsApp-native job search (via Twilio)
- ✅ AI-powered conversation (Ollama + Kimi K2.5)
- ✅ ATS-optimized resume generation (career-ops style)
- ✅ Auto-apply with Playwright
- ✅ Job evaluation (A-F system from career-ops)
- ✅ Interview prep with STAR stories
- ✅ Salary intelligence
- ✅ Application tracking
- ✅ Voice mock interviews with AI feedback
- ✅ LinkedIn recruiter outreach
- ✅ Dashboard UI

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Server runs at: http://localhost:8000
Dashboard at: http://localhost:5173

## Deployment

### Railway (Recommended)

1. Push code to GitHub
2. Connect to Railway.app
3. Add environment variables
4. Deploy

See [DEPLOY.md](./DEPLOY.md) for detailed instructions.

### Docker

```bash
docker build -t jobsys .
docker run -p 8000:8000 jobsys
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **AI**: Ollama + Kimi K2.5
- **Database**: PostgreSQL (Supabase)
- **WhatsApp**: Twilio
- **Automation**: Playwright

## License

MIT