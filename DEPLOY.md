# Railway Deployment Guide

## Quick Deploy

### 1. Push to GitHub
```bash
# Initialize git if not done
cd C:\Users\gandh\Desktop\opencode_Jobsy
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/jopsy.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add these Environment Variables:

```
# Database (Supabase)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Twilio WhatsApp (REQUIRED)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238888

# Ollama (for AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=kimi-k2.5:cloud

# App Settings
APP_NAME="Jobsy"
DEBUG=false
MAX_APPLICATIONS_PER_DAY=20
```

5. Click **Deploy**

---

## Twilio Setup

1. Create a Twilio account at https://twilio.com
2. Get your Account SID and Auth Token from console
3. Enable WhatsApp in Twilio (Sandbox mode is free)
4. Set webhook URL to: `https://your-app.railway.app/webhook/twilio`

---

## WhatsApp Commands (After Deploy)

Once deployed, users can message Jobsy on WhatsApp:

- `jobs` - Get job recommendations
- `apply` - Apply to a job
- `status` - Check applications
- `help` - See all commands

---

## Alternative: Direct Docker Deploy

```bash
# Build
docker build -t jobsys .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL="your_db_url" \
  -e WHATSAPP_PHONE_NUMBER_ID="your_id" \
  -e WHATSAPP_ACCESS_TOKEN="your_token" \
  jobsys
```

---

## Getting Public URL for WhatsApp Webhook

### Option 1: ngrok (Free)
```bash
# Install ngrok
winget install ngrok

# Run
ngrok http 8000

# Use the generated URL for WhatsApp webhook
```

### Option 2: Cloudflare Tunnel (Free)
```bash
# Install
winget install cloudflare/cloudflared

# Run
cloudflared tunnel --url http://localhost:8000
```

---

## After Deploy

1. Set WhatsApp webhook URL to: `https://your-app.railway.app/webhook/whatsapp`
2. Test with: `https://your-app.railway.app/health`
3. Access API docs: `https://your-app.railway.app/docs`