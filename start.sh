#!/bin/bash

echo "🚀 Starting AI Sales Pitch Customization Agent..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed or not in PATH"
    exit 1
fi

echo "✅ Dependencies check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd api
pip3 install -r ../requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start backend in background
echo "🔧 Starting Flask backend..."
cd api
python3 api.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:5000/api/health > /dev/null; then
    echo "✅ Backend is running on http://127.0.0.1:5000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🌐 Starting React frontend..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 System is starting up!"
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔧 Backend is running at: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 