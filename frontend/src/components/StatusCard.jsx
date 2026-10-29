import { EscalationMeter } from './EscalationMeter'

const STATUS_STYLES = {
  Applied: 'bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200',
  Screening: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200',
  'Interview Scheduled': 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200',
  Offered: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
  Rejected: 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200',
}

export function StatusCard({ result }) {
  if (!result) return null

  if (result.error) {
    return (
      <div className="mt-3 rounded-2xl border border-amber-200 bg-amber-50/70 p-3.5 text-xs text-amber-900 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200">
        <p className="font-semibold">Application Lookup Note</p>
        <p className="mt-1">
          I can&apos;t find that application ID. Could you double-check it? ({result.error})
        </p>
      </div>
    )
  }

  const badgeStyle =
    STATUS_STYLES[result.status] ||
    'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200'

  const formattedSalary = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(result.expected_salary_inr || 0)

  return (
    <div className="mt-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-700/80 dark:bg-slate-900">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-indigo-600 dark:text-indigo-400">
            {result.record_id}
          </span>
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
            · {result.category}
          </span>
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badgeStyle}`}>
          {result.status}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/60">
          <span className="block text-slate-500 dark:text-slate-400">Expected Salary</span>
          <span className="mt-0.5 block font-semibold text-slate-900 dark:text-slate-100">
            {formattedSalary}/yr
          </span>
        </div>
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/60">
          <span className="block text-slate-500 dark:text-slate-400">Application Age</span>
          <span className="mt-0.5 block font-semibold text-slate-900 dark:text-slate-100">
            {result.days_since_created} days ago
          </span>
        </div>
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/60">
          <span className="block text-slate-500 dark:text-slate-400">Priority Flag</span>
          <span className="mt-0.5 block font-semibold text-slate-900 dark:text-slate-100">
            {result.flagged_priority_review ? '🚩 Flagged' : 'Standard'}
          </span>
        </div>
      </div>

      <EscalationMeter
        score={result.escalation_score}
        threshold={result.escalation_threshold ?? 0.36}
      />
    </div>
  )
}
