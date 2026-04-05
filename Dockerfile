FROM python:3.13-slim

WORKDIR /app

# Copy dependency list
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables for performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Entry point
CMD ["python", "run.py"]
