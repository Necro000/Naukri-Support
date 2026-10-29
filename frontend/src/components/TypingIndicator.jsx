export function TypingIndicator() {
  return (
    <div
      className="flex items-center gap-3 self-start rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-xs dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
      aria-live="polite"
    >
      <div className="flex items-center gap-1" aria-hidden="true">
        <span className="h-2 w-2 rounded-full bg-indigo-500 motion-safe:animate-bounce" />
        <span className="h-2 w-2 rounded-full bg-indigo-500 motion-safe:animate-bounce [animation-delay:150ms]" />
        <span className="h-2 w-2 rounded-full bg-indigo-500 motion-safe:animate-bounce [animation-delay:300ms]" />
      </div>
      <span>Looking that up…</span>
    </div>
  )
}
