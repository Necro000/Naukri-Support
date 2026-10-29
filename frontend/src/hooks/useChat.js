import { useState, useCallback } from 'react'
import { ask } from '../api'

const STORAGE_KEY = 'naukri_support_conversation_id'

function getOrCreateConversationId() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return saved
    const fresh = `conv-${crypto.randomUUID().slice(0, 8)}`
    localStorage.setItem(STORAGE_KEY, fresh)
    return fresh
  } catch {
    return `conv-${Math.random().toString(36).slice(2, 10)}`
  }
}

export function useChat() {
  const [conversationId, setConversationId] = useState(getOrCreateConversationId)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [resetNotice, setResetNotice] = useState(false)

  const sendMessage = useCallback(
    async (rawQuery) => {
      const trimmed = rawQuery.trim()
      if (!trimmed || loading) return

      setError(null)
      setResetNotice(false)

      const userTurn = {
        id: `u-${Date.now()}`,
        role: 'user',
        text: trimmed,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, userTurn])
      setLoading(true)

      try {
        const res = await ask(trimmed, conversationId)
        const isBlocked = res.guardrail_flags?.includes('injection_blocked')
        const assistantTurn = {
          id: res.trace_id || `a-${Date.now()}`,
          role: 'assistant',
          text: res.answer,
          route: isBlocked ? 'blocked' : res.route,
          sources: res.sources || [],
          grounded: res.grounded,
          guardrailFlags: res.guardrail_flags || [],
          confidence: res.confidence,
          traceId: res.trace_id,
          latencyMs: res.latencyMs,
          toolResult: res.tool_result || null,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, assistantTurn])
      } catch (err) {
        setError(
          err?.message || 'Something went wrong on our side. Please try again in a moment.'
        )
      } finally {
        setLoading(false)
      }
    },
    [conversationId, loading]
  )

  const startNewChat = useCallback(() => {
    const fresh = `conv-${crypto.randomUUID().slice(0, 8)}`
    try {
      localStorage.setItem(STORAGE_KEY, fresh)
    } catch {
      // ignore storage failure
    }
    setConversationId(fresh)
    setMessages([])
    setError(null)
    setResetNotice(true)
  }, [])

  return {
    conversationId,
    messages,
    loading,
    error,
    resetNotice,
    setError,
    sendMessage,
    startNewChat,
  }
}
