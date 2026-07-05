# 1. Imagen base oficial y ligera
FROM python:3.11-slim

# 2. Configurar variables de entorno para optimizar Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 3. Instalar herramientas del sistema y la librería OpenMP para LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el contenido local (incluyendo app.py y los dos archivos .pkl)
COPY . /app

# 6. Exponer el puerto de la API REST
EXPOSE 8000

# 7. Comando de arranque usando Uvicorn con optimización de hilos (workers)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
