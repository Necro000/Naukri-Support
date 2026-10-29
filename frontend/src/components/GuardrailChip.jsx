const FLAG_META = {
  pii_masked: {
    icon: '🔒',
    label: 'PII masked',
    detail: 'I hid the phone number for your privacy.',
    style:
      'bg-sky-100 text-sky-900 border-sky-200 dark:bg-sky-950/70 dark:text-sky-200 dark:border-sky-800',
  },
  injection_blocked: {
    icon: '🛡️',
    label: 'Injection blocked',
    detail: "I can't help with that request, but I'm happy to answer hiring-policy questions.",
    style:
      'bg-rose-100 text-rose-900 border-rose-200 dark:bg-rose-950/70 dark:text-rose-200 dark:border-rose-800',
  },
  ungrounded: {
    icon: '❓',
    label: 'Not in policies',
    detail: "I couldn't find that in our hiring policies. Want me to flag it for the support team?",
    style:
      'bg-amber-100 text-amber-900 border-amber-200 dark:bg-amber-950/70 dark:text-amber-200 dark:border-amber-800',
  },
}

export function GuardrailChip({ flag }) {
  const meta = FLAG_META[flag] || {
    icon: '⚠️',
    label: flag,
    detail: flag,
    style:
      'bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:border-slate-700',
  }

  return (
    <span
      title={meta.detail}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${meta.style}`}
    >
      <span aria-hidden="true">{meta.icon}</span>
      <span>{meta.label}</span>
    </span>
  )
}
