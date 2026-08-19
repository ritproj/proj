import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, RefreshCw, Loader2, AlertCircle, ArrowLeft,
         Truck, Route, Users, Cpu, Leaf, TrendingDown } from 'lucide-react'
import {
  Chart as ChartJS, ArcElement, CategoryScale, LinearScale,
  BarElement, Tooltip, Legend, DoughnutController,
} from 'chart.js'
import { Doughnut, Bar } from 'react-chartjs-2'
import { useApp } from '../context/AppContext'
import { getAnalytics } from '../services/analytics'

ChartJS.register(
  ArcElement, CategoryScale, LinearScale,
  BarElement, Tooltip, Legend, DoughnutController,
)

/* ── KPI card ─────────────────────────────────────────────────────────────── */
function KpiCard({ label, value, sub, icon: Icon, color = 'text-green-400', warn = false }) {
  return (
    <div className={`bg-gray-900 border ${warn ? 'border-yellow-700/60' : 'border-gray-800'} rounded-xl px-5 py-4 flex flex-col gap-2
      hover:border-gray-700 transition-colors`}>
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">{label}</span>
        {Icon && <Icon size={18} className={color} />}
      </div>
      <div>
        <span className="text-2xl font-bold text-white leading-none">{value ?? '—'}</span>
        {sub && <p className="text-gray-500 text-xs mt-1">{sub}</p>}
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <section>
      <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {children}
      </div>
    </section>
  )
}

/* ── Utilization Donut ─────────────────────────────────────────────────────── */
function UtilizationDonut({ pct, vehiclesUsed, total }) {
  if (pct == null) return null
  const used = Math.min(pct, 100)
  const free = Math.max(100 - pct, 0)
  const color = pct > 90 ? '#f97316' : pct > 70 ? '#eab308' : '#10b981'

  const data = {
    datasets: [{
      data: [used, free],
      backgroundColor: [color, 'rgba(31,41,55,0.8)'],
      borderColor: [color, '#1f2937'],
      borderWidth: 2,
      circumference: 270,
      rotation: 225,
    }],
  }
  const opts = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '72%',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ctx.dataIndex === 0 ? `Utilization: ${pct}%` : `Headroom: ${free.toFixed(0)}%`,
        },
        backgroundColor: '#111827',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
      },
    },
    animation: { animateRotate: true, duration: 900 },
  }
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex flex-col items-center gap-3">
      <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider self-start">Fleet Utilization</p>
      <div style={{ position: 'relative', height: 160, width: 160 }}>
        <Doughnut data={data} options={opts} />
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          paddingTop: 20,
        }}>
          <span style={{ color, fontSize: 26, fontWeight: 800, lineHeight: 1 }}>{pct}%</span>
          <span style={{ color: '#6b7280', fontSize: 11, marginTop: 4 }}>{vehiclesUsed} / {total} vehicles</span>
        </div>
      </div>
      <p className={`text-xs font-medium ${pct > 90 ? 'text-orange-400' : 'text-green-400'}`}>
        {pct > 90 ? 'Near capacity — consider extra vehicles' : 'Capacity headroom OK'}
      </p>
    </div>
  )
}

/* ── Route Length Bar ──────────────────────────────────────────────────────── */
function RouteBar({ avg, longest }) {
  if (avg == null && longest == null) return null
  const data = {
    labels: ['Average Route', 'Longest Route'],
    datasets: [{
      data: [avg ?? 0, longest ?? 0],
      backgroundColor: ['rgba(59,130,246,0.7)', 'rgba(249,115,22,0.7)'],
      borderColor: ['#3b82f6', '#f97316'],
      borderWidth: 1.5,
      borderRadius: 6,
    }],
  }
  const opts = {
    responsive: true, maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: { legend: { display: false }, tooltip: {
      backgroundColor: '#111827', bodyColor: '#d1d5db', borderColor: '#374151', borderWidth: 1,
      callbacks: { label: ctx => `${ctx.parsed.x.toFixed(1)} km` },
    }},
    scales: {
      x: { grid: { color: 'rgba(31,41,55,0.8)' }, ticks: { color: '#6b7280', callback: v => `${v} km` } },
      y: { grid: { display: false }, ticks: { color: '#9ca3af' } },
    },
    animation: { duration: 800 },
  }
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
      <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-4">Route Distances</p>
      <div style={{ height: 100 }}>
        <Bar data={data} options={opts} />
      </div>
    </div>
  )
}

