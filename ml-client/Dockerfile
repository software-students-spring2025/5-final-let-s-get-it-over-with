FROM python:3.11-slim

WORKDIR /ml-client

# Helps load the cv2 library
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "-u", "comments.py"]