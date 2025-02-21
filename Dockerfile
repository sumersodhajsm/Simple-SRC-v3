FROM python:3.10.4-slim-buster

# Update apt and install necessary packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Ensure pip is updated and install wheel
RUN pip install --upgrade pip wheel

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory to /app
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Expose port 5000 (since Quart runs on port 5000 by default)
EXPOSE 8000

# Start the Quart application
CMD flask run -h 0.0.0.0 -p 8000 & python3 main.py
