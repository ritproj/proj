import React from 'react'

/**
 * BenchmarkTable — full split-screen Classical vs Quantum comparison.
 * Includes all /api/benchmark fields including QAOA-specific stats.
 *
 * Props:
 *   classical : { distance_km, fuel_l, co2_kg, runtime_s, feasible }
 *   quantum   : { distance_km, fuel_l, co2_kg, runtime_s, feasible, fallback_used,
 *                 objective_best, objective_mean, objective_variance, runs }
 */
export default function BenchmarkTable({ classical, quantum }) {
  if (!classical && !quantum) return null

  const fmt = (v, d = 2) =>
    v != null ? Number(v).toFixed(d) : '—'

  const better = (cv, qv, lowerIsBetter = true) => {
    if (cv == null || qv == null) return null
    return lowerIsBetter ? qv < cv : qv > cv
  }

  const rows = [
    { label: 'Distance',  cv: classical?.distance_km != null ? `${fmt(classical.distance_km)} km` : '—',
                          qv: quantum?.distance_km   != null ? `${fmt(quantum.distance_km)} km`   : '—',
                          q_better: better(classical?.distance_km, quantum?.distance_km) },
    { label: 'Fuel',      cv: classical?.fuel_l != null ? `${fmt(classical.fuel_l)} L`  : '—',
                          qv: quantum?.fuel_l   != null ? `${fmt(quantum.fuel_l)} L`    : '—',
                          q_better: better(classical?.fuel_l, quantum?.fuel_l) },
    { label: 'CO₂',       cv: classical?.co2_kg != null ? `${fmt(classical.co2_kg)} kg` : '—',
                          qv: quantum?.co2_kg   != null ? `${fmt(quantum.co2_kg)} kg`   : '—',
                          q_better: better(classical?.co2_kg, quantum?.co2_kg) },
    { label: 'Runtime',   cv: classical?.runtime_s != null ? `${fmt(classical.runtime_s, 3)} s` : '—',
                          qv: quantum?.runtime_s   != null ? `${fmt(quantum.runtime_s, 3)} s`   : '—',
                          q_better: false },
    { label: 'Feasible',  cv: classical?.feasible != null ? (classical.feasible ? '✓ Yes' : '✗ No') : '—',
                          qv: quantum?.feasible   != null ? (quantum.feasible   ? '✓ Yes' : '✗ No') : '—',
                          q_better: null },
    { label: 'QUBO Vars', cv: '—',
                          qv: quantum?.n_vars != null ? String(quantum.n_vars) : '—',
                          q_better: null },
    { label: 'Method',    cv: 'GLS exact',
                          qv: quantum?.method === 'exhaustive'         ? 'Exhaustive enum'
                            : quantum?.method === 'simulated_annealing' ? 'Sim. Annealing'
                            : quantum?.method === 'nn_fallback'         ? 'NN + 2-opt'
                            : quantum?.method ?? '—',
                          q_better: null },
  ]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left text-gray-500 text-xs font-semibold uppercase tracking-wider px-5 py-3">Metric</th>
            <th className="text-center text-blue-400 text-xs font-semibold uppercase tracking-wider px-5 py-3">Classical</th>
            <th className="text-center text-purple-400 text-xs font-semibold uppercase tracking-wider px-5 py-3">Quantum</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ label, cv, qv, q_better }, idx) => (
            <tr key={label} className={`border-b border-gray-800/50 ${idx % 2 === 0 ? '' : 'bg-gray-800/20'}`}>
              <td className="text-gray-400 px-5 py-3">{label}</td>
              <td className="text-center text-white px-5 py-3">{cv}</td>
              <td className={`text-center font-medium px-5 py-3 ${q_better === true ? 'text-green-400' : q_better === false ? 'text-white' : 'text-white'}`}>
                {qv}
                {q_better === true && <span className="ml-1 text-green-500 text-xs">↓</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* QAOA-specific stats */}
      {quantum && (
        <div className="border-t border-gray-800 px-5 py-3 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'QAOA Runs',   value: quantum.runs       },
            { label: 'Obj Best',    value: quantum.objective_best  != null ? Number(quantum.objective_best).toFixed(2)  : null },
            { label: 'Obj Mean',    value: quantum.objective_mean  != null ? Number(quantum.objective_mean).toFixed(2)  : null },
            { label: 'Obj Variance',value: quantum.objective_variance != null ? Number(quantum.objective_variance).toFixed(4) : null },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-gray-500 text-xs mb-0.5">{label}</p>
              <p className="text-gray-300 text-sm font-medium font-mono">{value ?? '—'}</p>
            </div>
          ))}
        </div>
      )}

      {/* Fallback badge */}
      {quantum?.fallback_used && (
        <div className="border-t border-gray-800 px-5 py-2 text-orange-300 text-xs flex items-center gap-2">
          <span className="text-orange-400">⚠</span>
          Fallback heuristic used — QAOA did not converge to a feasible route.
        </div>
      )}
    </div>
  )
}
