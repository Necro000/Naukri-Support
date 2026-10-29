import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'

export function ChatWindow({ messages, loading, resetNotice, onPickPrompt }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, loading])

  return (
    <div
      id="chat-log"
      role="log"
      aria-live="polite"
      aria-label="Support conversation history"
      className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 space-y-5"
    >
      {resetNotice && (
        <div
          role="status"
          className="mx-auto max-w-md rounded-full border border-indigo-200 bg-indigo-50/80 px-4 py-1.5 text-center text-xs font-medium text-indigo-800 dark:border-indigo-900/60 dark:bg-indigo-950/60 dark:text-indigo-200"
        >
          ✨ Fresh start — I won&apos;t remember the earlier conversation.
        </div>
      )}

      <div className="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50/90 via-white to-slate-50 p-5 shadow-xs dark:border-indigo-950/80 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/30">
        <div className="flex items-start gap-3">
          <div
            aria-hidden="true"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-lg font-bold text-white shadow-xs"
          >
            N
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
              Hi! I&apos;m your Naukri hiring assistant.
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
              Ask about any Naukri.com hiring policy (grounded strictly in our 12 policy documents),
              or check a candidate job application status like{' '}
              <button
                type="button"
                onClick={() => onPickPrompt('Status of APP-0002?')}
                className="font-mono font-semibold text-indigo-600 underline decoration-indigo-300 underline-offset-2 hover:text-indigo-500 dark:text-indigo-400"
              >
                APP-0002
              </button>{' '}
              or{' '}
              <button
                type="button"
                onClick={() => onPickPrompt('Status of APP-0006?')}
                className="font-mono font-semibold text-indigo-600 underline decoration-indigo-300 underline-offset-2 hover:text-indigo-500 dark:text-indigo-400"
              >
                APP-0006
              </button>
              .
            </p>
          </div>
        </div>
      </div>

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
