// Kloud Modules Industrial Dashboard
// Author: Ledjan Ahmati

import React from 'react'

const modules = [
  {
    name: 'Neuroacoustic Converter',
    path: '/modules/neuroacoustic-converter',
    description: 'Konverton sinjale neuroakustike industriale me log, audit, metrika.'
  },
  {
    name: 'Neural Synthesis',
    path: '/modules/neural-synthesis',
    description: 'Sintetizon tÃ« dhÃ«na neurale nÃ« audio industriale me log, audit, metrika.'
  },
  {
    name: 'EEG Analysis',
    path: '/modules/eeg-analysis',
    description: 'Analizon sinjale EEG industriale, detekton evente, log, audit, metrika.'
  },
  {
    name: 'Spectrum Analyzer',
    path: '/modules/spectrum-analyzer',
    description: 'Analizues spektral industrial me log, audit, metrika.'
  }
]

export default function ModulesDashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Kloud Modules Industrial Dashboard</h1>
      <div className="grid grid-cols-2 gap-6">
        {modules.map((mod, i) => (
          <a key={i} href={mod.path} className="block p-6 bg-gray-100 rounded-lg shadow hover:bg-gray-200 transition">
            <h2 className="text-xl font-semibold mb-2">{mod.name}</h2>
            <p className="mb-2 text-sm text-muted-foreground">{mod.description}</p>
            <div className="text-xs text-muted-foreground">Industrial | Log | Audit | Metrika</div>
          </a>
        ))}
      </div>
      <div className="mt-8 text-xs text-muted-foreground">
        Â© 2025 Kloud Industrial Cloud. All modules are protected, audited, and monitored for industrial compliance.
      </div>
    </div>
  )
}

