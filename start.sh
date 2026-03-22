#!/bin/bash
# Railway start script

echo "🚀 Starting GDC LeadMachine..."

# Start backend
cd backend
uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
