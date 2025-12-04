# Setup Guide for AI Resume Generator

## Quick Start (5 minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Claude API Key

1. Go to https://console.anthropic.com/settings/keys
2. Sign up or log in
3. Click "Create Key"
4. Copy your API key

### 3. Configure API Key

**Option A: Using .env file (Recommended)**
```bash
cp .env.example .env
# Edit .env and add your API key
```

**Option B: Enter in the app**
- Start the app and enter your API key in the sidebar

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Guide

### Step 1: Create Your Master Profile

1. Click "Create New Profile" in the sidebar
2. Fill in your information:
   - **Personal Info**: Name, email, phone, location, LinkedIn, GitHub
   - **Education**: All your degrees and certifications
   - **Work Experience**: All your jobs (with detailed bullet points)
   - **Projects**: Your best projects with technologies used
   - **Skills**: Technical skills, languages, tools, soft skills
   - **Certifications & Awards**: Any certifications or awards

3. Save your profile with a memorable name

**Pro Tips:**
- Be comprehensive! Add ALL your experiences, even if they seem irrelevant
- Use action verbs and quantify achievements (e.g., "Increased performance by 50%")
- Add as many skills as you have - the AI will prioritize based on the job

### Step 2: Generate Tailored Resume

1. Go to the "Generate Resume" tab
2. Paste the job description you're applying for
3. Choose your preferred resume style
4. Click "Generate Resume"
5. Wait 10-30 seconds while AI analyzes and tailors your resume

**What the AI does:**
- Analyzes the job description for required skills and responsibilities
- Selects your most relevant experiences
- Rewrites bullet points to match the job requirements
- Prioritizes skills that match the job
- Generates a compelling summary tailored to the role

### Step 3: Export Your Resume

1. Go to "View & Export" tab
2. Review the tailored resume
3. Export in your preferred format:
   - **PDF** - Best for most applications
   - **DOCX** - For further editing
   - **TXT** - For plain text applications

## Tips for Best Results

### 1. Complete Profile
- The more information you provide, the better the AI can tailor your resume
- Include metrics and numbers whenever possible
- Use specific technologies and tools names

### 2. Good Job Descriptions
- Paste the complete job description, not just bullet points
- Include company information if available
- The more context, the better the match

### 3. Review & Edit
- Always review the generated resume before submitting
- The AI is smart but not perfect - you may want to tweak things
- Use the DOCX export if you need to make manual edits

### 4. Multiple Versions
- Generate different versions for different types of roles
- Keep your master profile updated with new experiences
- Save different profiles for different career paths (e.g., "frontend_dev", "fullstack_dev")

## Troubleshooting

### "Claude API key is required"
- Make sure you've entered a valid API key in the sidebar or .env file
- Check that your API key is active at https://console.anthropic.com/settings/keys

### "Error generating resume"
- Check your internet connection
- Verify you have Anthropic credits available
- Make sure your profile has at least name and one experience/education entry

### Generated resume looks wrong
- Check that your profile information is complete
- Try rephrasing your job descriptions to be more specific
- Make sure you're using the latest version of the dependencies

### Export not working
- Ensure the `output/` directory exists (it's created automatically)
- Check file permissions in the project directory
- Try a different export format

## API Costs

The AI Resume Generator uses Anthropic's Claude 3.5 Sonnet model:
- Cost: ~$0.30-0.60 per resume generation
- You need to have credits in your Anthropic account

**To minimize costs:**
- Generate resume only when you have a complete profile
- Review your profile before generating to avoid regenerations
- Claude 3.5 Sonnet provides excellent quality at reasonable cost

## Privacy & Security

- All data is stored locally on your computer
- API calls go directly to Anthropic (encrypted)
- No data is sent to any other third party
- Your profiles are stored in the `profiles/` folder
- Generated resumes are in the `output/` folder

## Advanced Usage

### Command Line (for developers)

```python
from profile_manager import ProfileManager
from resume_generator import ResumeGenerator
from export_handler import ResumeExporter

# Load profile
pm = ProfileManager()
profile = pm.load_profile("my_profile")

# Generate resume
generator = ResumeGenerator(api_key="your-api-key")
resume = generator.generate_tailored_resume(profile, job_description)

# Export
exporter = ResumeExporter()
pdf_path = exporter.export_to_pdf(resume)
```

### Customize Models

Edit `resume_generator.py` and change:
```python
self.model = "claude-3-5-sonnet-20241022"  # Default (best quality)
self.model = "claude-3-haiku-20240307"  # Faster and cheaper option
```

## Getting Help

- Check this guide first
- Review the README.md for project overview
- Verify all dependencies are installed
- Make sure Python 3.8+ is installed

## What's Next?

- Create your master profile with all your information
- Test it with a real job description
- Iterate and improve your profile based on results
- Keep your profile updated as you gain new experiences

Good luck with your job search! 🚀
