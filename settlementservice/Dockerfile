# Base image with Python
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy only requirements.txt.txt.txt first to use Docker layer cache
COPY settlementservice/requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy entire service code
COPY . .

ENV PYTHONPATH=/app
# Expose the port used by Flask (5003 is standard for this service)
EXPOSE 5003

# Default command to run the service
#CMD ["python", "app.py"]
CMD ["python", "-m", "settlementservice.app"]
