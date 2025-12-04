# AI Resume Generator 🤖

An intelligent resume generator that creates customized resumes tailored to specific job descriptions using AI.

## Features

- 📝 **AI-Powered Customization**: Uses Anthropic's Claude AI to tailor your resume to any job description
- 🎯 **Smart Matching**: Highlights relevant skills and experiences that match the JD
- 📄 **Multiple Export Formats**: Generate resumes in PDF, DOCX, or plain text
- 💾 **Profile Management**: Save your master profile with all experiences, skills, and achievements
- 🎨 **Clean Web Interface**: Easy-to-use Streamlit interface
- ⚡ **Fast Generation**: Get a tailored resume in seconds

## How It Works

1. **Create Your Master Profile**: Input all your work experience, education, skills, and achievements
2. **Paste Job Description**: Copy the JD you want to apply for
3. **AI Magic**: The AI analyzes the JD and selects/rephrases your experiences to match
4. **Download**: Get your tailored resume in your preferred format

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Claude API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```

### Command Line
```bash
python resume_generator.py --profile profile.json --jd job_description.txt --output resume.pdf
```

## Project Structure

```
├── app.py                  # Streamlit web interface
├── resume_generator.py     # Core AI resume generation engine
├── profile_manager.py      # User profile management
├── export_handler.py       # Resume export (PDF, DOCX)
├── templates/             # Resume templates
│   └── default_profile.json
├── profiles/              # User profiles (created at runtime)
└── output/               # Generated resumes (created at runtime)
```

## Requirements

- Python 3.8+
- Anthropic Claude API key
- Internet connection for AI API calls

## Tips for Best Results

- **Complete Profile**: Add as much detail as possible to your master profile
- **Quantify Achievements**: Include numbers, percentages, and metrics
- **Use Action Verbs**: Start bullet points with strong action verbs
- **Keep It Current**: Update your profile regularly with new skills and experiences

## Privacy & Security

- All data is stored locally on your machine
- API calls are made directly to Anthropic with encryption
- No data is stored on external servers (except temporary Claude API processing)
- Your profile and resumes remain on your device

## License

MIT License - feel free to modify and use for your needs!
