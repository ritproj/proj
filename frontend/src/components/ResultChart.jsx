import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#9ca3af',
        font: { size: 12, family: 'Inter, sans-serif' },
        boxWidth: 12,
        boxHeight: 12,
        borderRadius: 4,
        useBorderRadius: true,
        padding: 16,
      },
    },
    tooltip: {
      backgroundColor: '#111827',
      titleColor: '#f9fafb',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { color: 'rgba(31,41,55,0.8)' },
      ticks: { color: '#6b7280', font: { size: 11 } },
    },
    y: {
      grid: { color: 'rgba(31,41,55,0.8)' },
      ticks: { color: '#6b7280', font: { size: 11 } },
      beginAtZero: true,
    },
  },
  animation: {
    duration: 600,
    easing: 'easeInOutQuart',
  },
  borderRadius: 6,
}

/**
 * ResultChart — grouped bar chart comparing Classical vs Quantum.
 * Props:
 *   classical: { distance_km, fuel_l, co2_kg, runtime_s }
 *   quantum:   { distance_km, fuel_l, co2_kg, runtime_s }
 */
export default function ResultChart({ classical, quantum }) {
  if (!classical && !quantum) return null

  const hasRuntime = classical?.runtime_s != null || quantum?.runtime_s != null

  const labels = ['Distance (km)', 'Fuel (L)', 'CO₂ (kg)', ...(hasRuntime ? ['Runtime (s)'] : [])]

  const data = {
    labels,
    datasets: [
      {
        label: 'Classical',
        data: [
          classical?.distance_km ?? 0,
          classical?.fuel_l      ?? 0,
          classical?.co2_kg      ?? 0,
          ...(hasRuntime ? [classical?.runtime_s ?? 0] : []),
        ],
        backgroundColor: 'rgba(59,130,246,0.75)',
        borderColor: '#3b82f6',
        borderWidth: 1.5,
        borderRadius: 6,
        hoverBackgroundColor: 'rgba(59,130,246,0.95)',
      },
      {
        label: 'Quantum (BQPhy)',
        data: [
          quantum?.distance_km ?? 0,
          quantum?.fuel_l      ?? 0,
          quantum?.co2_kg      ?? 0,
          ...(hasRuntime ? [quantum?.runtime_s ?? 0] : []),
        ],
        backgroundColor: 'rgba(168,85,247,0.75)',
        borderColor: '#a855f7',
        borderWidth: 1.5,
        borderRadius: 6,
        hoverBackgroundColor: 'rgba(168,85,247,0.95)',
      },
    ],
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-4">
        Classical vs Quantum — Key Metrics
      </h3>
      <div style={{ height: 240 }}>
        <Bar data={data} options={OPTIONS} />
      </div>
    </div>
  )
}
