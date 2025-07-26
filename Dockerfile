# FROM python:3.10-slim

# WORKDIR /app

# COPY process_pdfs.py .

# RUN pip install PyMuPDF

# CMD ["python", "process_pdfs.py"]

# Use base image
FROM python:3.10-slim

# Set platform (optional)
# FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY process_pdfs.py .

# Run script
CMD ["python", "process_pdfs.py"]
