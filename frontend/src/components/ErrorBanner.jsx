export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null

  return (
    <div
      role="alert"
      className="mx-4 mt-3 flex items-center justify-between gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-2.5 text-xs text-rose-900 sm:mx-6 dark:border-rose-900/70 dark:bg-rose-950/60 dark:text-rose-200"
    >
      <div className="flex items-center gap-2">
        <span aria-hidden="true">⚠️</span>
        <span>
          <strong>Something went wrong on our side.</strong> Please try again in a moment. ({message})
        </span>
      </div>
      <button
        type="button"
        onClick={onDismiss}
        className="rounded-lg px-2 py-1 font-semibold hover:bg-rose-100 focus:outline-2 focus:outline-rose-500 dark:hover:bg-rose-900/50"
      >
        Dismiss
      </button>
    </div>
  )
}
