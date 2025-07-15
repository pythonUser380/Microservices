#!/bin/sh
echo "Waiting for SQL Server..."

while ! nc -z sqlserver 1433; do
  sleep 1
done

echo "SQL Server started"
python invoiceservice/app.py
