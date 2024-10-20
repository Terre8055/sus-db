# Stage 1: Build stage
FROM python:3.9-slim AS builder

# Set environment variables for security and non-interactive installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install python dependencies in a temporary directory
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Production stage
FROM python:3.9-slim

# Set environment variables for security and non-interactive installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for runtime only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the python dependencies from the build stage
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

ENV PYTHONPATH=/app/src

RUN chmod +x welcome_script.sh

CMD ["./welcome_script.sh"]
