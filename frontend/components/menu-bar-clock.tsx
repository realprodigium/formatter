"use client"

import { useState, useEffect } from "react"

export function MenuBarClock() {
  const [mounted, setMounted] = useState(false)
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    setMounted(true)
    const interval = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(interval)
  }, [])

  if (!mounted) {
    return <span className="w-32" />
  }

  return (
    <>
      <span>
        {time.toLocaleDateString("es-ES", { 
          weekday: "short", 
          day: "numeric", 
          month: "short" 
        })}
      </span>
      <span>
        {time.toLocaleTimeString("es-ES", { 
          hour: "2-digit", 
          minute: "2-digit" 
        })}
      </span>
    </>
  )
}
