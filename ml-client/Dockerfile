FROM python:3.11-slim

WORKDIR /ml-client

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