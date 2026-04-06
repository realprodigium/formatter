import { ChangeEvent, useMemo, useState } from "react";

type PreviewRow = Record<string, string | number | null>;

type Summary = {
  total_transacciones: number;
  total_abonos: number;
  total_debitos: number;
  saldo_neto: number;
  saldo_final: number;
  tipos_transaccion: number;
};

type PreviewResponse = {
  columns: string[];
  rows: PreviewRow[];
  total_rows: number;
  summary: Summary;
};

const showMoney = (value: number) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 2,
  }).format(value);

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Selecciona un archivo .xlsx para comenzar.");

  const columns = useMemo(() => preview?.columns ?? [], [preview]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setPreview(null);
    setMessage(nextFile ? "Archivo cargado. Previsualiza antes de descargar." : "Selecciona un archivo .xlsx para comenzar.");
  };

  const uploadPreview = async () => {
    if (!file) {
      setMessage("Debes seleccionar un archivo primero.");
      return;
    }

    setLoading(true);
    setMessage("Procesando extracto...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload/preview", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Error al leer el archivo.");
      }

      const data = (await response.json()) as PreviewResponse;
      setPreview(data);
      setMessage("Vista previa lista. Descarga el archivo limpio cuando quieras.");
    } catch (error) {
      setPreview(null);
      setMessage(error instanceof Error ? error.message : "No se pudo procesar el archivo.");
    } finally {
      setLoading(false);
    }
  };

  const downloadCleanFile = async () => {
    if (!file) {
      setMessage("Selecciona un archivo para descargar el resultado.");
      return;
    }

    setLoading(true);
    setMessage("Generando archivo limpio...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload/download", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Error al generar el archivo.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "extracto_limpio.xlsx";
      anchor.click();
      URL.revokeObjectURL(url);
      setMessage("Archivo listo para descargar.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No se pudo descargar el archivo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="panel card">
        <div className="header-block">
          <div>
            <p className="eyebrow">BankFlow</p>
            <h1>Conciliación de extractos bancarios</h1>
          </div>
          <p className="lead">
            Sube tu archivo XLSX y recibe un extracto limpio, ordenado y listo para descargar.
          </p>
        </div>

        <div className="form-grid">
          <label className="upload-box" htmlFor="file-upload">
            <span className="upload-title">Arrastra o selecciona el archivo</span>
            <span className="upload-hint">Solo .xlsx / .xls. Se procesa en el mismo navegador con el backend.</span>
            <input
              id="file-upload"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
            />
          </label>

          <div className="actions">
            <button type="button" onClick={uploadPreview} disabled={loading || !file}>
              {loading ? "Procesando…" : "Previsualizar"}
            </button>
            <button
              type="button"
              className="primary"
              onClick={downloadCleanFile}
              disabled={loading || !file}
            >
              Descargar limpio
            </button>
          </div>

          <div className="status-box">
            <strong>Estado</strong>
            <p>{message}</p>
          </div>
        </div>

        {preview ? (
          <>
            <div className="summary-grid">
              <div>
                <span>Total transacciones</span>
                <strong>{preview.total_rows}</strong>
              </div>
              <div>
                <span>Total abonos</span>
                <strong>{showMoney(preview.summary.total_abonos)}</strong>
              </div>
              <div>
                <span>Total débitos</span>
                <strong>{showMoney(preview.summary.total_debitos)}</strong>
              </div>
              <div>
                <span>Saldo neto</span>
                <strong>{showMoney(preview.summary.saldo_neto)}</strong>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((row, index) => (
                    <tr key={index}>
                      {columns.map((column) => (
                        <td key={`${index}-${column}`}>{row[column] ?? ""}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default App;
