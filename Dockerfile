# Dockerfile
FROM python:3.9.13-slim

# Create app user (non-root)
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# System deps (if you need them uncomment)
# RUN apt-get update && apt-get install -y build-essential

# Copy dependency specification first for better caching
COPY requirements.txt .

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure files are owned by appuser
RUN chown -R appuser:appuser /home/appuser/app

USER appuser

# Port that uvicorn will run on
EXPOSE 8000

# Use environment variable for host/port in command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]