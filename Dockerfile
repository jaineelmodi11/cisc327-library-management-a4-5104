# Dockerfile
FROM python:3.11-slim

# Don't write .pyc files, don't buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code into the image
COPY . .

# Flask config
# our app object lives in app.py as "app"
ENV FLASK_APP=app:app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose port 5000 to the host
EXPOSE 5000

# Run the Flask dev server inside the container
CMD ["flask", "run"]
