export function EscalationMeter({ score = 0, threshold = 0.36 }) {
  const pct = Math.min(100, Math.max(0, Math.round(score * 100)))
  const threshPct = Math.min(100, Math.max(0, Math.round(threshold * 100)))
  const isEscalated = score >= threshold

  return (
    <div className="mt-3 rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700">
      <div className="flex items-center justify-between text-xs font-medium">
        <span className="text-slate-600 dark:text-slate-300">
          Escalation Score:{' '}
          <strong className="font-mono text-slate-900 dark:text-white">
            {Number(score).toFixed(4)}
          </strong>{' '}
          <span className="text-slate-400">(threshold {Number(threshold).toFixed(2)})</span>
        </span>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
            isEscalated
              ? 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200'
              : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200'
          }`}
        >
          <span aria-hidden="true">{isEscalated ? '⚡' : '✓'}</span>
          {isEscalated ? 'Escalate Recommended' : 'Within Normal SLA'}
        </span>
      </div>

      <div
        className="relative mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Application escalation score"
      >
        <div
          className={`h-full rounded-full transition-all duration-200 ${
            isEscalated ? 'bg-amber-500 dark:bg-amber-400' : 'bg-emerald-500 dark:bg-emerald-400'
          }`}
          style={{ width: `${pct}%` }}
        />
        <div
          title={`Escalation Threshold (${threshold})`}
          className="absolute top-0 bottom-0 w-0.5 bg-slate-900 dark:bg-white"
          style={{ left: `${threshPct}%` }}
        />
      </div>
    </div>
  )
}
