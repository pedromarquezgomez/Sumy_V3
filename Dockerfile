# Dockerfile para Sumy_V3 ADK
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Configurar variables de entorno
ENV GOOGLE_GENAI_USE_VERTEXAI=true
ENV GOOGLE_CLOUD_PROJECT=maitre-digital
ENV GOOGLE_CLOUD_LOCATION=us-central1

# Exponer puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "hybrid_main.py"]