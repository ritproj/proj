import React from 'react'

/**
 * StatsCard — displays a single metric.
 * Props: label, value, unit, icon (Lucide component), color (tailwind color class)
 */
export default function StatsCard({ label, value, unit = '', icon: Icon, color = 'text-green-400' }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">{label}</span>
        {Icon && <Icon size={18} className={color} />}
      </div>
      <div className="flex items-end gap-1.5">
        <span className="text-2xl font-bold text-white leading-none">
          {value ?? '—'}
        </span>
        {unit && <span className="text-gray-400 text-sm mb-0.5">{unit}</span>}
      </div>
    </div>
  )
}
