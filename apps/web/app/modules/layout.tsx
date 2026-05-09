/**
 * Kloud Modules Layout
 * Advanced neuroacoustic processing, EEG analysis, and industrial monitoring
 */

import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Kloud Modules - Advanced Neural Processing',
  description: 'Industrial-grade EEG analysis, neuroacoustic conversion, biofeedback training, and spectrum analysis',
}

export default function ModulesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  )
}









