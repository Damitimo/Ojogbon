# Deployment Guide for Ojogbon (AI Resume Generator)

## Overview
This guide will help you deploy both the frontend (Vercel) and backend (Railway) for production use.

---

## 🚀 Step 1: Deploy Backend to Railway

### 1.1 Prepare Backend
The backend is already configured and ready. All files are in the `backend/` directory.

### 1.2 Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up / Log in** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Select this repository**
6. **Configure:**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

7. **Add Environment Variables** (if needed):
   - Railway will auto-detect Python and set PORT
   - No additional env vars needed for now

8. **Deploy!**
9. **Copy your Railway URL** (e.g., `https://your-app.railway.app`)

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Prepare Frontend

1. **Create `.env.local` file** in the `frontend/` directory:
   ```bash
   cd frontend
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local`** and add your Railway backend URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

### 2.2 Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy? **Yes**
   - Which scope? Select your account
   - Link to existing project? **No**
   - Project name? `ojogbon` (or your choice)
   - Directory? **./frontend** (if not already in frontend dir, use `.`)
   - Override settings? **No**

5. **Set Environment Variable:**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   ```
   - When prompted, paste your Railway URL: `https://your-app.railway.app`
   - Select: **Production, Preview, Development**

6. **Deploy to production:**
   ```bash
   vercel --prod
   ```

#### Option B: Using Vercel Dashboard

1. **Go to [Vercel.com](https://vercel.com)**
2. **Click "Add New Project"**
3. **Import your Git repository**
4. **Configure:**
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)

5. **Add Environment Variable:**
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-app.railway.app` (your Railway URL)

6. **Click "Deploy"**

---

## ✅ Step 3: Verify Deployment

### 3.1 Test Backend
Visit your Railway URL:
```
https://your-app.railway.app/api/profiles
```
You should see a JSON response with your profiles.

### 3.2 Test Frontend
1. Visit your Vercel URL (e.g., `https://ojogbon.vercel.app`)
2. Check that the profile dropdown loads your profiles
3. Try generating a resume to ensure backend connection works

---

## 🔧 Post-Deployment Configuration

### Update CORS (if needed)
If you encounter CORS issues, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ojogbon.vercel.app",  # Add your Vercel URL
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend on Railway.

---

## 📁 File Structure for Deployment

```
internship-ai/
├── frontend/               # Deploy to Vercel
│   ├── .env.local         # Local environment variables (not committed)
│   ├── .env.local.example # Template for env vars
│   ├── vercel.json        # Vercel configuration
│   └── ...
│
├── backend/               # Deploy to Railway
│   ├── main.py           # FastAPI app
│   ├── requirements.txt  # Python dependencies
│   ├── profiles/         # User profiles (persisted in Railway volume)
│   └── ...
│
└── DEPLOYMENT.md         # This file
```

---

## 🔐 Security Notes

1. **API Key Storage**: API keys are stored in `backend/.api_config.json` - make sure Railway persists this file
2. **Profile Data**: User profiles in `backend/profiles/` should be persisted using Railway volumes
3. **Environment Variables**: Never commit `.env.local` or `.api_config.json` to git

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` environment variable in Vercel
- Verify Railway backend is running
- Check CORS settings in `backend/main.py`

### Profiles not loading
- Check Railway logs for errors
- Verify `profiles/` directory exists in Railway
- Check Railway persistent storage is configured

### Build fails on Vercel
- Check Node version compatibility
- Run `npm run build` locally first to test
- Check Vercel build logs for specific errors

---

## 📊 Monitoring

### Railway Dashboard
- View backend logs
- Monitor memory/CPU usage
- Check deployment status

### Vercel Dashboard
- View frontend deployment logs
- Monitor function execution
- Check analytics

---

## 🔄 Redeployment

### Update Frontend
```bash
cd frontend
vercel --prod
```

### Update Backend
Railway auto-deploys on git push (if connected to GitHub)

---

## 💰 Cost Estimates

### Vercel (Frontend)
- **Hobby Plan**: Free
  - Unlimited deployments
  - 100 GB bandwidth/month
  - Serverless functions

### Railway (Backend)
- **Starter Plan**: $5/month
  - 500 execution hours
  - 8 GB RAM
  - Shared CPU

**Total**: ~$5/month for full deployment

---

## 🎉 You're Done!

Your AI Resume Generator (Ojogbon) is now live!

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app

Share it with the world! 🚀
