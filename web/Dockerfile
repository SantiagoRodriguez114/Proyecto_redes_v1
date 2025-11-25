FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero (para hacer caching correcto)
COPY requirements.txt /app/

# Instalar dependencias del sistema necesarias para gevent
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto del código
COPY . /app/

# Puerto de Flask
EXPOSE 5000

# Ejecutar con gunicorn + gevent
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "1", "--bind", "0.0.0.0:5000", "app:app"]
