FROM python:3.10-slim

WORKDIR /app

COPY splitservice/requirements.txt .
#COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "-m", "splitservice.app"]

