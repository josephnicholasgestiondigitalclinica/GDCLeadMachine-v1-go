FROM python:3.11-slim

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire repo
COPY . .

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Build frontend
RUN cd frontend && npm install --global yarn && yarn install && CI=false yarn build

# Expose port
EXPOSE 8080

# Start the backend
CMD ["sh", "-c", "cd backend && uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
