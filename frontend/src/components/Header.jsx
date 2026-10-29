export function Header({
  health,
  conversationId,
  theme,
  onToggleTheme,
  onNewChat,
  onToggleMobilePanel,
}) {
  const isHealthy = health?.status === 'ok'

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3 sm:px-6 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center gap-3">
        <div
          aria-hidden="true"
          className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 font-bold text-white shadow-xs"
        >
          N
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight text-slate-900 dark:text-white">
              Naukri Support
            </h1>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                isHealthy
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-200'
                  : 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-200'
              }`}
            >
              <span
                aria-hidden="true"
                className={`h-2 w-2 rounded-full ${
                  isHealthy ? 'bg-emerald-500' : 'bg-rose-500'
                }`}
              />
              <span>{isHealthy ? 'API Online · MOCK_LLM' : 'API Offline'}</span>
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Track: Recruitment &amp; HR · Session:{' '}
            <code className="font-mono text-slate-700 dark:text-slate-300">{conversationId}</code>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          id="new-chat-btn"
          type="button"
          onClick={onNewChat}
          className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 focus:outline-2 focus:outline-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          + New chat
        </button>

        <button
          id="theme-toggle-btn"
          type="button"
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          aria-pressed={theme === 'dark'}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 focus:outline-2 focus:outline-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          <span aria-hidden="true">{theme === 'dark' ? '☀️' : '🌙'}</span>
          <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>

        <button
          id="mobile-sidebar-btn"
          type="button"
          onClick={onToggleMobilePanel}
          className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 lg:hidden dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
        >
          Tools &amp; KB
        </button>
      </div>
    </header>
  )
}
