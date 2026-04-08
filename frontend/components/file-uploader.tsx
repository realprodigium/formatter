"use client"

import { useCallback, useState } from "react"
import { Upload, File, X, CheckCircle2, AlertCircle, Loader2, Download } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileUploaderProps {
  apiEndpoint: string
  acceptedFileTypes?: string
  maxFileSize?: number
}

type UploadStatus = "idle" | "uploading" | "processing" | "success" | "error"

interface ProcessedFile {
  name: string
  downloadUrl: string
}

export function FileUploader({
  apiEndpoint,
  acceptedFileTypes = ".xlsx,.xls",
  maxFileSize = 10,
}: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<UploadStatus>("idle")
  const [errorMessage, setErrorMessage] = useState<string>("")
  const [processedFile, setProcessedFile] = useState<ProcessedFile | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const validateFile = (file: File): string | null => {
    const validExtensions = acceptedFileTypes.split(",").map((ext) => ext.trim().toLowerCase())
    const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`

    if (!validExtensions.includes(fileExtension)) {
      return `Tipo de archivo no válido. Acepta: ${acceptedFileTypes}`
    }

    if (file.size > maxFileSize * 1024 * 1024) {
      return `El archivo excede el tamaño máximo de ${maxFileSize}MB`
    }

    return null
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile) {
        const error = validateFile(droppedFile)
        if (error) {
          setErrorMessage(error)
          setStatus("error")
          return
        }
        setFile(droppedFile)
        setStatus("idle")
        setErrorMessage("")
        setProcessedFile(null)
      }
    },
    [acceptedFileTypes, maxFileSize]
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0]
      if (selectedFile) {
        const error = validateFile(selectedFile)
        if (error) {
          setErrorMessage(error)
          setStatus("error")
          return
        }
        setFile(selectedFile)
        setStatus("idle")
        setErrorMessage("")
        setProcessedFile(null)
      }
    },
    [acceptedFileTypes, maxFileSize]
  )

  const removeFile = () => {
    setFile(null)
    setStatus("idle")
    setErrorMessage("")
    setProcessedFile(null)
  }

  const uploadFile = async () => {
    if (!file) return

    setStatus("uploading")
    setErrorMessage("")

    const formData = new FormData()
    formData.append("file", file)

    try {
      setStatus("processing")

      const response = await fetch(apiEndpoint, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Error del servidor: ${response.status}`)
      }

      const blob = await response.blob()
      const downloadUrl = URL.createObjectURL(blob)

      const contentDisposition = response.headers.get("content-disposition")
      let fileName = `conciliado_${file.name}`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/)
        if (match) fileName = match[1]
      }

      setProcessedFile({ name: fileName, downloadUrl })
      setStatus("success")
    } catch (error) {
      setStatus("error")
      setErrorMessage(error instanceof Error ? error.message : "Error al procesar el archivo")
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="w-full space-y-5 p-6">
      {/* Drop Zone - macOS Style */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-10 transition-all duration-200 cursor-pointer",
          "hover:border-neutral-400 hover:bg-neutral-50",
          isDragging && "border-blue-500 bg-blue-50/50 scale-[1.01]",
          status === "error" && "border-red-300",
          !isDragging && status !== "error" && "border-neutral-300 bg-neutral-50/50"
        )}
      >
        <input
          type="file"
          accept={acceptedFileTypes}
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={status === "uploading" || status === "processing"}
        />

        <div className="flex flex-col items-center gap-3 text-center">
          <div
            className={cn(
              "p-4 rounded-2xl transition-colors",
              isDragging ? "bg-blue-100" : "bg-neutral-100"
            )}
          >
            <Upload
              className={cn(
                "w-7 h-7 transition-colors",
                isDragging ? "text-blue-600" : "text-neutral-500"
              )}
              strokeWidth={1.5}
            />
          </div>

          <div className="space-y-1">
            <p className="text-neutral-800 font-medium text-sm">
              {isDragging ? "Suelta el archivo aquí" : "Arrastra tu archivo XLSX aquí"}
            </p>
            <p className="text-xs text-neutral-500">
              o haz clic para seleccionar
            </p>
          </div>
          
          <p className="text-[11px] text-neutral-400 mt-1">
            Máximo {maxFileSize}MB
          </p>
        </div>
      </div>

      {/* Selected File - Finder Style */}
      {file && (
        <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            {/* File Icon */}
            <div className="w-10 h-12 bg-gradient-to-b from-neutral-100 to-neutral-200 rounded-lg border border-neutral-300 flex items-center justify-center shadow-sm">
              <span className="text-[10px] font-bold text-neutral-500 uppercase">xlsx</span>
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-800 truncate">{file.name}</p>
              <p className="text-xs text-neutral-500">{formatFileSize(file.size)}</p>
            </div>

            {status === "idle" && (
              <button
                onClick={removeFile}
                className="p-1.5 hover:bg-neutral-200 rounded-lg transition-colors"
                aria-label="Eliminar archivo"
              >
                <X className="w-4 h-4 text-neutral-500" />
              </button>
            )}

            {(status === "uploading" || status === "processing") && (
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            )}

            {status === "success" && (
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            )}

            {status === "error" && (
              <AlertCircle className="w-5 h-5 text-red-500" />
            )}
          </div>

          {/* Progress - macOS style */}
          {(status === "uploading" || status === "processing") && (
            <div className="mt-4 space-y-2">
              <div className="h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full animate-pulse w-2/3" />
              </div>
              <p className="text-[11px] text-neutral-500 text-center">
                {status === "uploading" ? "Subiendo archivo..." : "Procesando conciliación..."}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {status === "error" && errorMessage && (
        <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-xl">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
          <p className="text-xs text-red-700">{errorMessage}</p>
        </div>
      )}

      {/* Process Button - macOS Style */}
      {file && status === "idle" && (
        <button
          onClick={uploadFile}
          className={cn(
            "w-full py-2.5 px-5 rounded-lg font-medium text-sm transition-all duration-150",
            "bg-blue-500 text-white shadow-sm",
            "hover:bg-blue-600 active:bg-blue-700 active:scale-[0.99]"
          )}
        >
          Procesar archivo
        </button>
      )}

      {/* Download Section - Success State */}
      {status === "success" && processedFile && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-green-600" />
            <p className="text-sm font-medium text-green-800">Archivo procesado</p>
          </div>

          <a
            href={processedFile.downloadUrl}
            download={processedFile.name}
            className={cn(
              "flex items-center justify-center gap-2 w-full py-2.5 px-5 rounded-lg",
              "bg-green-600 text-white font-medium text-sm shadow-sm",
              "hover:bg-green-700 transition-all duration-150 active:scale-[0.99]"
            )}
          >
            <Download className="w-4 h-4" />
            Descargar
          </a>

          <button
            onClick={removeFile}
            className="w-full py-2 text-xs text-neutral-500 hover:text-neutral-700 transition-colors"
          >
            Procesar otro archivo
          </button>
        </div>
      )}
    </div>
  )
}
