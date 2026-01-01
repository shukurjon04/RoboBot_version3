FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc and python3-dev might be needed for some python packages
# netcat-openbsd is useful for wait-for-it scripts or checking services
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    netcat-openbsd \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Run the bot using entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
