"""
Resume Generator - Core AI engine for generating tailored resumes
"""
import os
import json
import re
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from profile_manager import UserProfile

# Load environment variables
load_dotenv()


def extract_json_from_text(text: str) -> Dict:
    """Extract JSON from text that might have markdown or other content"""
    # Try to parse as-is first
    try:
        return json.loads(text)
    except:
        pass
    
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass
    
    # Try to find raw JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    # If all fails, raise error with the actual response
    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")


def truncate_bullets_to_25_words(bullets: List[str]) -> List[str]:
    """Truncate each bullet to a maximum of 25 words"""
    truncated = []
    for bullet in bullets:
        words = bullet.split()
        if len(words) > 25:
            # Truncate to 25 words and add ellipsis
            truncated_bullet = ' '.join(words[:25]) + '...'
            truncated.append(truncated_bullet)
        else:
            truncated.append(bullet)
    return truncated


class ResumeGenerator:
    """AI-powered resume generator that tailors resumes to job descriptions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the resume generator with Claude API key"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required. Set ANTHROPIC_API_KEY in .env file or pass it directly.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"  # Using Claude Sonnet 4.5 (latest model)
    
    def generate_tailored_resume(
        self, 
        profile: UserProfile, 
        job_description: str,
        style: str = "professional",
        extra_knowledge: str = None,
        experience_bullet_counts: Dict[int, int] = None
    ) -> Dict[str, any]:
        """
        Generate a tailored resume based on the job description
        
        Args:
            profile: User's complete profile (required)
            job_description: Job description text
            style: Resume style (professional, creative, minimal)
            extra_knowledge: Additional context information
            experience_bullet_counts: Dict mapping experience index to desired bullet count
        
        Returns:
            Dict containing tailored resume sections
        """
        # Analyze the job description first
        jd_analysis = self._analyze_job_description(job_description)
        
        # Always tailor existing profile to JD (profile is now required)
        # Generate tailored summary
        tailored_summary = self._generate_summary(profile, jd_analysis)
        
        # Select and tailor experiences
        tailored_experiences = self._tailor_experiences(profile, jd_analysis, extra_knowledge, experience_bullet_counts)
        
        # Select and tailor projects
        tailored_projects = self._tailor_projects(profile, jd_analysis, extra_knowledge)
        
        # Generate tailored skills
        tailored_skills = self._generate_skills(profile, jd_analysis)
        
        return {
            "personal_info": profile.personal_info,
            "summary": tailored_summary,
            "experience": tailored_experiences,
            "projects": tailored_projects,
            "education": [edu.model_dump() for edu in profile.education],
            "skills": tailored_skills,
            "certifications": profile.certifications,
            "awards": profile.awards,
            "jd_analysis": jd_analysis
        }
    
    def generate_story_content(
        self,
        profile: UserProfile,
        job_description: str,
        include_why: bool = False,
        include_cover_letter: bool = False,
        extra_knowledge: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate narrative content (why statement / cover letter) leveraging user's story"""
        if not include_why and not include_cover_letter:
            return {}

        if not profile.my_story or not profile.my_story.strip():
            raise ValueError("Please add content to 'My Story' in your profile before generating story-based responses.")

        if not job_description or not job_description.strip():
            raise ValueError("A job description is required to tailor story-based responses.")

        story_context = profile.my_story.strip()
        summary_context = profile.summary.strip() if profile.summary else ""

        experience_summaries = []
        for exp in profile.experience[:4]:
            bullet_preview = " ".join(exp.description[:2]) if exp.description else "No detailed responsibilities provided"
            experience_summaries.append(
                f"{exp.title} at {exp.company} ({exp.start_date} - {exp.end_date}): {bullet_preview}"
            )
        experience_context = "\n".join(experience_summaries) if experience_summaries else "No experience entries provided."

        outputs_requested = []
        if include_why:
            outputs_requested.append(
                "1. WHY_RESPONSE: A 3-paragraph narrative explaining why the candidate wants to work at the company, directly tying motivations from 'My Story' to the specific job description. Each paragraph should be 3-5 sentences, separated by blank lines."
            )
        if include_cover_letter:
            outputs_requested.append(
                "2. COVER_LETTER: A full professional cover letter (4-5 paragraphs) tailored to the job description. Follow standard cover letter structure (introduction, value proposition, evidence, cultural fit, closing) and ensure tone is authentic to the story."
            )

        prompt = f"""You are an expert career storyteller crafting personalised narratives that feel authentic and compelling.

CANDIDATE STORY (primary source material):
{story_context}

ADDITIONAL CONTEXT:
- Professional Summary (if provided): {summary_context or 'No summary provided'}
- Experience Highlights:
{experience_context}
- Extra Knowledge: {extra_knowledge or 'None provided'}

TARGET JOB DESCRIPTION:
{job_description}

OUTPUT REQUIREMENTS:
{chr(10).join(outputs_requested)}

STRICT RULES:
- Root every paragraph in the candidate's story, motivations, and authentic experiences.
- Reference relevant elements from the job description (mission, responsibilities, skills) to show alignment.
- Use confident, professional tone without exaggeration or buzzwords.
- Ensure paragraphs are separated by a blank line for readability.
- Return ONLY valid JSON with keys for the requested outputs. Omit keys that were not requested.

Return JSON like:
{{"why_you_want_to_work_here": "...", "cover_letter": "..."}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1100,
            temperature=0.7,
            system="You are an expert career storyteller who writes authentic, tailored narratives. Always respond with valid JSON only.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result = extract_json_from_text(response.content[0].text)

        filtered: Dict[str, str] = {}
        if include_why and result.get("why_you_want_to_work_here"):
            filtered["why_you_want_to_work_here"] = result["why_you_want_to_work_here"].strip()
        if include_cover_letter and result.get("cover_letter"):
            filtered["cover_letter"] = result["cover_letter"].strip()

        return filtered

    def _analyze_job_description(self, job_description: str) -> Dict[str, any]:
        """Analyze job description to extract key requirements"""
        prompt = f"""Analyze this job description and extract:
