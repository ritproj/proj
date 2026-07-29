import React from 'react'
import { AlertTriangle, X } from 'lucide-react'

/**
 * ErrorBanner — shows a dismissible error message.
 * Props:
 *   message: string
 *   onDismiss: () => void
 */
export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null

  return (
    <div
      role="alert"
      className="flex items-start gap-3 bg-red-900/30 border border-red-700/60 text-red-300 rounded-xl px-4 py-3"
    >
      <AlertTriangle size={18} className="mt-0.5 shrink-0 text-red-400" />
      <span className="flex-1 text-sm">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="text-red-400 hover:text-red-200 transition-colors shrink-0"
        >
          <X size={16} />
        </button>
      )}
    </div>
  )
}
