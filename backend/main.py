"""
FastAPI Backend for AI Resume Generator
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from pathlib import Path

from profile_manager import ProfileManager, UserProfile
from resume_generator import ResumeGenerator
from export_handler import ResumeExporter

# Initialize FastAPI app
app = FastAPI(title="AI Resume Generator API", version="1.0.0")

# Configure CORS - Allow all localhost origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
profile_manager = ProfileManager()
exporter = ResumeExporter()

# API Key storage path
CONFIG_FILE = Path(".api_config.json")


# Pydantic models for API
class APIKeyRequest(BaseModel):
    api_key: str


class ResumeGenerateRequest(BaseModel):
    profile_name: str
    job_description: str
    extra_knowledge: Optional[str] = ""
    experience_bullet_counts: Optional[Dict[int, int]] = {}


class ProfileSaveRequest(BaseModel):
    profile_name: str
    profile: dict


# Helper functions
def load_api_key() -> Optional[str]:
    """Load API key from config file"""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get('api_key')
    except:
        return None


def save_api_key(api_key: str) -> bool:
    """Save API key to config file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'api_key': api_key}, f)
        return True
    except:
        return False


# API Routes

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Resume Generator API is running"}


@app.get("/api/profiles")
def list_profiles():
    """List all available profiles"""
    try:
        profiles = profile_manager.list_profiles()
        return {"profiles": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profiles/{profile_name}")
def get_profile(profile_name: str):
    """Get a specific profile"""
    try:
        profile = profile_manager.load_profile(profile_name)
        return {"profile": profile.model_dump()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profiles")
def create_profile(request: ProfileSaveRequest):
    """Create or update a profile"""
    try:
        profile = UserProfile(**request.profile)
        path, clean_name = profile_manager.create_profile(request.profile_name, profile, replace=True)
        return {"message": "Profile saved successfully", "profile_name": clean_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/profiles/{profile_name}")
def delete_profile(profile_name: str):
    """Delete a profile"""
    try:
        success = profile_manager.delete_profile(profile_name)
        if success:
            return {"message": f"Profile '{profile_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Profile '{profile_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/api-key")
def set_api_key(request: APIKeyRequest):
    """Save Claude API key"""
    try:
        success = save_api_key(request.api_key)
        if success:
            return {"message": "API key saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save API key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/api-key/status")
def check_api_key():
    """Check if API key is configured"""
    api_key = load_api_key()
    if api_key:
        # Return masked version (show last 4 characters)
        masked = "sk-ant-..." + api_key[-4:]
        return {"configured": True, "masked_key": masked}
    return {"configured": False, "masked_key": None}


@app.post("/api/generate-resume")
def generate_resume(request: ResumeGenerateRequest):
    """Generate a tailored resume"""
    try:
        # Load API key
        api_key = load_api_key()
        if not api_key:
            raise HTTPException(status_code=400, detail="API key not configured")
        
        # Load profile
        profile = profile_manager.load_profile(request.profile_name)
        
        # Initialize generator
        generator = ResumeGenerator(api_key=api_key)
        
        # Generate resume
        tailored_resume = generator.generate_tailored_resume(
            profile=profile,
            job_description=request.job_description,
            extra_knowledge=request.extra_knowledge,
            experience_bullet_counts=request.experience_bullet_counts
        )
        
        return {"resume": tailored_resume}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Profile '{request.profile_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/docx")
async def export_docx(resume_data: dict):
    """Export resume as DOCX"""
    try:
        # Export returns the full path to the created file
        output_path = exporter.export_to_docx(resume_data, "resume.docx")
        
        return FileResponse(
            path=str(output_path),
            filename="resume.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf")
async def export_pdf(resume_data: dict):
    """Export resume as PDF"""
    try:
        # Export returns the full path to the created file
        output_path = exporter.export_to_pdf(resume_data, "resume.pdf")
        
        return FileResponse(
            path=output_path,
            filename="resume.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
