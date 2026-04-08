"use client"

import { ReactNode } from "react"

interface MacOSWindowProps {
  title: string
  children: ReactNode
}

export function MacOSWindow({ title, children }: MacOSWindowProps) {
  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Window Container */}
      <div className="rounded-xl overflow-hidden shadow-2xl shadow-black/20 border border-neutral-200/50">
        {/* Title Bar */}
        <div className="bg-neutral-100 border-b border-neutral-200/80 px-3 py-2 flex items-center gap-2.5">
          {/* Traffic Lights - Monochrome */}
          <div className="flex items-center gap-1.5">
            <button 
              className="w-2.5 h-2.5 rounded-full bg-neutral-400 hover:bg-neutral-500 transition-all"
              aria-label="Cerrar"
            />
            <button 
              className="w-2.5 h-2.5 rounded-full bg-neutral-400 hover:bg-neutral-500 transition-all"
              aria-label="Minimizar"
            />
            <button 
              className="w-2.5 h-2.5 rounded-full bg-neutral-400 hover:bg-neutral-500 transition-all"
              aria-label="Maximizar"
            />
          </div>
          
          {/* Window Title */}
          <div className="flex-1 text-center">
            <span className="text-[11px] font-medium text-neutral-500">{title}</span>
          </div>
          
          {/* Spacer for centering */}
          <div className="w-10" />
        </div>
        
        {/* Window Content */}
        <div className="bg-white/95 backdrop-blur-xl">
          {children}
        </div>
      </div>
    </div>
  )
}
