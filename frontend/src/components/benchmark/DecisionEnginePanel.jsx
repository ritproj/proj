import React from 'react'
import { Trophy, Zap, Cpu, AlertCircle, Minus } from 'lucide-react'

/**
 * DecisionEnginePanel — renders the backend's decision object verbatim.
 * Never recomputes scores or winner client-side (ADR-002).
 *
 * Props:
 *   winner   : "classical" | "quantum" | null
 *   decision : { reason, classical_score, quantum_score, scoring_breakdown }
 *   quantum  : { feasible, fallback_used, ... }  — for infeasibility check
 */
export default function DecisionEnginePanel({ winner, decision, quantum }) {
  if (!winner || !decision) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex items-center gap-3 text-gray-500">
        <AlertCircle size={18} className="shrink-0" />
        <span className="text-sm">Run both solvers to see the Decision Engine verdict.</span>
      </div>
    )
  }

  const infeasible = quantum?.feasible === false
  const isQuantumWinner = winner === 'quantum'
  const winnerColor = isQuantumWinner ? 'text-purple-400' : 'text-blue-400'
  const winnerBg    = isQuantumWinner ? 'bg-purple-900/20 border-purple-700/50' : 'bg-blue-900/20 border-blue-700/50'
  const WinnerIcon  = isQuantumWinner ? Zap : Cpu
  const winnerLabel = isQuantumWinner ? 'Quantum' : 'Classical'

  const sb = decision.scoring_breakdown ?? {}

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">

      {/* Winner badge */}
      <div className={`flex items-center gap-3 border rounded-xl px-4 py-3 ${winnerBg}`}>
        <Trophy size={20} className="text-yellow-400 shrink-0" />
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-0.5">Winner</p>
          <div className="flex items-center gap-2">
            <WinnerIcon size={16} className={winnerColor} />
            <span className={`text-lg font-bold ${winnerColor}`}>{winnerLabel}</span>
          </div>
        </div>
      </div>

      {/* Reason — largest text, verbatim from backend */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">Reasoning</p>
        <p className="text-gray-200 text-sm leading-relaxed">{decision.reason}</p>
      </div>

      {/* Score bars — only when both are feasible */}
      {!infeasible ? (
        <div className="space-y-3">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Composite Score (0–1)</p>

          {/* Classical */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-blue-400 font-medium flex items-center gap-1.5"><Cpu size={12} />Classical</span>
              <span className="text-gray-300 font-mono">{decision.classical_score?.toFixed(3)}</span>
            </div>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${(decision.classical_score ?? 0) * 100}%` }}
              />
            </div>
          </div>

          {/* Quantum */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-purple-400 font-medium flex items-center gap-1.5"><Zap size={12} />Quantum</span>
              <span className="text-gray-300 font-mono">{decision.quantum_score?.toFixed(3)}</span>
            </div>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${(decision.quantum_score ?? 0) * 100}%` }}
              />
            </div>
          </div>

          {/* Metric breakdown */}
          {(sb.distance != null || sb.runtime != null) && (
            <div className="pt-1 grid grid-cols-2 gap-3">
              {[
                { label: 'Distance score', value: sb.distance, color: 'text-green-400' },
                { label: 'Runtime score',  value: sb.runtime,  color: 'text-yellow-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-gray-800 rounded-xl px-3 py-2 text-center">
                  <p className="text-gray-500 text-xs mb-1">{label}</p>
                  <p className={`text-base font-bold ${color}`}>
                    {value != null ? value.toFixed(3) : '—'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Fuel/CO₂ exclusion note */}
          {sb.fuel_co2_note && (
            <p className="text-gray-600 text-xs italic leading-relaxed pt-1">
              ℹ {sb.fuel_co2_note}
            </p>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2 text-orange-300 text-sm bg-orange-900/20 border border-orange-700/50 rounded-xl px-4 py-3">
          <AlertCircle size={15} className="shrink-0" />
          <span>Quantum route infeasible — score comparison not applicable.</span>
        </div>
      )}
    </div>
  )
}
