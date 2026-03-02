'use client'

import { FormEvent, useEffect, useState } from 'react'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

type ToolsStatus = {
  checks?: Record<string, { status?: string; url?: string; error?: string }>
}

type MemoryItem = {
  id: string
  text: string
  tags?: string[]
  source?: string
}

type TaskItem = {
  id: string
  title: string
  objective: string
  status: string
  result?: string | null
}

const OPENMIND_PROXY = '/api/openmind'

export default function OpenMindPage() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [statusPayload, setStatusPayload] = useState<ToolsStatus | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'OpenMind is ready. Ask me anything, then scale to memory, tasks, music, vision, and workflows.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const [memoryText, setMemoryText] = useState('')
  const [memoryTags, setMemoryTags] = useState('')
  const [memoryResults, setMemoryResults] = useState<MemoryItem[]>([])
  const [memoryQuery, setMemoryQuery] = useState('')

  const [taskTitle, setTaskTitle] = useState('')
  const [taskObjective, setTaskObjective] = useState('')
  const [tasks, setTasks] = useState<TaskItem[]>([])

  const [musicNotes, setMusicNotes] = useState('do,re,mi,fa,sol,la,si')
  const [musicWaveform, setMusicWaveform] = useState('sine')
  const [musicFormat, setMusicFormat] = useState('wav')
  const [musicResult, setMusicResult] = useState('')

  const [visionPrompt, setVisionPrompt] = useState('Create a futuristic OpenMind visual dashboard')
  const [visionImageBase64, setVisionImageBase64] = useState('')
  const [visionFile, setVisionFile] = useState('')

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${OPENMIND_PROXY}/tools/status`)
        if (!res.ok) {
          setStatus('offline')
          return
        }
        const data = (await res.json()) as ToolsStatus
        setStatusPayload(data)
        setStatus('online')
      } catch {
        setStatus('offline')
      }
    }

    checkStatus()
    void loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const res = await fetch(`${OPENMIND_PROXY}/tasks`)
      if (!res.ok) return
      const data = (await res.json()) as { tasks?: TaskItem[] }
      setTasks(data.tasks ?? [])
    } catch {
      setTasks([])
    }
  }

  const sendMessage = async (event: FormEvent) => {
    event.preventDefault()
    if (!input.trim() || loading) return

    const userText = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userText }])
    setLoading(true)

    try {
      const res = await fetch(`${OPENMIND_PROXY}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, query: userText }),
      })

      const data = (await res.json()) as { response?: string; detail?: string }
      const reply = data.response || data.detail || 'No response received from OpenMind.'
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'OpenMind connection failed. Verify engine `9999/app.py` is running.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const storeMemory = async (event: FormEvent) => {
    event.preventDefault()
    if (!memoryText.trim()) return
    const tags = memoryTags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)

    const res = await fetch(`${OPENMIND_PROXY}/memory/store`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: memoryText.trim(), tags, source: 'openmind-frontend' }),
    })

    if (res.ok) {
      setMemoryText('')
      const data = (await res.json()) as { memory?: MemoryItem }
      if (data.memory) {
        setMemoryResults((prev) => [data.memory as MemoryItem, ...prev].slice(0, 10))
      }
    }
  }

  const searchMemory = async (event: FormEvent) => {
    event.preventDefault()
    if (!memoryQuery.trim()) return
    const res = await fetch(`${OPENMIND_PROXY}/memory/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: memoryQuery.trim(), limit: 8 }),
    })
    if (!res.ok) return
    const data = (await res.json()) as { results?: MemoryItem[] }
    setMemoryResults(data.results ?? [])
  }

  const createTask = async (event: FormEvent) => {
    event.preventDefault()
    if (!taskTitle.trim() || !taskObjective.trim()) return
    const res = await fetch(`${OPENMIND_PROXY}/tasks/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: taskTitle.trim(),
        objective: taskObjective.trim(),
        priority: 'normal',
        input_data: {},
      }),
    })
    if (!res.ok) return
    setTaskTitle('')
    setTaskObjective('')
    await loadTasks()
  }

  const runTask = async (taskId: string) => {
    const res = await fetch(`${OPENMIND_PROXY}/tasks/${taskId}/run`, { method: 'POST' })
    if (!res.ok) return
    await loadTasks()
  }

  const createMusic = async (event: FormEvent) => {
    event.preventDefault()
    const notes = musicNotes
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    if (!notes.length) return

    const res = await fetch(`${OPENMIND_PROXY}/music/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notes,
        waveform: musicWaveform,
        output_format: musicFormat,
      }),
    })
    if (!res.ok) return
    const data = (await res.json()) as { file?: string }
    setMusicResult(data.file ?? 'Music generated successfully.')
  }

  const createVision = async (event: FormEvent) => {
    event.preventDefault()
    if (!visionPrompt.trim()) return
    const res = await fetch(`${OPENMIND_PROXY}/vision/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: visionPrompt.trim(), width: 640, height: 384 }),
    })
    if (!res.ok) return
    const data = (await res.json()) as { image_base64?: string; image_file?: string }
    setVisionImageBase64(data.image_base64 ?? '')
    setVisionFile(data.image_file ?? '')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-900 text-white">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-6 rounded-xl border border-white/15 bg-black/25 p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold">OpenMind</h1>
              <p className="mt-1 text-sm text-slate-300">
                Dynamic general AI module connected to the `9999` engine.
              </p>
            </div>
            <div
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                status === 'online'
                  ? 'bg-emerald-500/20 text-emerald-300'
                  : status === 'offline'
                    ? 'bg-red-500/20 text-red-300'
                    : 'bg-yellow-500/20 text-yellow-300'
              }`}
            >
              {status === 'online' ? '● Online' : status === 'offline' ? '● Offline' : '● Checking'}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="rounded-xl border border-white/15 bg-black/25 p-4 lg:col-span-1">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">Engine Checks</h2>
            <div className="space-y-2 text-xs">
              {statusPayload?.checks ? (
                Object.entries(statusPayload.checks).map(([key, value]) => (
                  <div key={key} className="rounded-md border border-white/10 bg-white/5 p-2">
                    <div className="font-medium">{key}</div>
                    <div className="text-slate-300">status: {value.status ?? 'unknown'}</div>
                  </div>
                ))
              ) : (
                <div className="rounded-md border border-white/10 bg-white/5 p-2 text-slate-300">
                  No check data yet.
                </div>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-white/15 bg-black/25 p-4 lg:col-span-2">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">OpenMind Chat</h2>
            <div className="mb-4 h-[420px] space-y-3 overflow-y-auto rounded-lg border border-white/10 bg-black/30 p-3">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`max-w-[88%] rounded-lg px-3 py-2 text-sm ${
                    message.role === 'user'
                      ? 'ml-auto border border-indigo-400/40 bg-indigo-500/20'
                      : 'border border-white/10 bg-white/5'
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage} className="flex gap-2">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask OpenMind anything..."
                className="flex-1 rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none ring-indigo-400/40 focus:ring"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-white/15 bg-black/25 p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-200">Memory</h3>
            <form onSubmit={storeMemory} className="space-y-2">
              <textarea
                value={memoryText}
                onChange={(event) => setMemoryText(event.target.value)}
                placeholder="Store memory text..."
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
                rows={3}
              />
              <input
                value={memoryTags}
                onChange={(event) => setMemoryTags(event.target.value)}
                placeholder="tags: ai, research, note"
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
              />
              <button className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-medium">Store Memory</button>
            </form>

            <form onSubmit={searchMemory} className="mt-3 flex gap-2">
              <input
                value={memoryQuery}
                onChange={(event) => setMemoryQuery(event.target.value)}
                placeholder="Search memory..."
                className="flex-1 rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
              />
              <button className="rounded-lg border border-white/20 px-3 py-2 text-xs">Search</button>
            </form>

            <div className="mt-3 max-h-48 space-y-2 overflow-y-auto text-xs">
              {memoryResults.map((item) => (
                <div key={item.id} className="rounded-md border border-white/10 bg-white/5 p-2">
                  <div className="text-slate-100">{item.text}</div>
                  <div className="mt-1 text-slate-400">#{(item.tags ?? []).join(' #')}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-white/15 bg-black/25 p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-200">Task Engine</h3>
            <form onSubmit={createTask} className="space-y-2">
              <input
                value={taskTitle}
                onChange={(event) => setTaskTitle(event.target.value)}
                placeholder="Task title"
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
              />
              <textarea
                value={taskObjective}
                onChange={(event) => setTaskObjective(event.target.value)}
                placeholder="Task objective"
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
                rows={2}
              />
              <button className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-medium">Create Task</button>
            </form>

            <div className="mt-3 max-h-48 space-y-2 overflow-y-auto text-xs">
              {tasks.map((task) => (
                <div key={task.id} className="rounded-md border border-white/10 bg-white/5 p-2">
                  <div className="font-medium">{task.title}</div>
                  <div className="text-slate-300">{task.status}</div>
                  {task.result ? <div className="mt-1 text-slate-400">{task.result}</div> : null}
                  <button
                    onClick={() => runTask(task.id)}
                    className="mt-2 rounded-md border border-white/20 px-2 py-1 text-[11px]"
                    type="button"
                  >
                    Run
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-white/15 bg-black/25 p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-200">Music Studio</h3>
            <form onSubmit={createMusic} className="space-y-2">
              <input
                value={musicNotes}
                onChange={(event) => setMusicNotes(event.target.value)}
                placeholder="do,re,mi,fa,sol"
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
              />
              <div className="grid grid-cols-2 gap-2">
                <select
                  value={musicWaveform}
                  onChange={(event) => setMusicWaveform(event.target.value)}
                  className="rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm"
                >
                  <option value="sine">sine</option>
                  <option value="square">square</option>
                  <option value="sawtooth">sawtooth</option>
                  <option value="triangle">triangle</option>
                  <option value="bass">bass</option>
                  <option value="organ">organ</option>
                  <option value="piano">piano</option>
                </select>
                <select
                  value={musicFormat}
                  onChange={(event) => setMusicFormat(event.target.value)}
                  className="rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm"
                >
                  <option value="wav">wav</option>
                  <option value="mp3">mp3</option>
                </select>
              </div>
              <button className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-medium">Create Music</button>
            </form>
            {musicResult ? (
              <div className="mt-3 rounded-md border border-white/10 bg-white/5 p-2 text-xs text-slate-300">
                {musicResult}
              </div>
            ) : null}
          </div>

          <div className="rounded-xl border border-white/15 bg-black/25 p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-200">Vision Creator</h3>
            <form onSubmit={createVision} className="space-y-2">
              <input
                value={visionPrompt}
                onChange={(event) => setVisionPrompt(event.target.value)}
                placeholder="Describe the image"
                className="w-full rounded-lg border border-white/20 bg-black/40 px-3 py-2 text-sm outline-none"
              />
              <button className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-medium">Create Image</button>
            </form>
            {visionFile ? <div className="mt-2 text-xs text-slate-400">{visionFile}</div> : null}
            {visionImageBase64 ? (
              <img
                alt="OpenMind Vision Output"
                className="mt-3 w-full rounded-lg border border-white/10"
                src={`data:image/png;base64,${visionImageBase64}`}
              />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
