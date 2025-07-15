FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gnupg curl unixodbc-dev gcc g++ netcat-openbsd && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

COPY . .

COPY balanceservice/entrypoint.sh .

RUN chmod +x entrypoint.sh

RUN pip install --no-cache-dir -r invoiceservice/requirements.txt

ENV PYTHONPATH=/app

ENTRYPOINT ["./entrypoint.sh"]
