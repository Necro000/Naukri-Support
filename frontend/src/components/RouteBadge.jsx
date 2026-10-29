export function RouteBadge({ route }) {
  if (route === 'blocked') {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-medium text-rose-800 dark:bg-rose-950/70 dark:text-rose-200 border border-rose-200 dark:border-rose-800">
        <span aria-hidden="true">🛑</span>
        <span>Blocked · Input Guard</span>
      </span>
    )
  }

  if (route === 'status') {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-900 dark:bg-amber-950/70 dark:text-amber-200 border border-amber-200 dark:border-amber-800">
        <span aria-hidden="true">🗂️</span>
        <span>Status lookup · Tool</span>
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-medium text-indigo-800 dark:bg-indigo-950/70 dark:text-indigo-200 border border-indigo-200 dark:border-indigo-800">
      <span aria-hidden="true">📘</span>
      <span>Policy · RAG</span>
    </span>
  )
}