1. Key technical skills required
2. Soft skills required
3. Years of experience needed
4. Main responsibilities
5. Nice-to-have skills
6. Company culture keywords

Job Description:
{job_description}

Provide the analysis in JSON format with these keys:
{{
    "required_skills": [],
    "soft_skills": [],
    "experience_years": "",
    "responsibilities": [],
    "nice_to_have": [],
    "culture_keywords": []
}}

Return ONLY the JSON object, no additional text."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            system="You are an expert resume consultant who analyzes job descriptions. Always respond with valid JSON only.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return extract_json_from_text(response.content[0].text)
    
    def _generate_summary(self, profile: UserProfile, jd_analysis: Dict) -> str:
        """Generate a tailored professional summary"""
        prompt = f"""Create a compelling professional summary (2-3 sentences) for a resume.

User's Background:
- Current Experience: {profile.experience[0].title if profile.experience else "Entry Level"}
- Skills: {', '.join(profile.skills.get('technical', [])[:10])}
- Education: {profile.education[0].degree if profile.education else ""}

Job Requirements:
- Required Skills: {', '.join(jd_analysis.get('required_skills', [])[:10])}
- Responsibilities: {', '.join(jd_analysis.get('responsibilities', [])[:5])}
- Culture Keywords: {', '.join(jd_analysis.get('culture_keywords', []))}

Create a summary that:
1. Highlights relevant experience and skills matching the job
2. Uses keywords from the job description naturally
3. Demonstrates value proposition
4. Is concise and impactful

Return ONLY the summary text, nothing else.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,  # Increased for better reasoning
            temperature=0.6,  # Lower for more grounded outputs
            system="You are an expert resume writer with strong analytical skills. Think carefully about the candidate's ACTUAL background before creating a summary. Ground the summary in their real experience and skills. Don't over-tailor or fabricate capabilities.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text.strip()
    
    def _tailor_experiences(self, profile: UserProfile, jd_analysis: Dict, extra_knowledge: str = None, experience_bullet_counts: Dict[int, int] = None) -> List[Dict]:
        """Select and tailor work experiences to match the job"""
        if not profile.experience:
            return []
        
        tailored = []
        
        for i, exp in enumerate(profile.experience):
            # Get the desired bullet count for this experience (default to 4)
            desired_bullets = experience_bullet_counts.get(i, 4) if experience_bullet_counts else 4
            
            # Check if we need to generate skills from JD
            has_skills = exp.skills_used and len(exp.skills_used) > 0

            existing_bullets = exp.description or []
            existing_bullets_text = "\n".join(f"- {bullet}" for bullet in existing_bullets) if existing_bullets else "- No existing responsibilities provided"
            existing_verbs = []
            for bullet in existing_bullets:
                cleaned = bullet.lstrip("•- ").strip()
                first_word = cleaned.split(" ")[0] if cleaned else ""
                first_word = first_word.strip(",.;:").capitalize()
                if first_word and first_word not in existing_verbs:
                    existing_verbs.append(first_word)
            existing_verbs_text = ", ".join(existing_verbs) if existing_verbs else "None provided"
            
            if has_skills:
                # User provided skills, just generate responsibilities
                prompt = f"""You are generating resume bullets. Think step-by-step and reason carefully.

