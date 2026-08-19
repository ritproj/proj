import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { Activity } from 'lucide-react'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler,
)

/**
 * ConvergenceChart — displays BQPhy per-run QUBO energy convergence.
 *
 * Props:
 *   convergenceData : number[]  — per-run QUBO energy values
 *   method          : string    — solver method label
 *   nVars           : number    — number of QUBO variables
 */
export default function ConvergenceChart({ convergenceData, method, nVars }) {
  if (!convergenceData || convergenceData.length === 0) return null

  const isBqphy = method === 'bqphy'
  const labels = convergenceData.map((_, i) => `Run ${i + 1}`)

  const data = {
    labels,
    datasets: [
      {
        label: 'QUBO Energy',
        data: convergenceData,
        borderColor: '#a855f7',
        backgroundColor: 'rgba(168, 85, 247, 0.08)',
        pointBackgroundColor: convergenceData.map((v, i) =>
          v === Math.min(...convergenceData) ? '#22c55e' : '#a855f7'
        ),
        pointBorderColor: convergenceData.map((v, i) =>
          v === Math.min(...convergenceData) ? '#22c55e' : '#a855f7'
        ),
        pointRadius: convergenceData.map((v, i) =>
          v === Math.min(...convergenceData) ? 7 : 5
        ),
        pointHoverRadius: 8,
        borderWidth: 2.5,
        tension: 0.3,
        fill: true,
      },
    ],
  }

  const minEnergy = Math.min(...convergenceData)
  const maxEnergy = Math.max(...convergenceData)

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#111827',
        titleColor: '#f9fafb',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: ctx => `QUBO energy: ${ctx.parsed.y.toFixed(4)}`,
          afterLabel: ctx => {
            const isMin = ctx.parsed.y === minEnergy
            return isMin ? '★ Best run' : ''
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(55,65,81,0.4)' },
        ticks: { color: '#6b7280', font: { size: 11 } },
        title: {
          display: true,
          text: 'Independent Restart',
          color: '#4b5563',
          font: { size: 11 },
        },
      },
      y: {
        grid: { color: 'rgba(55,65,81,0.4)' },
        ticks: { color: '#6b7280', font: { size: 11 } },
        title: {
          display: true,
          text: 'QUBO Energy (xᵀQx)',
          color: '#4b5563',
          font: { size: 11 },
        },
      },
    },
    animation: {
      duration: 800,
      easing: 'easeInOutQuart',
    },
  }

  return (
    <div className="bg-gray-900 border border-purple-900/40 rounded-2xl p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity size={15} className="text-purple-400" />
          <h3 className="text-gray-300 text-xs font-semibold uppercase tracking-wider">
            {isBqphy ? 'BQPhy Energy Convergence' : 'QUBO Solver Convergence'}
          </h3>
        </div>
        <span className="text-gray-600 text-xs font-mono">{nVars} vars</span>
      </div>

      {/* Chart */}
      <div style={{ height: 180 }}>
        <Line data={data} options={options} />
      </div>

      {/* Stats row */}
      <div className="mt-3 grid grid-cols-3 gap-2">
        {[
          { label: 'Best energy', value: minEnergy.toFixed(2), color: 'text-green-400' },
          { label: 'Mean energy', value: convergenceData.length > 0
              ? (convergenceData.reduce((s, v) => s + v, 0) / convergenceData.length).toFixed(2)
              : '—', color: 'text-purple-400' },
          { label: 'Variance', value: convergenceData.length > 1
              ? (convergenceData.reduce((s, v) => s + Math.pow(v - convergenceData.reduce((a, b) => a + b, 0) / convergenceData.length, 2), 0) / convergenceData.length).toFixed(4)
              : '0.0000', color: 'text-yellow-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-gray-800/60 rounded-xl p-2 text-center">
            <p className="text-gray-600 text-xs mb-0.5">{label}</p>
            <p className={`text-sm font-bold font-mono ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Interpretation note */}
      <p className="text-gray-600 text-xs mt-3 leading-relaxed">
        Each point = one independent {isBqphy ? 'BQPhy evolutionary' : 'SA'} restart on the{' '}
        <span className="text-purple-400 font-mono">{nVars}-variable QUBO</span>.
        Green point = best solution selected for route decoding.
        Lower energy = closer to optimal assignment.
      </p>
    </div>
  )
}
