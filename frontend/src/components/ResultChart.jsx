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

const LABELS = ['Distance (km)', 'Fuel (L)', 'CO₂ (kg)']

const OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#9ca3af', font: { size: 12 } },
    },
    title: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1f2937',
      titleColor: '#f9fafb',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      grid: { color: '#1f2937' },
      ticks: { color: '#9ca3af' },
    },
    y: {
      grid: { color: '#1f2937' },
      ticks: { color: '#9ca3af' },
      beginAtZero: true,
    },
  },
}

/**
 * ResultChart — grouped bar chart: Classical vs Quantum
 * Props:
 *   classical: { distance_km, fuel_l, co2_kg }
 *   quantum:   { distance_km, fuel_l, co2_kg }
 */
export default function ResultChart({ classical, quantum }) {
  if (!classical && !quantum) return null

  const data = {
    labels: LABELS,
    datasets: [
      {
        label: 'Classical',
        data: [
          classical?.distance_km ?? 0,
          classical?.fuel_l      ?? 0,
          classical?.co2_kg      ?? 0,
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: '#3b82f6',
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: 'Quantum',
        data: [
          quantum?.distance_km ?? 0,
          quantum?.fuel_l      ?? 0,
          quantum?.co2_kg      ?? 0,
        ],
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
        borderColor: '#22c55e',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-4">
        Classical vs Quantum
      </h3>
      <div style={{ height: 240 }}>
        <Bar data={data} options={OPTIONS} />
      </div>
    </div>
  )
}
