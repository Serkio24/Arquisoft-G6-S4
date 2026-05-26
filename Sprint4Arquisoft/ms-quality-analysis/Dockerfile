# Imagen base liviana para FastAPI
FROM python:3.11-slim

WORKDIR /service

# Instalar dependencias primero (capa cacheada en rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/

# Puerto en el que escucha FastAPI — Kong apunta aquí
EXPOSE 8080

# Uvicorn como servidor ASGI de producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
