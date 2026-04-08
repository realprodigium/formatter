"""
Backend FastAPI de ejemplo para el procesador de archivos XLSX.
Este archivo es solo una referencia - adáptalo a tu lógica de conciliación.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO
from datetime import datetime

app = FastAPI(
    title="Conciliador XLSX API",
    description="API para procesar archivos Excel para conciliación bancaria",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        # Agrega tu dominio de producción aquí
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Conciliador XLSX API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    """
    Procesa un archivo XLSX:
    1. Lee el archivo
    2. Limpia y normaliza los datos
    3. Retorna el archivo procesado
    """
    
    # Validar tipo de archivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Formato no válido. Solo se aceptan archivos .xlsx o .xls"
        )
    
    try:
        # Leer el archivo
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # === LÓGICA DE PROCESAMIENTO ===
        # Aquí implementa tu lógica específica de conciliación bancaria
        
        # Ejemplo de operaciones comunes:
        
        # 1. Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # 2. Eliminar duplicados
        df = df.drop_duplicates()
        
        # 3. Limpiar espacios en blanco en columnas de texto
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', '')
        
        # 4. Normalizar columnas numéricas (si existen columnas de montos)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            # Redondear a 2 decimales para montos
            df[col] = df[col].round(2)
        
        # 5. Normalizar fechas (si existen columnas de fecha)
        for col in df.columns:
            if 'fecha' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
                except:
                    pass
        
        # 6. Ordenar por la primera columna (ajusta según tu necesidad)
        if len(df.columns) > 0:
            df = df.sort_values(by=df.columns[0], ascending=True, na_position='last')
        
        # 7. Resetear índices
        df = df.reset_index(drop=True)
        
        # === FIN LÓGICA DE PROCESAMIENTO ===
        
        # Generar el archivo de salida
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Conciliado')
        output.seek(0)
        
        # Generar nombre del archivo de salida
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"conciliado_{original_name}_{timestamp}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
