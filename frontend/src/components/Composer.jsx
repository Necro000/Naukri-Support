import { useState, useId } from 'react'
import { PromptChips } from './PromptChips'

export function Composer({ onSend, disabled }) {
  const [text, setText] = useState('')
  const inputId = useId()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() || disabled) return
    onSend(text)
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="border-t border-slate-200 bg-white/95 px-4 py-3 backdrop-blur-xs sm:px-6 dark:border-slate-800 dark:bg-slate-900/95">
      <PromptChips onPick={(q) => onSend(q)} disabled={disabled} />

      <form onSubmit={handleSubmit} className="flex items-end gap-2.5">
        <div className="flex-1">
          <label htmlFor={inputId} className="sr-only">
            Ask a policy question or check an application status
          </label>
          <textarea
            id={inputId}
            rows={1}
            value={text}
            disabled={disabled}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a hiring policy question or check an application ID (e.g. APP-0002)…"
            className="w-full resize-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-2 focus:outline-indigo-500 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:bg-slate-900"
          />
        </div>
        <button
          id="send-message-btn"
          type="submit"
          disabled={disabled || !text.trim()}
          className="inline-flex h-10 shrink-0 items-center justify-center gap-1.5 rounded-2xl bg-indigo-600 px-4 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-500 focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500 disabled:opacity-50 dark:bg-indigo-500 dark:hover:bg-indigo-400"
        >
          <span>Send</span>
          <span aria-hidden="true">↑</span>
        </button>
      </form>
    </div>
  )
}
