FROM python:3.11-slim

LABEL maintainer="info@merendamattia.com"

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Ensure output dir exists
RUN mkdir -p /app/output

# Default entrypoint runs the CLI; user must pass --target-path
ENTRYPOINT ["python", "src/app.py"]
