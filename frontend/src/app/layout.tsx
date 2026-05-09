// Kloud Industrial Cloud Root Layout
// Author: Ledjan Ahmati
// Next.js 15 App Router - Server Component

import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Kloud Cloud - Industrial Intelligence Platform',
  description: 'Advanced Neural & Audio Intelligence Platform by Ledjan Ahmati',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <header className="bg-green-700 text-white py-4 px-8 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-black">Kloud Cloud</div>
            <nav className="flex gap-4 text-sm">
              <a href="/" className="hover:opacity-80">Home</a>
              <a href="/modules" className="hover:opacity-80">Modules</a>
            </nav>
          </div>
        </header>
        <main className="container mx-auto py-8 px-4">
          {children}
        </main>
        <footer className="bg-gray-900 border-t border-gray-700 py-4 text-center text-gray-500 text-sm">
          © 2025 Kloud Cloud by Ledjan Ahmati
        </footer>
      </body>
    </html>
  )
}

