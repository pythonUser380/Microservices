FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including SQL Server ODBC driver
RUN apt-get update && \
    apt-get install -y gnupg curl unixodbc-dev gcc g++ netcat-openbsd && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies (adjust this to match your service: authservice OR balanceservice)
RUN pip install --no-cache-dir -r  balanceservice/requirements.txt

# Ensure entrypoint is executable
RUN chmod +x balanceservice/entrypoint.sh

# Ensure Python can import from service directory
ENV PYTHONPATH=/app

ENTRYPOINT ["balanceservice/entrypoint.sh"]
