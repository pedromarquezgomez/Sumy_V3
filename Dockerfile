# Dockerfile

# --- Etapa 1: Builder ---
# Instala dependencias en un entorno virtual
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Final ---
# Crea la imagen final, limpia y segura
FROM python:3.11-slim-bookworm AS final
WORKDIR /app
COPY --from=builder /app/venv /app/venv

# Copia todos los directorios de los agentes y el punto de entrada
COPY agents/ ./agents/
COPY main.py .
COPY fleet.yaml .
COPY adk_config.py .

# Copia los índices vectoriales que se generaron con data_ingestion/ingest.py
COPY indexes/ ./indexes/

# Ejecuta la aplicación como un usuario no-root
RUN addgroup --system app && adduser --system --group app
USER app

ENV PATH="/app/venv/bin:$PATH"
# Set default environment variables (can be overridden at runtime)
ENV GOOGLE_CLOUD_PROJECT=""
ENV VERTEX_AI_LOCATION="us-central1"
ENV GOOGLE_APPLICATION_CREDENTIALS=""

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 