STEP 1: ANALYZE THE CONTEXT
Current Role: {exp.title} at {exp.company}
Work Period: {exp.start_date} - {exp.end_date}
Skills Used: {', '.join(exp.skills_used)}

Existing Responsibilities (your SOURCE OF TRUTH - these are REAL activities):
{existing_bullets_text}

Action verbs already used: {existing_verbs_text}

Target Role: {jd_analysis.get('experience_years', 'Entry-level')} position
Target Requirements:
- Core Skills: {', '.join(jd_analysis.get('required_skills', []))}
- Responsibilities: {', '.join(jd_analysis.get('responsibilities', []))}
- Soft Skills: {', '.join(jd_analysis.get('soft_skills', []))}

Extra Context:
{f"- {extra_knowledge}" if extra_knowledge else "- No additional context provided"}

STEP 2: REASON ABOUT WHAT MAKES SENSE
Before writing bullets, think through:
1. What industry is {exp.company} in? (insurance, SaaS, healthcare, pharmacy, etc.)
2. What would a {exp.title} ACTUALLY do in that industry?
3. What are the REAL transferable skills from this role?
4. Which existing bullets show relevant capabilities?
5. How can I reframe WITHOUT fabricating or misrepresenting?

STEP 3: GROUNDING CHECK
- Only use facts from the existing bullets
- Keep industry context authentic
- Don't insert keywords from target role that don't fit the actual work
- Don't claim work on projects/systems that don't match the company

STEP 4: CREATE BULLETS
Now create {desired_bullets} bullet points that:
- **NO VERB REPETITION** - Each bullet starts with a DIFFERENT action verb
- Are factually grounded in the existing responsibilities
- Highlight transferable skills authentically
- Use industry-appropriate terminology for {exp.company}
- Maximum 25 words each
- Show operational capabilities without misrepresenting

Return as JSON:
{{"bullets": ["bullet 1", "bullet 2", ...]}}

Return ONLY the JSON object, no additional text."""
            else:
                # Generate both skills and responsibilities from JD
                prompt = f"""You are generating resume content. Think step-by-step and reason carefully.

STEP 1: ANALYZE THE CONTEXT
Current Role: {exp.title} at {exp.company}
Work Period: {exp.start_date} - {exp.end_date}

Existing Responsibilities (your SOURCE OF TRUTH):
{existing_bullets_text}

Action verbs already used: {existing_verbs_text}

Target Role: {jd_analysis.get('experience_years', 'Entry-level')} position
Target Requirements:
- Core Skills: {', '.join(jd_analysis.get('required_skills', []))}
- Responsibilities: {', '.join(jd_analysis.get('responsibilities', []))}
- Soft Skills: {', '.join(jd_analysis.get('soft_skills', []))}

