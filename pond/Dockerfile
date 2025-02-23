FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-pygame \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable to disable ALSA sound
ENV SDL_AUDIODRIVER=dummy

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the application files
COPY . .

# Command to run the application
CMD ["python", "main.py"]