import Link from 'next/link'

const modules = [
  { name: 'Ocean', href: '/modules/curiosity-ocean', icon: '🌊', desc: 'AI Chat' },
  { name: 'Reader', href: '/modules/web-reader', icon: '📖', desc: 'Web Reader' },
  { name: 'Archive', href: '/modules/archive', icon: '📚', desc: 'Saved' },
]

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 p-4">
      <h1 className="text-2xl text-white text-center py-6">Kloud</h1>
      <div className="space-y-3 max-w-md mx-auto">
        {modules.map(m => (
          <Link key={m.name} href={m.href} className="block bg-slate-800 rounded-xl p-4">
            <span className="text-3xl mr-3">{m.icon}</span>
            <span className="text-white font-medium">{m.name}</span>
            <span className="text-slate-400 text-sm ml-2">{m.desc}</span>
          </Link>
        ))}
      </div>
    </main>
  )
}

