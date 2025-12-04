# Migration to Claude AI ✅

The AI Resume Generator has been successfully converted from OpenAI to Claude AI (Anthropic)!

## What Changed

### 1. **Dependencies** (`requirements.txt`)
- ✅ Replaced `openai` with `anthropic`
- ✅ Removed `tiktoken` (no longer needed)

### 2. **Core Engine** (`resume_generator.py`)
- ✅ Updated to use Claude's Messages API
- ✅ Changed model to `claude-3-5-sonnet-20241022`
- ✅ Modified all API calls to Claude's format
- ✅ Updated error messages and validation

### 3. **Environment Variables** (`.env.example`)
- ✅ Changed from `OPENAI_API_KEY` to `ANTHROPIC_API_KEY`
- ✅ Updated API key URL to Anthropic console

### 4. **Web Interface** (`app.py`)
- ✅ Updated UI to reference "Claude API Key"
- ✅ Changed help text and error messages
- ✅ Updated API key environment variable

### 5. **Documentation**
- ✅ Updated `README.md` with Claude references
- ✅ Updated `SETUP.md` with new API key instructions
- ✅ Updated API cost estimates
- ✅ Changed all OpenAI URLs to Anthropic URLs

## How to Get Started

### 1. Install Updated Dependencies

```bash
pip install -r requirements.txt
```

This will install the Anthropic SDK instead of OpenAI.

### 2. Get Your Claude API Key

1. Go to: https://console.anthropic.com/settings/keys
2. Sign up or log in to Anthropic
3. Click "Create Key"
4. Copy your API key

### 3. Configure Your API Key

**Option A: Using .env file (Recommended)**
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

**Option B: Enter in the app**
- Run the app and enter your API key in the sidebar

### 4. Run the Application

```bash
streamlit run app.py
```

## Why Claude AI?

### Advantages of Claude:
- 🎯 **Better Context Understanding**: Excellent at understanding nuanced job descriptions
- 📝 **Superior Writing Quality**: More natural and professional resume writing
- 🔒 **Enhanced Safety**: Strong ethical guidelines and content moderation
- 💰 **Competitive Pricing**: Good value for quality
- 🚀 **Latest Model**: Claude 3.5 Sonnet (Oct 2024) with 200K context window

### Model Information:
- **Default**: `claude-3-5-sonnet-20241022`
- **Cost**: ~$0.30-0.60 per resume generation
- **Context**: 200K tokens
- **Quality**: State-of-the-art language understanding

## API Cost Comparison

| Feature | OpenAI (GPT-4o-mini) | Claude (3.5 Sonnet) |
|---------|---------------------|---------------------|
| Cost per resume | $0.10-0.30 | $0.30-0.60 |
| Quality | Good | Excellent |
| Context window | 128K tokens | 200K tokens |
| Response quality | Very good | Outstanding |

## Troubleshooting

### "Claude API key is required"
- Make sure you've set `ANTHROPIC_API_KEY` in your `.env` file
- Or enter it in the app sidebar
- Verify your key at: https://console.anthropic.com/settings/keys

### "Error generating resume"
- Check internet connection
- Verify you have Anthropic credits
- Check API key is valid and active

### Import errors
- Run `pip install -r requirements.txt` again
- Make sure you uninstall old dependencies: `pip uninstall openai tiktoken`

## Model Options

You can customize the model in `resume_generator.py`:

```python
# In resume_generator.py, line 25:
self.model = "claude-3-5-sonnet-20241022"  # Default (best quality)

# Alternative options:
self.model = "claude-3-5-haiku-20241022"   # Faster, cheaper
self.model = "claude-3-opus-20240229"      # Most powerful (more expensive)
```

## Feature Compatibility

All features work exactly the same:
- ✅ Profile management
- ✅ Job description analysis
- ✅ Resume tailoring
- ✅ Export to PDF, DOCX, TXT
- ✅ Web interface
- ✅ All existing functionality preserved

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Get Claude API key**: https://console.anthropic.com/settings/keys
3. **Configure**: Add key to `.env` file
4. **Run**: `streamlit run app.py`
5. **Generate**: Create amazing tailored resumes!

---

**Note**: Your existing profiles are 100% compatible. No need to recreate them!

Enjoy better resume generation with Claude AI! 🎉