/* ── Sustainability Bars ───────────────────────────────────────────────────── */
function SustainBar({ label, pct, color }) {
  const positive = pct != null && pct > 0.05
  const negative = pct != null && pct < -0.05
  const barColor = positive ? '#10b981' : negative ? '#ef4444' : '#eab308'
  const barW = pct != null ? Math.min(Math.abs(pct), 100) : 0
  const sign = positive ? '−' : (negative ? '+' : '±')
  const display = pct != null ? `${sign}${Math.abs(pct).toFixed(1)}%` : '—'
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-gray-500 text-xs">{label}</span>
        <span className={`text-xs font-bold ${positive ? 'text-green-400' : negative ? 'text-red-400' : 'text-yellow-400'}`}>
          {display}
        </span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${barW}%`, backgroundColor: barColor }}
        />
      </div>
    </div>
  )
}

/* ── Main page ─────────────────────────────────────────────────────────────── */
export default function Analytics() {
  const navigate  = useNavigate()
  const { uploadedFile, analyticsResult, setAnalyticsResult } = useApp()

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  async function handleFetch() {
    if (!uploadedFile) return
    setLoading(true)
    setError(null)
    try {
      const data = await getAnalytics()
      setAnalyticsResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Analytics fetch failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (uploadedFile && !analyticsResult && !loading) handleFetch()
  }, [uploadedFile]) // eslint-disable-line

  const d = analyticsResult

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="text-gray-400 hover:text-white transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Activity size={22} className="text-green-400" />
              Analytics
            </h1>
            <p className="text-gray-400 text-sm mt-0.5">Fleet · Routing · Sustainability · QUBO KPIs</p>
          </div>
        </div>

        <button
          onClick={handleFetch}
          disabled={loading || !uploadedFile}
          className="flex items-center gap-2 bg-green-700 hover:bg-green-600 disabled:opacity-40
            disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <RefreshCw size={15} />}
          {loading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {/* Guards */}
      {!uploadedFile && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4 text-gray-400">
          <AlertCircle size={18} className="shrink-0 text-yellow-400" />
          <span className="text-sm">No dataset uploaded. Go to <button onClick={() => navigate('/upload')} className="text-green-400 underline">Upload</button> first.</span>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 text-red-400 text-sm bg-red-900/20 border border-red-800/50 rounded-xl px-4 py-3">
          <AlertCircle size={15} className="mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
          <Loader2 size={18} className="animate-spin text-green-400 shrink-0" />
          <span className="text-gray-300 text-sm">Fetching analytics…</span>
        </div>
      )}

      {/* ── Analytics content ── */}
      {d && !loading && (
        <div className="space-y-8">

          {/* Fleet — KPIs + donut */}
          {d.fleet && (
            <section>
              <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Fleet</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <KpiCard label="Vehicles Used"   icon={Truck}  color="text-purple-400"
                  value={d.fleet.vehicles_used}
                  sub={`of ${d.fleet.total_vehicles_configured} configured`} />
                <KpiCard label="Avg Utilisation" icon={Truck}  color="text-blue-400"
                  value={d.fleet.average_utilization_pct != null ? `${d.fleet.average_utilization_pct}%` : '—'}
                  warn={d.fleet.average_utilization_pct > 90}
                  sub={d.fleet.average_utilization_pct > 90 ? 'Fleet near capacity' : 'Capacity headroom OK'} />
                <UtilizationDonut
                  pct={d.fleet.average_utilization_pct}
                  vehiclesUsed={d.fleet.vehicles_used}
                  total={d.fleet.total_vehicles_configured}
                />
              </div>
            </section>
          )}

          {/* Routing — KPIs + bar chart */}
          {d.routing && (
            <section>
              <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Routing</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <KpiCard label="Avg Route"     icon={Route} color="text-yellow-400"
                  value={`${d.routing.average_route_km} km`} sub="per vehicle" />
                <KpiCard label="Longest Route" icon={Route} color="text-orange-400"
                  value={`${d.routing.longest_route_km} km`} sub="worst-case vehicle" />
                <KpiCard label="Solver Used"   icon={Cpu}   color="text-green-400"
                  value={d.routing.solver_used === 'quantum' ? 'Quantum' : 'Classical'}
                  sub="routes shown on map" />
                <RouteBar avg={d.routing.average_route_km} longest={d.routing.longest_route_km} />
              </div>
            </section>
          )}

          {/* Customers */}
          {d.customers && (
            <Section title="Customers">
              <KpiCard label="Delivered"     icon={Users} color="text-green-400"
                value={d.customers.delivered} sub={`of ${d.customers.total} total`} />
              <KpiCard label="Delivery Rate" icon={Users} color="text-blue-400"
                value={`${((d.customers.delivered / d.customers.total) * 100).toFixed(0)}%`}
                warn={d.customers.delivered < d.customers.total}
                sub={d.customers.delivered < d.customers.total ? 'Some customers unserved' : 'All customers served'} />
            </Section>
          )}

          {/* Optimization */}
          {d.optimization && (
            <Section title="Optimization (QUBO)">
              <KpiCard label="Runtime"      icon={Cpu} color="text-purple-400"
                value={`${d.optimization.runtime_s ?? '—'} s`} sub="solver wall-time" />
              <KpiCard label="Runs"         icon={Cpu} color="text-blue-400"
                value={d.optimization.runs ?? '—'} sub="solver restarts" />
              <KpiCard label="Obj Best"     icon={Cpu} color="text-green-400"
                value={d.optimization.objective_best != null ? Number(d.optimization.objective_best).toFixed(2) : '—'}
                sub="QUBO energy" />
              <KpiCard label="Obj Variance" icon={Cpu} color="text-yellow-400"
                value={d.optimization.objective_variance != null ? Number(d.optimization.objective_variance).toFixed(4) : '—'}
                sub="across runs" />
            </Section>
          )}

          {/* Sustainability — KPIs + animated bars */}
          {d.sustainability && (
            <section>
              <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Sustainability</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="grid grid-cols-2 gap-3">
                  <KpiCard label="Fuel" icon={Leaf} color="text-orange-400"
                    value={d.sustainability.fuel_l != null ? `${Number(d.sustainability.fuel_l).toFixed(2)} L` : '—'} />
                  <KpiCard label="CO₂" icon={Leaf} color="text-green-400"
                    value={d.sustainability.co2_kg != null ? `${Number(d.sustainability.co2_kg).toFixed(2)} kg` : '—'} />
                </div>

                {/* Quantum-vs-classical saving bars */}
                {(d.sustainability.co2_saved_pct != null || d.sustainability.distance_saved_pct != null) && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 space-y-3">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingDown size={15} className="text-green-400" />
                      <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">
                        Quantum vs Classical
                      </p>
                    </div>
                    <SustainBar label="Distance saved" pct={d.sustainability.distance_saved_pct} />
                    <SustainBar label="CO₂ saved"      pct={d.sustainability.co2_saved_pct} />
                  </div>
                )}
              </div>
            </section>
          )}

        </div>
      )}

      {/* Empty state */}
      {!loading && !error && !d && uploadedFile && (
        <div className="text-center py-16 text-gray-600">
          <Activity size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-gray-500">Run at least one solver on the <button onClick={() => navigate('/dashboard')} className="text-green-400 underline">Dashboard</button> to see analytics.</p>
        </div>
      )}

    </div>
  )
}
