# AI Resume Generator - React Migration

## ✅ YOUR PROFILE DATA IS SAFE!

Your profile "Tech Profile" has been backed up to:
- `profiles_backup/Tech Profile.json`
- Original in `backend/profiles/Tech Profile.json`

## Project Structure

```
internship-ai/
├── backend/          # FastAPI Python backend
│   ├── main.py       # API endpoints
│   ├── profile_manager.py
│   ├── resume_generator.py
│   ├── export_handler.py
│   ├── profiles/     # YOUR PROFILE DATA IS HERE
│   └── requirements.txt
│
├── frontend/         # Next.js React frontend
│   ├── src/
│   │   ├── app/      # Next.js pages
│   │   ├── components/
│   │   └── lib/
│   └── package.json
│
└── profiles_backup/  # BACKUP OF YOUR PROFILE DATA
```

## Setup Instructions

### Backend Setup (5 minutes)

1. Open a terminal and navigate to the backend:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python main.py
```

The backend API will run at `http://localhost:8000`

### Frontend Setup (5 minutes)

1. Open a NEW terminal and navigate to the frontend:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run at `http://localhost:3000`

## Quick Start Script

Instead of manual setup, run this command from the project root:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

## What's Different?

### Before (Streamlit):
- Single Python app
- Profile preloaded automatically
- All-in-one interface

### After (React + FastAPI):
- **Frontend**: Modern React UI with Tailwind CSS
- **Backend**: FastAPI handles AI generation and data
- **Your Profile**: Still saved in the same location!
- **Multi-User**: Better profile management
- **Faster**: More responsive UI

## Your Profile Data

Your profile "Tech Profile" contains:
- Name: Timothy Ojo
- Email: toojo@marshall.usc.edu
- 4 work experiences (RBC Insurance, Guusto, Alphafox Media, OAU)
- 2 education entries (USC MBA, OAU B.Pharm)
- 2 projects (VectorGurus, RBC Edgenet)

**All of this data is preserved and will work in the new system!**

## Next Steps

1. Follow the setup instructions above
2. Open `http://localhost:3000` in your browser
3. Select "Tech Profile" from the dropdown
4. Start generating resumes!

## Deployment (Later)

When ready to deploy:
- **Frontend**: Deploy to Vercel (free)
- **Backend**: Deploy to Railway (free $5/month credit)

## Need Help?

- Backend API docs: `http://localhost:8000/docs`
- Check backend logs in the terminal where you ran `python main.py`
- Check frontend logs in the terminal where you ran `npm run dev`
