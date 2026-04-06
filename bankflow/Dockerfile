# Frontend build stage
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

RUN npm install -g pnpm

COPY frontend/package.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts frontend/index.html frontend/src ./
RUN pnpm install
RUN pnpm build

# Backend runtime stage
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
WORKDIR /app

COPY backend/pyproject.toml ./
RUN uv pip install --system --no-cache \
    fastapi uvicorn[standard] python-multipart openpyxl pandas xlsxwriter

COPY backend ./backend
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
