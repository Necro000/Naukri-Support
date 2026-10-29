# Frontend (optional extra)

React + Vite + **Tailwind CSS v4**, deployed on Vercel. Talks to the FastAPI backend via `VITE_API_URL`.
Goal: a warm, human, professional support chat — not a generic dashboard.
Build only after Part 4 passes; the backend must never depend on it.

## 1. Setup
```powershell
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install tailwindcss @tailwindcss/vite
```
`vite.config.js`
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({ plugins: [react(), tailwindcss()] })
```
`src/index.css`
```css
@import "tailwindcss";
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --color-brand-500: #4f46e5;
  --color-brand-600: #4338ca;
  --color-accent-500: #f59e0b;
}
```
`frontend/.env`: `VITE_API_URL=http://127.0.0.1:8001`

## 2. Screen layout
```
┌───────────────────────────────────────────────┐
│ Header: logo · "Naukri Support" · health dot · theme toggle │
├───────────────────────────────┬───────────────┤
│ ChatWindow                    │ Side panel    │
│  - greeting                   │  - Examples   │
│  - message bubbles            │  - Add doc    │
│  - status cards               │  - About      │
├───────────────────────────────┴───────────────┤
│ Composer: input · send · prompt chips         │
└───────────────────────────────────────────────┘
```
Mobile: side panel collapses into a drawer.

## 3. Components
| Component | Props | Behaviour |
|---|---|---|
| `App` | – | Holds conversation id, messages, theme |
| `Header` | `healthy`, `onToggleTheme` | Polls `/health` on load |
| `ChatWindow` | `messages`, `loading` | `aria-live="polite"`, auto-scroll |
| `MessageBubble` | `role`, `text`, `sources` | User right/indigo, agent left/white |
| `RouteBadge` | `route` | "Policy · RAG" / "Status lookup" / "Blocked" |
| `GuardrailChip` | `flag` | 🔒 PII masked · 🛡 Injection blocked · ❓ Not in policies |
| `SourceList` | `sources` | Doc names as small chips |
| `StatusCard` | `result` | Record ID, status pill, salary, escalation meter |
| `EscalationMeter` | `score`, `threshold` | 0–1 bar, amber when above threshold |
| `TypingIndicator` | – | Three bouncing dots |
| `Composer` | `onSend`, `disabled` | Enter to send, Shift+Enter newline |
| `PromptChips` | `onPick` | One-tap examples |
| `TraceFooter` | `traceId`, `latencyMs` | Small, muted, copyable |
| `AddDocPanel` | – | Form → `POST /add-document`, shows chunk counts |
| `ErrorBanner` | `message` | Friendly retry copy |

Folder: `src/components/`, `src/api.js`, `src/hooks/useChat.js`.

## 4. State & API flow
1. On first load generate `conversation_id` (`crypto.randomUUID()`), store in `localStorage`.
2. Send → push user bubble → show typing → `POST /ask`.
3. Render `answer`, then chips (route, flags), sources, status card if `tool_result`.
4. "New chat" button clears messages and creates a new `conversation_id` (demonstrates reset memory).
```js
export async function ask(query, conversation_id) {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, conversation_id }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
```

## 5. Design tokens
| Token | Light | Dark |
|---|---|---|
| Background | `slate-50` | `slate-950` |
| Surface | `white` | `slate-900` |
| Text | `slate-900` | `slate-100` |
| Primary | `#4f46e5` | `#818cf8` |
| Accent (escalation) | `#f59e0b` | `#fbbf24` |
| Success / danger | `#10b981` / `#f43f5e` | same, lighter |
| Radius | `rounded-2xl` cards, `rounded-full` chips | |
| Shadow | `shadow-sm`, hover `shadow-md` | |
| Font | Inter 400/500/600 | |
| Motion | 150–200 ms ease, respect `prefers-reduced-motion` | |

## 6. Human-touch copy
| Moment | Copy |
|---|---|
| Greeting | "Hi! I'm your Naukri hiring assistant. Ask about a policy, or check an application like APP-0007." |
| Typing | "Looking that up…" |
| Fallback | "I couldn't find that in our hiring policies. Want me to flag it for the support team?" |
| Injection blocked | "I can't help with that request, but I'm happy to answer hiring-policy questions." |
| PII masked | "I hid the phone number for your privacy." |
| Not found | "I can't find that application ID. Could you double-check it?" |
| Error | "Something went wrong on our side. Please try again in a moment." |
| New chat | "Fresh start — I won't remember the earlier conversation." |
Prompt chips: "Notice period policy", "Status of APP-0007", "How do referral bonuses work?", "Remote work eligibility".

## 7. Accessibility
- Visible focus rings; full keyboard use; labels on all inputs.
- Message list `role="log"` + `aria-live="polite"`.
- Contrast ≥ 4.5:1; status never conveyed by colour alone (icon + text).
- Honour `prefers-reduced-motion` and `prefers-color-scheme`.

## 8. Quality checklist
- [ ] Works at 360 px width and desktop
- [ ] Loading, empty, error states handled
- [ ] No hard-coded API URL
- [ ] No images/screenshots committed (keeps the repo within the brief)
- [ ] `npm run build` passes
- [ ] Unique `id`s on interactive elements for testing

## 9. Out of scope
Auth, real user accounts, analytics, file uploads.
