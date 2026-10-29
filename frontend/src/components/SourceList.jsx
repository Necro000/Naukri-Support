export function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
      <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Sources:</span>
      {sources.map((src) => (
        <span
          key={src}
          className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-mono text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
        >
          <span aria-hidden="true">📄</span>
          {src}
        </span>
      ))}
    </div>
  )
}
