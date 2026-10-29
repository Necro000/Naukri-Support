import { useState } from 'react'

export function TraceFooter({ traceId, latencyMs, confidence }) {
  const [copied, setCopied] = useState(false)

  if (!traceId) return null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(traceId)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // ignore clipboard errors
    }
  }

  return (
    <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-2 text-[11px] text-slate-400 dark:border-slate-800 dark:text-slate-500">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 font-mono hover:bg-slate-100 hover:text-slate-600 focus:outline-2 focus:outline-indigo-500 dark:hover:bg-slate-800 dark:hover:text-slate-300"
          title="Copy trace_id"
        >
          <span>trace: {traceId.slice(0, 8)}…</span>
          <span>{copied ? '✓ Copied' : '📋'}</span>
        </button>
        {typeof confidence === 'number' && (
          <span>· confidence: {(confidence * 100).toFixed(1)}%</span>
        )}
      </div>
      {typeof latencyMs === 'number' && <span>{latencyMs} ms</span>}
    </div>
  )
}
