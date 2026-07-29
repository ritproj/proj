import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, RefreshCw, Loader2, AlertCircle, ArrowLeft,
         Truck, Route, Users, Cpu, Leaf } from 'lucide-react'
import { useApp } from '../context/AppContext'
import { getAnalytics } from '../services/analytics'

function KpiCard({ label, value, sub, icon: Icon, color = 'text-green-400', warn = false }) {
  return (
    <div className={`bg-gray-900 border ${warn ? 'border-yellow-700/60' : 'border-gray-800'} rounded-xl px-5 py-4 flex flex-col gap-2`}>
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

  React.useEffect(() => {
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
            <p className="text-gray-400 text-sm mt-0.5">Fleet · Routing · Sustainability KPIs</p>
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

      {/* Analytics sections */}
      {d && !loading && (
        <div className="space-y-8">

          {/* Fleet */}
          {d.fleet && (
            <Section title="Fleet">
              <KpiCard label="Vehicles Used"    icon={Truck}   color="text-purple-400"
                value={d.fleet.vehicles_used}
                sub={`of ${d.fleet.total_vehicles_configured} configured`} />
              <KpiCard label="Avg Utilisation"  icon={Truck}   color="text-blue-400"
                value={d.fleet.average_utilization_pct != null ? `${d.fleet.average_utilization_pct}%` : '—'}
                warn={d.fleet.average_utilization_pct > 90}
                sub={d.fleet.average_utilization_pct > 90 ? 'Fleet near capacity' : 'Capacity headroom OK'} />
            </Section>
          )}

          {/* Routing */}
          {d.routing && (
            <Section title="Routing">
              <KpiCard label="Avg Route"       icon={Route}  color="text-yellow-400"
                value={`${d.routing.average_route_km} km`}
                sub="per vehicle" />
              <KpiCard label="Longest Route"   icon={Route}  color="text-orange-400"
                value={`${d.routing.longest_route_km} km`}
                sub="worst-case vehicle" />
              <KpiCard label="Solver Used"     icon={Cpu}    color="text-green-400"
                value={d.routing.solver_used === 'quantum' ? 'Quantum' : 'Classical'}
                sub="routes shown on map" />
            </Section>
          )}

          {/* Customers */}
          {d.customers && (
            <Section title="Customers">
              <KpiCard label="Delivered"       icon={Users}  color="text-green-400"
                value={d.customers.delivered}
                sub={`of ${d.customers.total} total`} />
              <KpiCard label="Delivery Rate"   icon={Users}  color="text-blue-400"
                value={`${((d.customers.delivered / d.customers.total) * 100).toFixed(0)}%`}
                warn={d.customers.delivered < d.customers.total}
                sub={d.customers.delivered < d.customers.total ? 'Some customers unserved' : 'All customers served'} />
            </Section>
          )}

          {/* Optimization */}
          {d.optimization && (
            <Section title="Optimization (QUBO)">
              <KpiCard label="Runtime"         icon={Cpu}    color="text-purple-400"
                value={`${d.optimization.runtime_s ?? '—'} s`}
                sub="solver wall-time" />
              <KpiCard label="Runs"            icon={Cpu}    color="text-blue-400"
                value={d.optimization.runs ?? '—'}
                sub="SA restarts" />
              <KpiCard label="Obj Best"        icon={Cpu}    color="text-green-400"
                value={d.optimization.objective_best != null ? Number(d.optimization.objective_best).toFixed(2) : '—'}
                sub="QUBO energy" />
              <KpiCard label="Obj Variance"    icon={Cpu}    color="text-yellow-400"
                value={d.optimization.objective_variance != null ? Number(d.optimization.objective_variance).toFixed(4) : '—'}
                sub="across runs" />
            </Section>
          )}

          {/* Sustainability */}
          {d.sustainability && (
            <Section title="Sustainability">
              <KpiCard label="Fuel"            icon={Leaf}   color="text-orange-400"
                value={d.sustainability.fuel_l != null ? `${Number(d.sustainability.fuel_l).toFixed(2)} L` : '—'} />
              <KpiCard label="CO₂"             icon={Leaf}   color="text-green-400"
                value={d.sustainability.co2_kg != null ? `${Number(d.sustainability.co2_kg).toFixed(2)} kg` : '—'} />
              <KpiCard label="CO₂ Saved"       icon={Leaf}   color="text-green-400"
                value={d.sustainability.co2_saved_pct != null ? `${d.sustainability.co2_saved_pct > 0 ? '-' : '+'}${Math.abs(d.sustainability.co2_saved_pct).toFixed(1)}%` : '—'}
                sub="quantum vs classical" />
              <KpiCard label="Distance Saved"  icon={Leaf}   color="text-blue-400"
                value={d.sustainability.distance_saved_pct != null ? `${d.sustainability.distance_saved_pct > 0 ? '-' : '+'}${Math.abs(d.sustainability.distance_saved_pct).toFixed(1)}%` : '—'}
                sub="quantum vs classical" />
            </Section>
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
