# AI Resume Generator - Backend API

FastAPI backend for the AI Resume Generator application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /api/profiles` - List all profiles
- `GET /api/profiles/{name}` - Get a specific profile
- `POST /api/profiles` - Create/update a profile
- `DELETE /api/profiles/{name}` - Delete a profile
- `POST /api/generate-resume` - Generate tailored resume
- `POST /api/export/docx` - Export resume as DOCX
- `POST /api/export/pdf` - Export resume as PDF
- `POST /api/api-key` - Save Claude API key
- `GET /api/api-key/status` - Check if API key is configured

## Data Persistence

- Profiles are stored in the `profiles/` directory
- API key is stored in `.api_config.json`
- Resume history is stored in `resume_history.json`
