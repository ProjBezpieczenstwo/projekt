FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app
RUN update-ca-certificates
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "email_service.py"]