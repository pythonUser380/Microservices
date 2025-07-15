#!/bin/sh
echo "Waiting for SQL Server..."

while ! nc -z db 1433; do
  sleep 1
done

echo "SQL Server started"
python authservice/app.py
