# BankFlow

Aplicación web para procesar extractos bancarios en XLSX, generar una tabla limpia y descargar un archivo listo para conciliación.

## Estructura

- `backend/`: API FastAPI que procesa el extracto y expone los endpoints.
- `frontend/`: app React + Vite con interfaz minimalista y glassmorphism.
- `Dockerfile`: build multi-stage para React y FastAPI.

## Comandos locales

### Backend

```bash
cd bankflow/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd bankflow/frontend
pnpm install
pnpm dev
```

## Build Docker

```bash
cd bankflow
docker build -t bankflow .
docker run -p 8000:8000 bankflow
```

## Despliegue en Render

Configura un servicio Docker con el Dockerfile en la carpeta `bankflow`.
El servidor levantará la app en el puerto `8000`.

### Seguridad en Render

- El servicio procesa los archivos en memoria y no guarda el archivo cargado ni el archivo generado en disco.
- Render provee TLS/HTTPS para la transmisión segura de los archivos entre el navegador y el servidor.
- El backend añade encabezados de seguridad recomendados para proteger la aplicación web.
