FROM python:3.11-slim

WORKDIR /app

# dependencias del sistema
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/
COPY templates /app/templates

# carpeta data (sqlite) montada por docker-compose en /data
VOLUME ["/data"]

EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:5000", "app:app"]
