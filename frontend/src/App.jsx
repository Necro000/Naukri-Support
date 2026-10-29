import { useState, useEffect, useCallback } from 'react'
import { checkHealth } from './api'
import { useChat } from './hooks/useChat'
import { Header } from './components/Header'
import { ChatWindow } from './components/ChatWindow'
import { Composer } from './components/Composer'
import { AddDocPanel } from './components/AddDocPanel'
import { ErrorBanner } from './components/ErrorBanner'

function getSystemScheme() {
  if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  return 'light'
}

function getResolvedTheme() {
  try {
    const stored = localStorage.getItem('color-scheme')
    if (stored === 'dark' || stored === 'light') return stored
  } catch {
    // ignore storage failure
  }
  return getSystemScheme()
}

function applyColorSchemeMeta(storedValue) {
  const meta = document.querySelector('meta[name="color-scheme"]')
  if (meta) {
    meta.content = storedValue ?? 'light dark'
  }
  const effective = storedValue ?? getSystemScheme()
  document.documentElement.classList.toggle('dark', effective === 'dark')
}

const SAMPLE_APPS = [
  { id: 'APP-0002', desc: 'HR Executive · Flagged · 17d (Escalate)' },
  { id: 'APP-0008', desc: 'Sales Associate · Unflagged · 29d (Aged SLA Escalate)' },
  { id: 'APP-0006', desc: 'HR Executive · Unflagged · 6d (Normal SLA)' },
  { id: 'APP-0001', desc: 'Product Manager · Unflagged · 7d (Normal SLA)' },
]

export function App() {
  const [theme, setTheme] = useState(getResolvedTheme)
  const [health, setHealth] = useState(null)
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)

  const {
    conversationId,
    messages,
    loading,
    error,
    resetNotice,
    setError,
    sendMessage,
    startNewChat,
  } = useChat()

  const refreshHealth = useCallback(async () => {
    try {
      const data = await checkHealth()
      setHealth(data)
    } catch {
      setHealth(null)
    }
  }, [])

  useEffect(() => {
    refreshHealth()
  }, [refreshHealth])

  useEffect(() => {
    const handleStorage = (e) => {
      if (e.key === 'color-scheme') {
        const nextVal = e.newValue === 'dark' || e.newValue === 'light' ? e.newValue : null
        applyColorSchemeMeta(nextVal)
        setTheme(nextVal ?? getSystemScheme())
      }
    }
    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [])

  const handleToggleTheme = () => {
    const target = theme === 'dark' ? 'light' : 'dark'
    const systemPref = getSystemScheme()
    try {
      if (target === systemPref) {
        localStorage.removeItem('color-scheme')
        applyColorSchemeMeta(null)
      } else {
        localStorage.setItem('color-scheme', target)
        applyColorSchemeMeta(target)
      }
    } catch {
      applyColorSchemeMeta(target)
    }
    setTheme(target)
  }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <Header
        health={health}
        conversationId={conversationId}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        onNewChat={startNewChat}
        onToggleMobilePanel={() => setMobileDrawerOpen((v) => !v)}
      />

      <div className="relative flex flex-1 overflow-hidden">
        <main className="flex flex-1 flex-col overflow-hidden">
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
          <ChatWindow
            messages={messages}
            loading={loading}
            resetNotice={resetNotice}
            onPickPrompt={sendMessage}
          />
          <Composer onSend={sendMessage} disabled={loading} />
        </main>

        <aside
          aria-label="Knowledge base and sample records"
          className={`${
            mobileDrawerOpen ? 'fixed inset-y-0 right-0 z-30 flex w-80' : 'hidden'
          } lg:static lg:flex lg:w-88 shrink-0 flex-col gap-4 overflow-y-auto border-l border-slate-200 bg-slate-100/70 p-4 dark:border-slate-800 dark:bg-slate-900/60`}
        >
          {mobileDrawerOpen && (
            <div className="flex items-center justify-between lg:hidden">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Workspace Tools
              </span>
              <button
                type="button"
                onClick={() => setMobileDrawerOpen(false)}
                className="rounded-lg px-2 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                Close ✕
              </button>
            </div>
          )}

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Sample Applications (Dataset)
            </h3>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
              Click any seeded record ID (<code className="font-mono">SEED=42</code>) to inspect its
              status and escalation meter:
            </p>
            <div className="mt-2.5 space-y-1.5">
              {SAMPLE_APPS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  disabled={loading}
                  onClick={() => {
                    sendMessage(`What is the status of ${item.id}?`)
                    setMobileDrawerOpen(false)
                  }}
                  className="flex w-full items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50 px-3 py-2 text-left text-xs transition hover:border-indigo-300 hover:bg-indigo-50/70 focus:outline-2 focus:outline-indigo-500 disabled:opacity-50 dark:border-slate-700/80 dark:bg-slate-800/60 dark:hover:border-indigo-700 dark:hover:bg-indigo-950/50"
                >
                  <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                    {item.id}
                  </span>
                  <span className="truncate pl-2 text-[11px] text-slate-500 dark:text-slate-400">
                    {item.desc}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <AddDocPanel onDocumentAdded={refreshHealth} />

          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-600 shadow-xs dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
            <h3 className="font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              System Telemetry
            </h3>
            <dl className="mt-2 space-y-1.5">
              <div className="flex justify-between">
                <dt>Active Collection</dt>
                <dd className="font-mono font-semibold text-slate-900 dark:text-slate-200">
                  kb_sentence ({health?.collections?.kb_sentence ?? 24} chunks)
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Fixed Collection</dt>
                <dd className="font-mono font-semibold text-slate-900 dark:text-slate-200">
                  kb_fixed ({health?.collections?.kb_fixed ?? 48} chunks)
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Grounded Threshold</dt>
                <dd className="font-mono font-semibold text-slate-900 dark:text-slate-200">
                  0.4296 (cosine)
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Escalation Threshold</dt>
                <dd className="font-mono font-semibold text-slate-900 dark:text-slate-200">
                  0.3600 (p80)
                </dd>
              </div>
            </dl>
          </div>
        </aside>
      </div>
    </div>
  )
}
