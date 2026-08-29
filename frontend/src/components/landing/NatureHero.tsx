'use client'

import { useEffect, useMemo, useState } from 'react'

type Slide = {
  src: string
  alt: string
}

const slides: Slide[] = [
  {
    // Nature images from web (Unsplash Source)
    src: 'https://source.unsplash.com/1600x900/?forest,mist',
    alt: 'Forest mist'
  },
  {
    src: 'https://source.unsplash.com/1600x900/?mountains,river',
    alt: 'Mountains and river'
  },
  {
    src: 'https://source.unsplash.com/1600x900/?ocean,clouds',
    alt: 'Ocean and clouds'
  },
  {
    src: 'https://source.unsplash.com/1600x900/?rainforest,leaves',
    alt: 'Rainforest leaves'
  }
]

export default function NatureHero() {
  const [index, setIndex] = useState(0)

  const orderedSlides = useMemo(() => slides, [])

  useEffect(() => {
    const t = setInterval(() => setIndex((i) => (i + 1) % orderedSlides.length), 5000)
    return () => clearInterval(t)
  }, [orderedSlides.length])

  const current = orderedSlides[index]

  return (
    <section className="relative overflow-hidden rounded-2xl border border-white/10">
      {/* Background image */}
      <div className="absolute inset-0">
        <img
          key={current.src}
          src={current.src}
          alt={current.alt}
          className="h-full w-full object-cover opacity-70 transition-opacity duration-700"
        />
        {/* Overlay gradients for readability */}
        <div className="absolute inset-0 bg-gradient-to-br from-black/70 via-black/40 to-black/60" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.35),transparent_40%),radial-gradient(circle_at_80%_30%,rgba(168,85,247,0.25),transparent_45%)]" />
      </div>

      {/* Content */}
      <div className="relative px-6 py-14 md:px-10 md:py-20">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-white/90">
            <span aria-hidden>🌿</span>
            <span>Nature-inspired intelligence UI</span>
            <span className="text-white/60">•</span>
            <span className="text-white/70">Live services</span>
          </div>

          <h1 className="mt-5 text-4xl font-extrabold leading-tight md:text-6xl">
            Kloud Cloud
            <span className="block bg-gradient-to-r from-blue-300 via-purple-300 to-emerald-200 bg-clip-text text-transparent">
              Advanced Neural & Audio Intelligence
            </span>
          </h1>

          <p className="mt-5 text-base leading-relaxed text-white/80 md:text-lg">
            Një UI e qartë dhe moderne për përdoruesit: shërbime të dukshme, status live dhe
            një përvojë vizuale që frymëzon — me dinamika nga natyra.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <a
              href="/modules"
              className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:bg-blue-500"
            >
              Open Modules
            </a>
            <a
              href="#live"
              className="inline-flex items-center justify-center rounded-xl border border-white/20 bg-white/5 px-5 py-3 text-sm font-semibold text-white/90 transition hover:bg-white/10"
            >
              View Live Services
            </a>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-2xl font-bold text-blue-200">Real-time</div>
              <div className="mt-1 text-sm text-white/70">Health & metrics</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-2xl font-bold text-purple-200">Clear</div>
              <div className="mt-1 text-sm text-white/70">For clients & users</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-2xl font-bold text-emerald-200">Dynamic</div>
              <div className="mt-1 text-sm text-white/70">Nature-inspired UI</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
