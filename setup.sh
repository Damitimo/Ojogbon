#!/bin/bash

echo "🚀 Setting up AI Resume Generator (React + FastAPI)"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📦 Step 1: Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

echo "✅ Backend setup complete!"
echo ""

# Go back to root
cd ..

echo "📦 Step 2: Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js packages (this may take a few minutes)..."
npm install

echo "✅ Frontend setup complete!"
echo ""

cd ..

echo "🎉 Setup Complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "✅ Your profile 'Tech Profile' is safe and ready to use!"
