"use client"
import { useEffect } from "react"

export default function ArchivePage() {
  useEffect(() => {
    window.location.href = "https://kloud.com/modules/archive"
  }, [])
  
  return (
    <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
      <p>Loading...</p>
    </div>
  )
}

