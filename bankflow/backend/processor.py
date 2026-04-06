"""
processor.py – Limpieza y transformación del extracto bancario.

Estructura original del XLSX:
  Cols:  _1 | Column1 | DCTO. | DESCRIPCIÓN | FECHA | Suma de SALDO | SUCURSAL | Suma de VALOR
  Fila 1 (header real)
  Filas 2-N: datos con columnas _1, Column1, DCTO. mayormente NULL

Salida esperada:
  DESCRIPCIÓN | FECHA | SALDO | VALOR | TIPO | SUCURSAL
  Con SALDO y VALOR como int/float (COP), sin símbolo de moneda.
"""

from __future__ import annotations
import re
import io
import pandas as pd


# ─── Columnas de interés ────────────────────────────────────────────────────
_RENAME = {
    "DESCRIPCIÓN":      "DESCRIPCIÓN",
    "FECHA":            "FECHA",
    "Suma de SALDO":    "SALDO",
    "Suma de VALOR":    "VALOR",
    "SUCURSAL":         "SUCURSAL",
    "DCTO.":            "DCTO",
}

_MONEY_RE = re.compile(r"[^0-9\-]")   # elimina $, comas, espacios, etc.


def _parse_money(val) -> float | None:
    """Convierte '$ 254,115,530' o '-$ 432,372' a float."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ("NULL", "None", ""):
        return None
    # determinar signo
    negative = s.startswith("-")
    # quitar todo excepto dígitos y el signo inicial
    digits = _MONEY_RE.sub("", s)
    if not digits:
        return None
    result = float(digits)
    return -result if negative else result


def _classify(desc: str) -> str:
    """Clasifica la transacción según la descripción."""
    d = str(desc).upper()
    if "ABONO INTERESES" in d:
        return "Intereses"
    if "PAGO A NOMIN" in d or "PAGO DE NOMIN" in d or "SERVICIO PAGO DE NOMINA" in d:
        return "Nomina"
    if "PAGO A PROV" in d or "PAGO A PROVE" in d or "PAGO DE PROV" in d:
        return "Proveedores"
    if "IMPTO GOBIERNO" in d or "CXC IMPTO" in d or "IVA CUOTA" in d or "COBRO IVA" in d:
        return "Impuestos"
    if "PAGO INTERBANC" in d:
        return "Interbancos"
    if "CONSIGNACION" in d:
        return "Consignacion"
    if "PAGO PSE" in d:
        return "PSE"
    if "SERVICIO" in d:
        return "Servicios"
    if "LEASING" in d.lower() or "CUOTA OPERACION" in d:
        return "Leasing"
    if "CUOTA PLAN" in d:
        return "Cuota"
    return "Otros"


def process_bank_statement(file_like: io.BytesIO) -> tuple[pd.DataFrame, dict]:
    """
    Lee el XLSX, limpia y transforma.
    Retorna (df_limpio, summary_dict).
    """
    # ── 1. Leer raw ──────────────────────────────────────────────────────────
    df_raw = pd.read_excel(file_like, sheet_name=0, header=0, dtype=str)

    # ── 2. Seleccionar columnas relevantes ───────────────────────────────────
    keep = [c for c in df_raw.columns if c in _RENAME]
    df = df_raw[keep].copy()
    df.rename(columns=_RENAME, inplace=True)

    # Asegurar columna SUCURSAL aunque no exista
    if "SUCURSAL" not in df.columns:
        df["SUCURSAL"] = None
    if "DCTO" not in df.columns:
        df["DCTO"] = None

    # ── 3. Eliminar filas completamente vacías ───────────────────────────────
    df = df.dropna(how="all").reset_index(drop=True)

    # Eliminar la primera fila si es la cabecera repetida
    if df.iloc[0]["DESCRIPCIÓN"] in ("DESCRIPCIÓN", None, "None", "nan"):
        df = df.iloc[1:].reset_index(drop=True)

    # ── 4. Limpiar DESCRIPCIÓN ───────────────────────────────────────────────
    df["DESCRIPCIÓN"] = df["DESCRIPCIÓN"].astype(str).str.strip()
    # Eliminar filas sin descripción válida
    df = df[df["DESCRIPCIÓN"].notna() & (df["DESCRIPCIÓN"] != "None") & (df["DESCRIPCIÓN"] != "")].copy()

    # ── 5. Parsear montos ────────────────────────────────────────────────────
    df["SALDO"] = df["SALDO"].apply(_parse_money)
    df["VALOR"] = df["VALOR"].apply(_parse_money)

    # ── 6. Limpiar FECHA ─────────────────────────────────────────────────────
    df["FECHA"] = df["FECHA"].astype(str).str.strip()
    # Normalizar formato DD/MM
    def _norm_fecha(f: str) -> str:
        parts = f.split("/")
        if len(parts) == 2:
            day, month = parts
            return f"{int(day):02d}/{int(month):02d}"
        return f
    df["FECHA"] = df["FECHA"].apply(_norm_fecha)

    # ── 7. Clasificar ────────────────────────────────────────────────────────
    df["TIPO"] = df["DESCRIPCIÓN"].apply(_classify)

    # ── 8. Limpiar SUCURSAL ──────────────────────────────────────────────────
    df["SUCURSAL"] = df["SUCURSAL"].astype(str).str.strip()
    df["SUCURSAL"] = df["SUCURSAL"].replace({"None": "", "nan": "", "NULL": ""})

    # ── 9. Reordenar columnas ────────────────────────────────────────────────
    final_cols = ["FECHA", "DESCRIPCIÓN", "TIPO", "SALDO", "VALOR", "SUCURSAL"]
    if "DCTO" in df.columns:
        final_cols.append("DCTO")
    df = df[final_cols].reset_index(drop=True)

    # ── 10. Convertir dtypes finales ─────────────────────────────────────────
    df["SALDO"] = pd.to_numeric(df["SALDO"], errors="coerce")
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

    # ── 11. Resumen ──────────────────────────────────────────────────────────
    abonos  = df.loc[df["VALOR"] > 0, "VALOR"].sum()
    debitos = df.loc[df["VALOR"] < 0, "VALOR"].sum()
    summary = {
        "total_transacciones": int(len(df)),
        "total_abonos":        round(float(abonos), 2),
        "total_debitos":       round(float(debitos), 2),
        "saldo_neto":          round(float(abonos + debitos), 2),
        "saldo_final":         round(float(df["SALDO"].iloc[-1]) if not df.empty else 0, 2),
        "tipos_transaccion":   int(df["TIPO"].nunique()),
    }

    return df, summary
