FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Microsoft ODBC driver
RUN apt-get update && \
    apt-get install -y gnupg curl unixodbc-dev gcc g++ netcat-openbsd && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r authservice/requirements.txt

# Make entrypoint executable
RUN chmod +x authservice/entrypoint.sh

# Set Python path to resolve imports like balanceservice.*
ENV PYTHONPATH=/app

# Entrypoint that waits for SQL Server to be ready
ENTRYPOINT ["authservice/entrypoint.sh"]