Extra Context:
{f"- {extra_knowledge}" if extra_knowledge else "- No additional context provided"}

STEP 2: REASON ABOUT WHAT MAKES SENSE
Before creating content, think through:
1. What industry is {exp.company} actually in?
2. What would a {exp.title} REALISTICALLY do at this company?
3. What skills would this person ACTUALLY have?
4. What are authentic transferable capabilities from this role?
5. What tools/processes are REALISTIC for this industry?

STEP 3: INDUSTRY AUTHENTICITY CHECK
- Insurance company → policies, regulations, underwriting, claims, risk assessment
- SaaS company → product development, user engagement, feature launches, subscriptions
- Healthcare → patient systems, clinical workflows, compliance, medical records
- Pharmacy → medication management, clinical processes, regulatory compliance
- DO NOT mix industries or insert inappropriate terminology

STEP 4: CREATE CONTENT
Now create:
1. 5-8 skills authentic to {exp.title} at {exp.company} AND transferable to target role
2. {desired_bullets} bullet points that:
   - **NO VERB REPETITION** - Each bullet starts with a DIFFERENT action verb
   - Are factually grounded and realistic
   - Show transferable capabilities authentically
   - Use appropriate terminology for the actual industry
   - Maximum 25 words each

Return as JSON:
{{"skills": ["skill1", "skill2", ...], "bullets": ["bullet 1", "bullet 2", ...]}}

Return ONLY the JSON object, no additional text."""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,  # Increased for extended reasoning
                temperature=0.6,  # Slightly lower for more grounded outputs
                system="You are an expert resume writer with strong analytical skills. Your job is to THINK STEP-BY-STEP before creating content. CRITICAL RULES:\n1. REASON about what makes sense for the actual role and company\n2. Ground ALL content in reality - no fabrication\n3. Each bullet MUST start with a DIFFERENT action verb (NO repetition)\n4. Keep industry context authentic - don't insert inappropriate keywords\n5. Highlight real transferable skills without misrepresenting work\n6. If something doesn't make sense for the role/company, DON'T include it\nAlways respond with valid JSON only.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = extract_json_from_text(response.content[0].text)
            
            # Apply 25-word limit to bullets
            if "bullets" in result:
                result["bullets"] = truncate_bullets_to_25_words(result["bullets"])
            
            tailored.append({
                "title": exp.title,
                "company": exp.company,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": result.get("bullets", exp.description),
                "skills_used": result.get("skills", exp.skills_used) if not has_skills else exp.skills_used
            })
        
        return tailored
    
    def _tailor_projects(self, profile: UserProfile, jd_analysis: Dict, extra_knowledge: str = None) -> List[Dict]:
        """Select and tailor projects to match the job"""
        if not profile.projects:
            return []
        
        tailored_projects = []
        
        # Take top 3 projects
        for project in profile.projects[:3]:
            needs_generation = (
                not project.technologies or 
                len(project.technologies) == 0 or 
                project.description in ["Project details to be generated", ""]
            )
            
            if needs_generation:
                # Generate project details from JD
                prompt = f"""You are generating project details. Think step-by-step and reason carefully.

STEP 1: UNDERSTAND THE PROJECT
Project Name: {project.name}
Existing Description: {project.description if project.description else "None provided"}

