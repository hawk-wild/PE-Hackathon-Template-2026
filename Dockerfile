FROM python:3.13-slim

# Install uv directly into the container using the official binary image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv into the container's virtual environment
RUN uv sync --frozen --no-dev

# Copy the rest of the application files
COPY . .

# Explicitly state the port we will listen on
EXPOSE 8000

# Start Uvicorn via the run.py script (which spins up 4 workers per container!)
CMD ["uv", "run", "python", "run.py"]
