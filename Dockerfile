FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps kept minimal (curl useful for basic container debugging)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py ./run.py
COPY scripts ./scripts

EXPOSE 5000

# Gunicorn for production-like serving
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.wsgi:app"]

