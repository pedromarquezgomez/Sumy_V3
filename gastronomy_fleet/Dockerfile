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
COPY coordinator_agent/ ./coordinator_agent/
COPY culinary_agent/ ./culinary_agent/
COPY nutrition_agent/ ./nutrition_agent/
COPY sumiller_agent/ ./sumiller_agent/
COPY main.py .
COPY fleet.yaml .

# Copia los índices vectoriales que se generarán con ingest.py
# Debes ejecutar 'python ingest.py' antes de construir la imagen
COPY culinary_index/ ./culinary_index/
COPY enology_index/ ./enology_index/
COPY nutrition_index/ ./nutrition_index/

# Ejecuta la aplicación como un usuario no-root
RUN addgroup --system app && adduser --system --group app
USER app

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 