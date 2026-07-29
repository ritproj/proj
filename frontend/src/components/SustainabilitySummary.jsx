import React from 'react'
import { TrendingDown, Minus } from 'lucide-react'

/**
 * Formats a percentage saving for display.
 * Returns { display, positive } where positive means quantum is better.
 */
function formatPct(pct) {
  if (pct === null || pct === undefined) return { display: '—', positive: false, neutral: true }
  const fixed = Math.abs(pct).toFixed(1)
  const positive = pct > 0.05   // quantum saved relative to classical
  const negative = pct < -0.05  // quantum is worse
  const neutral  = !positive && !negative
  const sign     = positive ? '-' : (negative ? '+' : '±')
  return { display: `${sign}${fixed}%`, positive, negative, neutral }
}

/**
 * Optionally translates CO2 saved (kg) into tree-days equivalent.
 * A tree absorbs ~21.7 kg of CO2 per year → ~0.0595 kg/day
 */
function co2ToTreeDays(co2SavedKg) {
  if (!co2SavedKg || co2SavedKg <= 0) return null
  const treeDays = (co2SavedKg / 0.0595).toFixed(1)
  return `≈ ${treeDays} tree-day${treeDays !== '1.0' ? 's' : ''} of CO₂ absorption`
}

/**
 * SustainabilitySummary
 * Props:
 *   savings: { distance_pct, fuel_pct, co2_pct } — from GET /api/compare
 *   co2SavedKg: number (optional) — absolute CO2 saved in kg for the tree-days hint
 */
export default function SustainabilitySummary({ savings, co2SavedKg }) {
  if (!savings) return null

  const distPct = formatPct(savings.distance_pct)
  const fuelPct = formatPct(savings.fuel_pct)
  const co2Pct  = formatPct(savings.co2_pct)

  // Determine if quantum actually improved anything
  const anyImprovement = [savings.distance_pct, savings.fuel_pct, savings.co2_pct]
    .some((v) => v !== null && v > 0.05)

  const treeDaysHint = co2ToTreeDays(co2SavedKg)

  const rows = [
    { label: 'Distance', ...distPct },
    { label: 'Fuel',     ...fuelPct },
    { label: 'CO₂',      ...co2Pct  },
  ]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <TrendingDown size={18} className="text-green-400" />
        <h2 className="text-white font-semibold text-base">Sustainability Summary</h2>
      </div>

      {anyImprovement ? (
        <>
          <p className="text-gray-400 text-sm mb-4">Quantum Route Saves</p>
          <div className="grid grid-cols-3 gap-3">
            {rows.map(({ label, display, positive, negative, neutral }) => (
              <div key={label} className="bg-gray-800 rounded-xl p-4 text-center">
                <p className="text-gray-500 text-xs mb-2 uppercase tracking-wider">{label}</p>
                <p className={`text-xl font-bold ${
                  positive ? 'text-green-400' : negative ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {display}
                </p>
              </div>
            ))}
          </div>
          {treeDaysHint && (
            <p className="text-gray-500 text-xs mt-3 text-center">{treeDaysHint}</p>
          )}
        </>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-gray-400 bg-gray-800 rounded-xl px-4 py-3">
            <Minus size={16} className="text-yellow-400 shrink-0" />
            <span className="text-sm">
              Classical solver matched or outperformed quantum on this dataset.
            </span>
          </div>
          <p className="text-gray-600 text-xs px-1">
            This is expected — OR-Tools is an exact solver (finds the global optimum), while the
            quantum approach uses a QUBO heuristic that approximates the same objective.
            Quantum advantage emerges at scale on real quantum hardware, not local simulation.
          </p>
          {/* Still show the raw numbers */}
          <div className="grid grid-cols-3 gap-3 mt-2">
            {rows.map(({ label, display, positive, negative }) => (
              <div key={label} className="bg-gray-800/60 rounded-xl p-3 text-center">
                <p className="text-gray-600 text-xs mb-1 uppercase tracking-wider">{label}</p>
                <p className={`text-base font-semibold ${
                  positive ? 'text-green-400' : negative ? 'text-red-400' : 'text-yellow-400'
                }`}>{display}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
