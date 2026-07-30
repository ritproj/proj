import React from 'react'

/**
 * ComparisonTable — side-by-side classical vs quantum with Δ% column.
 * Highlights the winning value in green and marks the winner row.
 *
 * Props:
 *   classical : { distance_km, fuel_l, co2_kg, runtime_s }
 *   quantum   : { distance_km, fuel_l, co2_kg, runtime_s }
 *   winner    : "classical" | "quantum" | "tie" | null  — from /api/compare
 */
export default function ComparisonTable({ classical, quantum, winner, quantumMethod }) {
  if (!classical && !quantum) return null
  const qLabel = quantumMethod === 'bqphy' ? 'BQPhy' : 'Quantum'

  const fmt = (v, decimals = 2) =>
    v !== null && v !== undefined ? Number(v).toFixed(decimals) : '—'

  function delta(cv, qv) {
    if (cv == null || qv == null) return null
    if (cv === 0) return null
    return ((cv - qv) / cv * 100)
  }

  function deltaLabel(pct) {
    if (pct === null) return '—'
    const sign  = pct > 0.05 ? '▼ ' : pct < -0.05 ? '▲ ' : '≈ '
    const color = pct > 0.05 ? 'text-green-400' : pct < -0.05 ? 'text-red-400' : 'text-yellow-400'
    return <span className={`font-mono text-xs ${color}`}>{sign}{Math.abs(pct).toFixed(1)}%</span>
  }

  const rows = [
    {
      metric:   'Distance',
      cv:       classical ? `${fmt(classical.distance_km)} km` : '—',
      qv:       quantum   ? `${fmt(quantum.distance_km)} km`   : '—',
      deltaPct: delta(classical?.distance_km, quantum?.distance_km),
      qWins:    quantum && classical && quantum.distance_km < classical.distance_km - 0.01,
      cWins:    quantum && classical && classical.distance_km < quantum.distance_km - 0.01,
    },
    {
      metric:   'Fuel',
      cv:       classical ? `${fmt(classical.fuel_l)} L`  : '—',
      qv:       quantum   ? `${fmt(quantum.fuel_l)} L`    : '—',
      deltaPct: delta(classical?.fuel_l, quantum?.fuel_l),
      qWins:    quantum && classical && quantum.fuel_l < classical.fuel_l - 0.001,
      cWins:    quantum && classical && classical.fuel_l < quantum.fuel_l - 0.001,
    },
    {
      metric:   'CO₂',
      cv:       classical ? `${fmt(classical.co2_kg)} kg` : '—',
      qv:       quantum   ? `${fmt(quantum.co2_kg)} kg`   : '—',
      deltaPct: delta(classical?.co2_kg, quantum?.co2_kg),
      qWins:    quantum && classical && quantum.co2_kg < classical.co2_kg - 0.001,
      cWins:    quantum && classical && classical.co2_kg < quantum.co2_kg - 0.001,
    },
    {
      metric:   'Runtime',
      cv:       classical ? `${fmt(classical.runtime_s, 3)} s` : '—',
      qv:       quantum   ? `${fmt(quantum.runtime_s, 3)} s`   : '—',
      deltaPct: null,   // runtime comparison not a savings %
      qWins:    false,  // quantum is expected to be slower on simulator
      cWins:    false,
    },
  ]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left   text-gray-500 font-semibold uppercase text-xs tracking-wider px-4 py-3">Metric</th>
            <th className="text-center text-blue-400  font-semibold uppercase text-xs tracking-wider px-4 py-3">Classical</th>
            <th className="text-center text-green-400 font-semibold uppercase text-xs tracking-wider px-4 py-3">{qLabel}</th>
            <th className="text-center text-gray-500  font-semibold uppercase text-xs tracking-wider px-4 py-3">Δ (Q vs C)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ metric, cv, qv, deltaPct, qWins, cWins }, idx) => (
            <tr
              key={metric}
              className={`border-b border-gray-800/50 ${idx % 2 === 0 ? 'bg-gray-900' : 'bg-gray-800/20'}`}
            >
              <td className="text-gray-400 px-4 py-3">{metric}</td>

              {/* Classical value */}
              <td className={`text-center px-4 py-3 font-medium ${cWins ? 'text-blue-400' : 'text-white'}`}>
                {cv}
                {cWins && <span className="ml-1 text-blue-500 text-xs">↓</span>}
              </td>

              {/* Quantum value */}
              <td className={`text-center px-4 py-3 font-medium ${qWins ? 'text-green-400' : 'text-white'}`}>
                {qv}
                {qWins && <span className="ml-1 text-green-500 text-xs">↓</span>}
              </td>

              {/* Delta */}
              <td className="text-center px-4 py-3">
                {deltaLabel(deltaPct)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Winner footer */}
      {winner && (
        <div className={`px-4 py-2 border-t border-gray-800 flex items-center gap-2 text-xs font-medium ${
          winner === 'quantum'   ? 'text-green-400' :
          winner === 'classical' ? 'text-blue-400'  :
          'text-yellow-400'
        }`}>
          <span className="text-gray-500 font-normal">Winner:</span>
          <span className="capitalize font-semibold">
            {winner === 'quantum' && quantumMethod === 'bqphy' ? 'BQPhy' : winner}
          </span>
          {winner === 'tie' && <span className="text-gray-500 font-normal">(within 0.01 km)</span>}
        </div>
      )}
    </div>
  )
}
