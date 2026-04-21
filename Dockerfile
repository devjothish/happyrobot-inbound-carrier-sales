FROM node:20-alpine AS web

WORKDIR /web

COPY web/package*.json ./
RUN npm ci

COPY web ./
RUN npm run build


FROM python:3.12-slim AS api

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

COPY --from=web /web/out ./web_static

RUN mkdir -p /data

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
