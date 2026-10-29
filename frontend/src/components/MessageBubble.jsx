import { RouteBadge } from './RouteBadge'
import { GuardrailChip } from './GuardrailChip'
import { SourceList } from './SourceList'
import { StatusCard } from './StatusCard'
import { TraceFooter } from './TraceFooter'

export function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex flex-col items-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-indigo-600 px-4 py-2.5 text-sm text-white shadow-xs dark:bg-indigo-500">
          <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
        </div>
        <span className="mt-1 px-1 text-[11px] text-slate-400 dark:text-slate-500">
          You · {message.timestamp}
        </span>
      </div>
    )
  }

  const friendlyOverride = message.guardrailFlags?.includes('injection_blocked')
    ? "I can't help with that request, but I'm happy to answer hiring-policy questions."
    : !message.grounded && message.guardrailFlags?.includes('ungrounded')
    ? "I couldn't find that in our hiring policies. Want me to flag it for the support team?"
    : null

  return (
    <div className="flex flex-col items-start">
      <div className="w-full max-w-[92%] rounded-2xl rounded-bl-sm border border-slate-200 bg-white p-4 text-sm text-slate-900 shadow-xs dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100">
        <div className="mb-2.5 flex flex-wrap items-center gap-2">
          <RouteBadge route={message.route} />
          {message.guardrailFlags?.map((flag) => (
            <GuardrailChip key={flag} flag={flag} />
          ))}
        </div>

        {message.guardrailFlags?.includes('pii_masked') && (
          <p className="mb-2 rounded-lg bg-sky-50 px-3 py-1.5 text-xs text-sky-800 dark:bg-sky-950/50 dark:text-sky-200">
            🔒 I hid the phone number for your privacy before processing and logging.
          </p>
        )}

        <p className="whitespace-pre-wrap leading-relaxed text-slate-800 dark:text-slate-100">
          {message.text}
        </p>

        {friendlyOverride && (
          <p className="mt-1.5 text-xs italic text-slate-500 dark:text-slate-400">
            {friendlyOverride}
          </p>
        )}

        <SourceList sources={message.sources} />
        <StatusCard result={message.toolResult} />
        <TraceFooter
          traceId={message.traceId}
          latencyMs={message.latencyMs}
          confidence={message.confidence}
        />
      </div>
      <span className="mt-1 px-1 text-[11px] text-slate-400 dark:text-slate-500">
        Naukri Support · {message.timestamp}
      </span>
    </div>
  )
}
