import React, { useEffect, useRef } from 'react'
import { Trophy, Zap, Cpu, AlertCircle } from 'lucide-react'

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
  const winnerColor  = isQuantumWinner ? 'text-purple-400' : 'text-blue-400'
  const winnerBorder = isQuantumWinner ? 'border-purple-700/50' : 'border-blue-700/50'
  const winnerGlow   = isQuantumWinner
    ? 'rgba(168,85,247,0.15)'
    : 'rgba(59,130,246,0.15)'
  const WinnerIcon  = isQuantumWinner ? Zap : Cpu
  const winnerLabel = isQuantumWinner ? 'Quantum (BQPhy)' : 'Classical (OR-Tools)'

  const sb = decision.scoring_breakdown ?? {}

  const cs = decision.classical_score ?? 0
  const qs = decision.quantum_score   ?? 0

  /* Animated score bars — use CSS transition on width */
  const barRef = useRef(null)
  useEffect(() => {
    if (barRef.current) {
      barRef.current.style.transition = 'width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1)'
    }
  }, [])

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">

      {/* Winner badge */}
      <div
        className={`flex items-center gap-4 border ${winnerBorder} rounded-xl px-5 py-4`}
        style={{ background: winnerGlow, boxShadow: `0 0 24px ${winnerGlow}` }}
      >
        <Trophy size={28} className="text-yellow-400 shrink-0 drop-shadow-lg" />
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-0.5">Decision Engine Winner</p>
          <div className="flex items-center gap-2">
            <WinnerIcon size={20} className={winnerColor} />
            <span className={`text-2xl font-extrabold ${winnerColor}`}>{winnerLabel}</span>
          </div>
        </div>
      </div>

      {/* Reason */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">Reasoning</p>
        <p className="text-gray-200 text-sm leading-relaxed">{decision.reason}</p>
      </div>

      {/* Score bars */}
      {!infeasible ? (
        <div className="space-y-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Composite Score (0–1)</p>

          {/* Classical */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-blue-400 font-semibold flex items-center gap-1.5">
                <Cpu size={12} /> Classical
                {winner === 'classical' && <Trophy size={11} className="text-yellow-400" />}
              </span>
              <span className="text-gray-200 font-mono font-bold">{cs.toFixed(3)}</span>
            </div>
            <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{
                  width: `${cs * 100}%`,
                  transition: 'width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1)',
                  boxShadow: winner === 'classical' ? '0 0 8px rgba(59,130,246,0.6)' : 'none',
                }}
              />
            </div>
          </div>

          {/* Quantum */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-purple-400 font-semibold flex items-center gap-1.5">
                <Zap size={12} /> Quantum (BQPhy)
                {winner === 'quantum' && <Trophy size={11} className="text-yellow-400" />}
              </span>
              <span className="text-gray-200 font-mono font-bold">{qs.toFixed(3)}</span>
            </div>
            <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full"
                style={{
                  width: `${qs * 100}%`,
                  transition: 'width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) 0.15s',
                  boxShadow: winner === 'quantum' ? '0 0 8px rgba(168,85,247,0.6)' : 'none',
                }}
              />
            </div>
          </div>

          {/* Metric breakdown mini-cards */}
          {(sb.distance != null || sb.runtime != null) && (
            <div className="pt-1 grid grid-cols-2 gap-3">
              {[
                { label: 'Distance weight (75%)', value: sb.distance, color: 'text-green-400' },
                { label: 'Runtime weight (25%)',  value: sb.runtime,  color: 'text-yellow-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-gray-800 rounded-xl px-3 py-2.5 text-center">
                  <p className="text-gray-500 text-xs mb-1">{label}</p>
                  <p className={`text-base font-bold font-mono ${color}`}>
                    {value != null ? value.toFixed(3) : '—'}
                  </p>
                </div>
              ))}
            </div>
          )}

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
