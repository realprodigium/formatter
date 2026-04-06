"""
BankFlow API – Bank Statement Reconciliation Service
"""
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import io
import json

from processor import process_bank_statement

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend_dist"
MAX_UPLOAD_BYTES = 12 * 1024 * 1024

app = FastAPI(
    title="BankFlow API",
    description="Procesa y limpia extractos bancarios para conciliación",
    version="1.0.0",
)

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "interest-cohort=()"
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": "bankflow-api"}


@app.post("/api/upload/preview")
async def upload_preview(file: UploadFile = File(...)):
    """
    Recibe el XLSX, lo procesa y devuelve un JSON con:
      - columns: lista de cabeceras
      - rows:    primeras 50 filas
      - summary: estadísticas básicas
    """
    _validate_file(file)
    contents = await _read_upload(file)
    try:
        df, summary = process_bank_statement(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error al procesar el archivo: {str(e)}")

    preview_rows = df.head(50).to_dict(orient="records")
    # Serialize dates / NaN safely
    safe_rows = json.loads(json.dumps(preview_rows, default=str))

    return {
        "columns": list(df.columns),
        "rows": safe_rows,
        "total_rows": len(df),
        "summary": summary,
    }


@app.post("/api/upload/download")
async def upload_download(file: UploadFile = File(...)):
    """
    Recibe el XLSX, lo procesa y devuelve el XLSX limpio para descargar.
    """
    _validate_file(file)
    contents = await _read_upload(file)
    try:
        df, summary = process_bank_statement(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error al procesar el archivo: {str(e)}")

    output = io.BytesIO()
    _write_xlsx(df, summary, output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="extracto_limpio.xlsx"'},
    )


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    if FRONTEND_DIST.exists():
        index_html = FRONTEND_DIST / "index.html"
        if index_html.exists():
            return FileResponse(index_html)
    raise HTTPException(status_code=404, detail="Ruta no encontrada")


# ─── helpers ────────────────────────────────────────────────────────────────

def _validate_file(file: UploadFile):
    allowed = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    }
    ext = (file.filename or "").lower().split(".")[-1]
    if ext not in ("xlsx", "xls"):
        raise HTTPException(status_code=415, detail="Solo se aceptan archivos .xlsx / .xls")
    if file.content_type not in allowed and ext not in ("xlsx", "xls"):
        raise HTTPException(status_code=415, detail="Tipo de archivo no permitido")


async def _read_upload(file: UploadFile) -> bytes:
    contents = await file.read()
    await file.close()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el límite de 12 MB")
    return contents


def _write_xlsx(df, summary: dict, output: io.BytesIO):
    import xlsxwriter

    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    # ── Formats ──────────────────────────────────────────────────────────────
    header_fmt = workbook.add_format({
        "bold": True, "font_color": "#FFFFFF", "bg_color": "#1a1a1a",
        "border": 1, "border_color": "#333333", "font_size": 11,
        "align": "center", "valign": "vcenter",
    })
    money_pos_fmt = workbook.add_format({
        "num_format": '#,##0', "bg_color": "#f0fdf4",
        "border": 1, "border_color": "#e2e8f0",
    })
    money_neg_fmt = workbook.add_format({
        "num_format": '#,##0', "bg_color": "#fff1f2",
        "font_color": "#dc2626",
        "border": 1, "border_color": "#e2e8f0",
    })
    date_fmt = workbook.add_format({
        "num_format": "dd/mm", "border": 1, "border_color": "#e2e8f0",
    })
    text_fmt = workbook.add_format({
        "border": 1, "border_color": "#e2e8f0",
    })

    # ── Transactions sheet ─────────────────────────────────────────────────
    ws = workbook.add_worksheet("Transacciones")
    ws.set_zoom(90)
    ws.freeze_panes(1, 0)

    cols = list(df.columns)
    for ci, col in enumerate(cols):
        ws.write(0, ci, col, header_fmt)

    money_cols = {"SALDO", "VALOR"}

    for ri, row in enumerate(df.itertuples(index=False), start=1):
        for ci, col in enumerate(cols):
            val = getattr(row, col.replace(" ", "_").replace("/", "_"), None)
            if col in money_cols:
                fmt = money_neg_fmt if (val or 0) < 0 else money_pos_fmt
                ws.write_number(ri, ci, float(val or 0), fmt)
            elif col == "FECHA":
                ws.write(ri, ci, str(val), date_fmt)
            else:
                ws.write(ri, ci, str(val) if val is not None else "", text_fmt)

    col_widths = {"DESCRIPCIÓN": 40, "SUCURSAL": 22, "FECHA": 10, "SALDO": 18, "VALOR": 18}
    for ci, col in enumerate(cols):
        ws.set_column(ci, ci, col_widths.get(col, 18))

    ws.autofilter(0, 0, len(df), len(cols) - 1)

    # ── Summary sheet ──────────────────────────────────────────────────────
    ws2 = workbook.add_worksheet("Resumen")
    title_fmt = workbook.add_format({"bold": True, "font_size": 14, "font_color": "#1a1a1a"})
    label_fmt = workbook.add_format({"bold": True, "bg_color": "#f8fafc", "border": 1, "border_color": "#e2e8f0"})
    value_fmt  = workbook.add_format({"num_format": '#,##0', "border": 1, "border_color": "#e2e8f0"})
    int_fmt    = workbook.add_format({"num_format": '0', "border": 1, "border_color": "#e2e8f0"})

    ws2.write(0, 0, "Resumen del Extracto Bancario", title_fmt)
    ws2.set_column(0, 0, 35)
    ws2.set_column(1, 1, 22)

    labels = [
        ("Total de Transacciones",    summary.get("total_transacciones", 0), int_fmt),
        ("Total Abonos (COP)",         summary.get("total_abonos", 0),         value_fmt),
        ("Total Débitos (COP)",        summary.get("total_debitos", 0),        value_fmt),
        ("Saldo Neto (COP)",           summary.get("saldo_neto", 0),           value_fmt),
        ("Saldo Final (COP)",          summary.get("saldo_final", 0),          value_fmt),
        ("Tipos de Transacciones",     summary.get("tipos_transaccion", 0),    int_fmt),
    ]
    for i, (lbl, val, fmt) in enumerate(labels, start=2):
        ws2.write(i, 0, lbl, label_fmt)
        ws2.write_number(i, 1, float(val or 0), fmt)

    workbook.close()