Target Job Requirements:
- Required Skills: {', '.join(jd_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(jd_analysis.get('responsibilities', []))}

Extra Context:
{f"- {extra_knowledge}" if extra_knowledge else "- No additional context provided"}

STEP 2: REASON ABOUT WHAT MAKES SENSE
Before creating details, think through:
1. Based on the project NAME, what would this project ACTUALLY be about?
2. What technologies would REALISTICALLY be used for this type of project?
3. What achievements would be AUTHENTIC for this project scope?
4. Does the project align with the user's background?
5. Am I being realistic or over-tailoring?

STEP 3: GROUNDING CHECK
- Don't fabricate a completely different project just to match keywords
- Keep technologies realistic for the project type
- Don't claim involvement in systems/platforms that don't match the project name
- Achievements should be proportional to project scope

STEP 4: CREATE PROJECT CONTENT
Now create:
1. A brief, compelling description (2-3 sentences) that fits the project name
2. 4-6 technologies that are REALISTIC for this project type
3. 2-3 achievements that are AUTHENTIC and proportional
- Maximum 25 words per achievement

Return as JSON:
{{"description": "description text", "technologies": ["tech1", "tech2", ...], "achievements": ["achievement 1", "achievement 2", ...]}}

Return ONLY the JSON object, no additional text."""
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,  # Increased for extended reasoning
                    temperature=0.6,  # Lower for more grounded outputs
                    system="You are an expert resume writer with strong analytical skills. Your job is to THINK STEP-BY-STEP before creating project content. CRITICAL RULES:\n1. REASON about what the project ACTUALLY is based on its name\n2. Don't fabricate completely different projects just to match keywords\n3. Keep technologies and achievements REALISTIC for the project scope\n4. Stay grounded in reality - no over-tailoring\n5. If details don't make sense for the project, don't force them\nAlways respond with valid JSON only.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                result = extract_json_from_text(response.content[0].text)
                
                # Apply 25-word limit to achievements
                if "achievements" in result:
                    result["achievements"] = truncate_bullets_to_25_words(result["achievements"])
                
                tailored_projects.append({
                    "name": project.name,
                    "description": result.get("description", project.description),
                    "technologies": result.get("technologies", project.technologies),
                    "achievements": result.get("achievements", project.achievements),
                    "url": project.url
                })
            else:
                # Just use existing project data, but apply word limit to achievements
                project_data = project.model_dump()
                if "achievements" in project_data and project_data["achievements"]:
                    project_data["achievements"] = truncate_bullets_to_25_words(project_data["achievements"])
                tailored_projects.append(project_data)
        
        return tailored_projects
    
    def _generate_skills(self, profile: UserProfile, jd_analysis: Dict) -> Dict[str, List[str]]:
        """Generate tailored skills based on job requirements using AI"""
        prompt = f"""Generate a comprehensive skills section for a resume based on the target job description.

Job Description Analysis:
- Required Technical Skills: {', '.join(jd_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(jd_analysis.get('responsibilities', []))}
- Industry Keywords: {', '.join(jd_analysis.get('culture_keywords', []))}

User's Existing Skills (if any):
- Technical: {', '.join(profile.skills.get('technical', []))}
- Languages: {', '.join(profile.skills.get('languages', []))}
- Tools: {', '.join(profile.skills.get('tools', []))}
- Soft Skills: {', '.join(profile.skills.get('soft_skills', []))}

Create 3 categories of skills that would be most relevant for this job:

1. **Technical Skills**: 9 specific technical skills that match the job requirements. Include both required skills from the JD and complementary skills that demonstrate expertise.

2. **Languages & Frameworks**: 9 programming languages, frameworks, and technologies relevant to the role.

3. **Tools & Platforms**: 9 tools, platforms, and software that would be valuable for this position.

IMPORTANT:
- Focus on skills that directly match the job description
- Include both hard requirements and nice-to-have skills
- Use industry-standard terminology
- Prioritize skills mentioned or implied in the job description
- Include complementary skills that show breadth of knowledge
- Each category should have exactly 9 skills

Return as JSON:
{{
    "technical": ["skill1", "skill2", "skill3", ...],
    "languages": ["language1", "language2", "language3", ...],
    "tools": ["tool1", "tool2", "tool3", ...]
}}

Return ONLY the JSON object, no additional text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            system="You are an expert career counselor who creates compelling skills sections for resumes. Always respond with valid JSON only.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result = extract_json_from_text(response.content[0].text)
        
        # Ensure we have the expected structure
        return {
            "technical": result.get("technical", []),
            "languages": result.get("languages", []),
            "tools": result.get("tools", [])
        }


if __name__ == "__main__":
    # Example usage
    print("Resume Generator initialized. Use through app.py or import in your code.")
