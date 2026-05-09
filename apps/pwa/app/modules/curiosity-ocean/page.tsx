"use client"
import { useEffect } from "react"

export default function OceanPage() {
  useEffect(() => {
    window.location.href = "https://kloud.com/modules/curiosity-ocean"
  }, [])
  
  return (
    <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
      <p>Loading...</p>
    </div>
  )
}

