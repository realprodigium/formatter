import { FileUploader } from "@/components/file-uploader"
import { MacOSWindow } from "@/components/macos-window"
import { MenuBarClock } from "@/components/menu-bar-clock"

export default function Home() {
  const API_ENDPOINT = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/process"

  return (
    <main className="min-h-screen bg-gradient-to-br from-neutral-200 via-neutral-300 to-neutral-400 p-4 md:p-6 flex flex-col">
      {/* macOS Menu Bar */}
      <div className="fixed top-0 left-0 right-0 h-6 bg-neutral-100/90 backdrop-blur-md border-b border-neutral-300/50 flex items-center px-4 z-50">
        <div className="flex items-center gap-4 text-[12px] font-medium text-neutral-700">
          <svg className="w-3.5 h-3.5" viewBox="0 0 17 21" fill="currentColor">
            <path d="M15.5 14.2c-.4 1-1 2-1.6 2.8-.9 1.2-1.8 2.4-3.2 2.4-1.4.1-1.9-.8-3.5-.8-1.6 0-2.2.8-3.5.9-1.4.1-2.4-1.3-3.3-2.5-1.9-2.5-3.3-7-1.4-10.1.9-1.5 2.6-2.5 4.4-2.5 1.4 0 2.6.9 3.5.9.9 0 2.4-1.1 4.1-.9.7 0 2.6.3 3.9 2.1-3.1 1.9-2.6 6.6.6 7.7zm-4-15.2c.7-.9 1.2-2.1 1.1-3.3-1.1 0-2.4.7-3.1 1.6-.7.8-1.3 2-1.1 3.2 1.2.1 2.4-.6 3.1-1.5z"/>
          </svg>
          <span className="font-semibold">Conciliador</span>
          <span className="text-neutral-500">Archivo</span>
          <span className="text-neutral-500">Editar</span>
          <span className="text-neutral-500">Ayuda</span>
        </div>
        <div className="ml-auto text-[12px] text-neutral-600">
          <MenuBarClock />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center pt-8">
        <MacOSWindow title="Conciliador XLSX">
          <div className="flex min-h-[380px]">
            {/* Sidebar */}
            <div className="w-40 bg-neutral-100/60 border-r border-neutral-200/80 p-2 hidden md:block">
              <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider px-2 mb-1.5">
                Acciones
              </p>
              <div className="space-y-0.5">
                <div className="flex items-center gap-2 px-2 py-1 bg-neutral-900 rounded">
                  <svg className="w-3.5 h-3.5 text-neutral-100" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                  <span className="text-[11px] text-neutral-100 font-medium">Subir</span>
                </div>
                <div className="flex items-center gap-2 px-2 py-1 hover:bg-neutral-200/50 rounded transition-colors cursor-pointer">
                  <svg className="w-3.5 h-3.5 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-[11px] text-neutral-600">Recientes</span>
                </div>
              </div>
              
              <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider px-2 mt-4 mb-1.5">
                Info
              </p>
              <div className="px-2 text-[10px] text-neutral-500 space-y-1">
                <p>.xlsx, .xls</p>
                <p>Max 10MB</p>
              </div>
            </div>

            {/* Main Area */}
            <div className="flex-1 flex flex-col bg-white">
              <div className="flex-1 p-3">
                <FileUploader 
                  apiEndpoint={API_ENDPOINT}
                  acceptedFileTypes=".xlsx,.xls"
                  maxFileSize={10}
                />
              </div>

              <div className="px-3 py-1.5 border-t border-neutral-100 bg-neutral-50/50">
                <p className="text-[10px] text-neutral-400 text-center">
                  Los archivos se procesan de forma segura
                </p>
              </div>
            </div>
          </div>
        </MacOSWindow>
      </div>
    </main>
  )
}
