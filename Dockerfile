# Use the official Python image as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the container
COPY palm_detection.py .

# Set the entry point to run the Python script
ENTRYPOINT ["python", "./palm_detection.py"]
