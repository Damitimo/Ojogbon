"""
Profile Manager - Handles user profile creation and management
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """Education entry"""
    degree: str
    institution: str
    location: str = ""
    start_date: str
    end_date: str
    gpa: Optional[str] = None
    relevant_coursework: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    """Work experience entry"""
    title: str
    company: str
    location: str = ""
    start_date: str
    end_date: str
    description: List[str]
    skills_used: List[str] = Field(default_factory=list)


class Project(BaseModel):
    """Project entry"""
    name: str
    description: str
    technologies: List[str]
    achievements: List[str]
    url: Optional[str] = None


class UserProfile(BaseModel):
    """Complete user profile with all information"""
    personal_info: Dict[str, str] = Field(
        default_factory=lambda: {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "portfolio": "",
            "location": ""
        }
    )
    summary: str = ""
    my_story: str = ""
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "technical": [],
            "languages": [],
            "tools": [],
            "soft_skills": []
        }
    )
    certifications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)


class ProfileManager:
    """Manages user profiles - create, read, update, delete"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
    
    def create_profile(self, profile_name: str, profile: UserProfile, replace: bool = False) -> tuple[Path, str]:
        """Save a user profile to disk"""
        # Clean profile name - remove extra spaces and special characters
        clean_name = profile_name.strip()
        clean_name = ' '.join(clean_name.split())  # Remove multiple spaces
        clean_name = clean_name.replace('.', '')   # Remove dots
        
        # Check if profile exists
        profile_path = self.profiles_dir / f"{clean_name}.json"
        
        if profile_path.exists() and not replace:
            # Auto-version: find next available version
            version = 2
            while True:
                versioned_name = f"{clean_name}_v{version}"
                versioned_path = self.profiles_dir / f"{versioned_name}.json"
                if not versioned_path.exists():
                    clean_name = versioned_name
                    profile_path = versioned_path
                    break
                version += 1
        
        with open(profile_path, 'w') as f:
            json.dump(profile.model_dump(), f, indent=2)
        return profile_path, clean_name
    
    def load_profile(self, profile_name: str) -> UserProfile:
        """Load a user profile from disk"""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        with open(profile_path, 'r') as f:
            data = json.load(f)
        
        # Migrate old education format (graduation_date -> start_date/end_date)
        if 'education' in data:
            for edu in data['education']:
                # If old format with graduation_date, convert to start_date/end_date
                if 'graduation_date' in edu and 'start_date' not in edu:
                    grad_date = edu['graduation_date']
                    # Estimate start date (4 years before graduation)
                    if grad_date and len(grad_date.split()) == 2:
                        month, year = grad_date.split()
                        try:
                            year_int = int(year)
                            start_year = year_int - 4
                            edu['start_date'] = f"{month} {start_year}"
                            edu['end_date'] = grad_date
                            # Remove old field
                            del edu['graduation_date']
                        except:
                            # Fallback if parsing fails
                            edu['start_date'] = "Sep 2020"
                            edu['end_date'] = grad_date
                            del edu['graduation_date']
        
        return UserProfile(**data)
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        return [p.stem for p in self.profiles_dir.glob("*.json")]
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        if profile_path.exists():
            profile_path.unlink()
            return True
        return False
    
    def create_default_profile(self) -> UserProfile:
        """Create a default empty profile"""
        return UserProfile()
