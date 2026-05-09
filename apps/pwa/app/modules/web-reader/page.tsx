"use client"
import { useEffect } from "react"

export default function ReaderPage() {
  useEffect(() => {
    window.location.href = "https://kloud.com/modules/web-reader"
  }, [])
  
  return (
    <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
      <p>Loading...</p>
    </div>
  )
}

