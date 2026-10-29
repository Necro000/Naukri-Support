import { useState, useId, useCallback } from 'react'
import { addDocument } from '../api'

export function AddDocPanel({ onDocumentAdded }) {
  const [docId, setDocId] = useState('')
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState(null)

  const baseId = useId()

  const syncAriaInvalid = useCallback((e) => {
    const el = e.target
    if (el && typeof el.matches === 'function') {
      try {
        el.setAttribute('aria-invalid', el.matches(':user-invalid') ? 'true' : 'false')
      } catch {
        // ignore if selector unsupported
      }
    }
  }, [])

  const handleInputAriaSync = useCallback(
    (e) => {
      if (e.target?.hasAttribute?.('aria-invalid')) {
        syncAriaInvalid(e)
      }
    },
    [syncAriaInvalid]
  )

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!docId.trim() || !title.trim() || !text.trim() || submitting) return

    setSubmitting(true)
    setResult(null)
    setErr(null)

    try {
      const res = await addDocument({
        docId: docId.trim(),
        title: title.trim(),
        text: text.trim(),
      })
      setResult(res)
      setDocId('')
      setTitle('')
      setText('')
      onDocumentAdded?.()
    } catch (error) {
      setErr(error?.message || 'Could not index document.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900">
      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Add Knowledge Base Policy
      </h3>
      <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
        Chunks &amp; embeds into both <code className="font-mono">kb_fixed</code> and{' '}
        <code className="font-mono">kb_sentence</code> collections live.
      </p>

      <form
        onSubmit={handleSubmit}
        onBlurCapture={syncAriaInvalid}
        onInput={handleInputAriaSync}
        className="mt-3 space-y-2.5"
      >
        <div>
          <label
            htmlFor={`${baseId}-doc-id`}
            className="block text-xs font-medium text-slate-700 dark:text-slate-300"
          >
            Document ID
          </label>
          <span
            id={`${baseId}-doc-id-hint`}
            className="mb-1 block text-[11px] text-slate-500 dark:text-slate-400"
          >
            Format: lowercase snake_case (e.g. sabbatical_policy)
          </span>
          <input
            id={`${baseId}-doc-id`}
            type="text"
            required
            pattern="[a-z0-9_]+"
            aria-describedby={`${baseId}-doc-id-hint`}
            aria-errormessage={`${baseId}-doc-id-err`}
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            placeholder="sabbatical_policy"
            className="user-invalid-field w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-1.5 font-mono text-xs text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-2 focus:outline-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          />
          <div
            id={`${baseId}-doc-id-err`}
            className="error-msg mt-1 hidden text-[11px] text-rose-600 dark:text-rose-400"
          >
            <span aria-hidden="true">❌</span> Use lowercase letters, numbers, and underscores only.
          </div>
        </div>

        <div>
          <label
            htmlFor={`${baseId}-title`}
            className="block text-xs font-medium text-slate-700 dark:text-slate-300"
          >
            Title
          </label>
          <input
            id={`${baseId}-title`}
            type="text"
            required
            aria-errormessage={`${baseId}-title-err`}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Sabbatical Leave Policy"
            className="user-invalid-field mt-1 w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-1.5 text-xs text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-2 focus:outline-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          />
          <div
            id={`${baseId}-title-err`}
            className="error-msg mt-1 hidden text-[11px] text-rose-600 dark:text-rose-400"
          >
            <span aria-hidden="true">❌</span> Please enter a document title.
          </div>
        </div>

        <div>
          <label
            htmlFor={`${baseId}-text`}
            className="block text-xs font-medium text-slate-700 dark:text-slate-300"
          >
            Policy Text
          </label>
          <span
            id={`${baseId}-text-hint`}
            className="mb-1 block text-[11px] text-slate-500 dark:text-slate-400"
          >
            2–5 sentences describing the policy rules (min 10 chars)
          </span>
          <textarea
            id={`${baseId}-text`}
            rows={3}
            required
            minLength={10}
            aria-describedby={`${baseId}-text-hint`}
            aria-errormessage={`${baseId}-text-err`}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Employees with 5 years of continuous tenure may apply for a 12-week unpaid sabbatical…"
            className="user-invalid-field w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-1.5 text-xs text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-2 focus:outline-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          />
          <div
            id={`${baseId}-text-err`}
            className="error-msg mt-1 hidden text-[11px] text-rose-600 dark:text-rose-400"
          >
            <span aria-hidden="true">❌</span> Please enter at least 10 characters of policy text.
          </div>
        </div>

        <button
          id="add-doc-submit-btn"
          type="submit"
          disabled={submitting}
          className="w-full rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-slate-800 focus:outline-2 focus:outline-indigo-500 disabled:opacity-50 dark:bg-indigo-600 dark:hover:bg-indigo-500"
        >
          {submitting ? 'Indexing into ChromaDB…' : '+ Index Policy Document'}
        </button>
      </form>

      {result && (
        <div
          role="status"
          className="mt-2.5 rounded-xl border border-emerald-200 bg-emerald-50 p-2.5 text-xs text-emerald-900 dark:border-emerald-900/60 dark:bg-emerald-950/50 dark:text-emerald-200"
        >
          ✓ Indexed <code className="font-mono font-bold">{result.doc_id}</code> (
          <code className="font-mono">kb_fixed: +{result.chunks_added?.kb_fixed}</code>,{' '}
          <code className="font-mono">kb_sentence: +{result.chunks_added?.kb_sentence}</code>)
        </div>
      )}

      {err && (
        <div
          role="alert"
          className="mt-2.5 rounded-xl border border-rose-200 bg-rose-50 p-2.5 text-xs text-rose-900 dark:border-rose-900/60 dark:bg-rose-950/50 dark:text-rose-200"
        >
          ⚠️ {err}
        </div>
      )}
    </div>
  )
}
