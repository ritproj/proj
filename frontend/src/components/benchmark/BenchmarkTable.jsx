import React from 'react'
import { CheckCircle2, XCircle, TrendingDown, TrendingUp, Minus } from 'lucide-react'

/**
 * BenchmarkTable — full split-screen Classical vs Quantum comparison.
 * Winner cells are highlighted green; loser cells are highlighted red.
 *
 * Props:
 *   classical : { distance_km, fuel_l, co2_kg, runtime_s, feasible }
 *   quantum   : { distance_km, fuel_l, co2_kg, runtime_s, feasible, fallback_used,
 *                 objective_best, objective_mean, objective_variance, runs, method }
 */
export default function BenchmarkTable({ classical, quantum }) {
  if (!classical && !quantum) return null

  const fmt = (v, d = 2) => v != null ? Number(v).toFixed(d) : '—'

  // Returns: 'quantum' | 'classical' | 'tie' | null
  const winner = (cv, qv, lowerIsBetter = true) => {
    if (cv == null || qv == null) return null
    const diff = Math.abs(cv - qv)
    if (diff < 0.001) return 'tie'
    if (lowerIsBetter) return qv < cv ? 'quantum' : 'classical'
    return qv > cv ? 'quantum' : 'classical'
  }

  const methodLabel = m => {
    if (m === 'bqphy')               return 'BQPhy QIEO'
    if (m === 'exhaustive')          return 'Exhaustive enum'
    if (m === 'simulated_annealing') return 'Sim. Annealing'
    if (m === 'nn_fallback')         return 'NN + 2-opt'
    return m ?? '—'
  }

  const rows = [
    {
      label: 'Distance',
      cv: classical?.distance_km != null ? `${fmt(classical.distance_km)} km` : '—',
      qv: quantum?.distance_km   != null ? `${fmt(quantum.distance_km)} km`   : '—',
      w: winner(classical?.distance_km, quantum?.distance_km),
    },
    {
      label: 'Fuel Consumed',
      cv: classical?.fuel_l != null ? `${fmt(classical.fuel_l)} L`  : '—',
      qv: quantum?.fuel_l   != null ? `${fmt(quantum.fuel_l)} L`    : '—',
      w: winner(classical?.fuel_l, quantum?.fuel_l),
    },
    {
      label: 'CO₂ Emissions',
      cv: classical?.co2_kg != null ? `${fmt(classical.co2_kg)} kg` : '—',
      qv: quantum?.co2_kg   != null ? `${fmt(quantum.co2_kg)} kg`   : '—',
      w: winner(classical?.co2_kg, quantum?.co2_kg),
    },
    {
      label: 'Runtime',
      cv: classical?.runtime_s != null ? `${fmt(classical.runtime_s, 3)} s` : '—',
      qv: quantum?.runtime_s   != null ? `${fmt(quantum.runtime_s, 3)} s`   : '—',
      w: winner(classical?.runtime_s, quantum?.runtime_s),
    },
    {
      label: 'Feasible',
      cv: classical?.feasible != null ? (classical.feasible ? '✓ Yes' : '✗ No') : '—',
      qv: quantum?.feasible   != null ? (quantum.feasible   ? '✓ Yes' : '✗ No') : '—',
      w: null,
    },
    {
      label: 'QUBO Variables',
      cv: '—',
      qv: quantum?.n_vars != null ? `${quantum.n_vars} vars` : '—',
      w: null,
    },
    {
      label: 'Algorithm',
      cv: 'OR-Tools GLS',
      qv: methodLabel(quantum?.method),
      w: null,
    },
  ]

  // Cell styling based on winner
  function cellClass(side, w) {
    if (w === null) return 'text-white'
    if (w === 'tie') return 'text-yellow-400'
    if (side === 'quantum' && w === 'quantum')   return 'text-green-400 font-bold'
    if (side === 'classical' && w === 'classical') return 'text-green-400 font-bold'
    if (side === 'quantum' && w === 'classical')   return 'text-red-400/70'
    if (side === 'classical' && w === 'quantum')   return 'text-red-400/70'
    return 'text-white'
  }

  function cellBg(side, w) {
    if (w === null || w === 'tie') return ''
    if (side === 'quantum' && w === 'quantum')     return 'bg-green-900/15'
    if (side === 'classical' && w === 'classical') return 'bg-green-900/15'
    if ((side === 'quantum' && w === 'classical') || (side === 'classical' && w === 'quantum'))
      return 'bg-red-900/10'
    return ''
  }

  function WinIcon({ side, w }) {
    if (w === 'tie') return <Minus size={12} className="text-yellow-400 inline ml-1" />
    if (side === 'quantum'   && w === 'quantum')   return <TrendingDown size={12} className="text-green-400 inline ml-1" />
    if (side === 'classical' && w === 'classical') return <TrendingDown size={12} className="text-green-400 inline ml-1" />
    return null
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left text-gray-500 text-xs font-semibold uppercase tracking-wider px-5 py-3">Metric</th>
            <th className="text-center text-blue-400 text-xs font-semibold uppercase tracking-wider px-5 py-3">
              Classical
            </th>
            <th className="text-center text-purple-400 text-xs font-semibold uppercase tracking-wider px-5 py-3">
              Quantum
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ label, cv, qv, w }, idx) => (
            <tr key={label} className={`border-b border-gray-800/50 ${idx % 2 === 0 ? '' : 'bg-gray-800/10'}`}>
              <td className="text-gray-400 px-5 py-3 text-xs font-medium uppercase tracking-wide">{label}</td>
              <td className={`text-center px-5 py-3 transition-colors ${cellClass('classical', w)} ${cellBg('classical', w)}`}>
                {cv}
                <WinIcon side="classical" w={w} />
              </td>
              <td className={`text-center px-5 py-3 transition-colors ${cellClass('quantum', w)} ${cellBg('quantum', w)}`}>
                {qv}
                <WinIcon side="quantum" w={w} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* QUBO stats footer */}
      {quantum && (
        <div className="border-t border-gray-800 px-5 py-3 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Solver Runs',   value: quantum.runs },
            { label: 'Obj Best',      value: quantum.objective_best     != null ? Number(quantum.objective_best).toFixed(2)     : null },
            { label: 'Obj Mean',      value: quantum.objective_mean     != null ? Number(quantum.objective_mean).toFixed(2)     : null },
            { label: 'Obj Variance',  value: quantum.objective_variance != null ? Number(quantum.objective_variance).toFixed(4) : null },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-gray-600 text-xs mb-0.5">{label}</p>
              <p className="text-purple-300 text-sm font-medium font-mono">{value ?? '—'}</p>
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="border-t border-gray-800 px-5 py-2 flex items-center gap-4 text-xs text-gray-600">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 inline-block" /> Better value</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500/60 inline-block" /> Worse value</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500 inline-block" /> Tied</span>
        {quantum?.fallback_used && (
          <span className="ml-auto text-orange-400">⚠ Fallback heuristic used</span>
        )}
      </div>
    </div>
  )
}
