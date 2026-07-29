import React, { useEffect, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Users, Truck, Route, Fuel, Wind,
  Play, Atom, GitCompare, RotateCcw, Loader2,
  AlertCircle, BarChart2, Activity, CheckCircle2,
  AlertTriangle, Cpu, Hash,
} from 'lucide-react'
import { useApp } from '../context/AppContext'
import { runClassical, runQuantum, compareResults } from '../services/optimization'
import StatsCard from '../components/StatsCard'
import SustainabilitySummary from '../components/SustainabilitySummary'
import RouteMap from '../components/RouteMap'
import ComparisonTable from '../components/ComparisonTable'
import ResultChart from '../components/ResultChart'
import ErrorBanner from '../components/ErrorBanner'

function Spinner() {
  return <Loader2 size={16} className="animate-spin" />
}

/** Per-route breakdown row — uses backend route_meta for accuracy */
function RouteRow({ idx, meta }) {
  if (!meta) return null

  const { vehicle, type, stops, load_kg, capacity_kg, load_pct, distance_km } = meta
  const barColor = (load_pct ?? 0) >= 90 ? 'bg-red-500'
    : (load_pct ?? 0) >= 70 ? 'bg-yellow-500'
    : 'bg-green-500'

  return (
    <tr className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
      <td className="px-4 py-3 text-gray-300 font-medium">
        Vehicle {vehicle}
        {type && <span className="ml-2 text-gray-600 text-xs font-normal">({type})</span>}
      </td>
      <td className="px-4 py-3 text-center text-white">{stops}</td>
      <td className="px-4 py-3 text-center text-white">{distance_km != null ? `${distance_km} km` : '—'}</td>
      <td className="px-4 py-3 text-center text-white">{load_kg != null ? `${load_kg} kg` : '—'}</td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${barColor}`}
              style={{ width: `${Math.min(load_pct ?? 0, 100)}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 w-9 text-right">
            {load_pct != null ? `${load_pct}%` : '—'}
          </span>
        </div>
      </td>
    </tr>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const {
    uploadedFile,
    parsedCustomers,
    vehicleConfig,
    fleetCheck,
    classicalResult, setClassicalResult,
    quantumResult,   setQuantumResult,
    comparisonResult, setComparisonResult,
    loadingState, setLoadingState,
    error, setError,
    showClusteringNotice,
    reset,
  } = useApp()

  useEffect(() => {
    if (!uploadedFile) navigate('/upload', { replace: true })
  }, [uploadedFile, navigate])

  // ── Auto-compare whenever both solvers have results ───────────────────────
  useEffect(() => {
    if (classicalResult && quantumResult && !comparisonResult && !loadingState) {
      handleCompare()
    }
  }, [classicalResult, quantumResult]) // eslint-disable-line

  // ── Action handlers ──────────────────────────────────────────────────────

  async function handleRunClassical() {
    setLoadingState('classical')
    setError(null)
    try {
      const data = await runClassical()
      setClassicalResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Classical optimization failed.')
    } finally {
      setLoadingState(null)
    }
  }

  async function handleRunQuantum() {
    setLoadingState('quantum')
    setError(null)
    try {
      const data = await runQuantum()
      setQuantumResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Quantum optimization failed.')
    } finally {
      setLoadingState(null)
    }
  }

  async function handleCompare() {
    setLoadingState('compare')
    setError(null)
    try {
      const data = await compareResults()
      setComparisonResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Comparison failed.')
    } finally {
      setLoadingState(null)
    }
  }

  function handleReset() {
    reset()
    navigate('/upload')
  }

  // ── Derived display data ──────────────────────────────────────────────────

  const activeResult   = quantumResult ?? classicalResult
  const { depot, customers } = useMemo(() => {
    const r = activeResult
    if (!r) return { depot: null, customers: [] }
    return { depot: r.depot ?? null, customers: r.customers ?? [] }
  }, [activeResult])

  const statsSource    = activeResult?.stats ?? null
  const customerCount  = parsedCustomers.length || (statsSource?.customers ?? '—')

  const savings  = comparisonResult?.savings ?? null
  const co2Saved =
    classicalResult?.stats?.co2_kg && quantumResult?.stats?.co2_kg
      ? classicalResult.stats.co2_kg - quantumResult.stats.co2_kg
      : null

  const loading = loadingState !== null

  const loadingLabel = {
    classical: 'Running OR-Tools…',
    quantum:   'Generating QUBO & Solving…',
    compare:   'Comparing results…',
  }[loadingState] ?? ''

  const quantumFallback   = quantumResult?.fallback_used === true
  const quantumInfeasible = quantumResult?.feasible === false

  // Fleet capacity warning from upload pre-check
  const fleetWarning = fleetCheck?.warning ?? null
  const fleetOk      = fleetCheck?.sufficient !== false

  // Per-vehicle capacity list
  const capList = vehicleConfig?.capacities

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">

      {/* ── Page header ── */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {uploadedFile?.name} · {
              Object.entries(vehicleConfig?.fleet ?? {})
                .filter(([, v]) => v > 0)
                .map(([k, v]) => `${v}× ${k} (${vehicleConfig?.capacities?.[k] ?? '?'} kg)`)
                .join(', ')
            }
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleRunClassical}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-700 hover:bg-blue-600 disabled:opacity-40
              disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            {loadingState === 'classical' ? <Spinner /> : <Play size={15} />}
            {loadingState === 'classical' ? 'Running OR-Tools…' : 'Run Classical'}
          </button>

          <button
            onClick={handleRunQuantum}
            disabled={loading}
            className="flex items-center gap-2 bg-purple-700 hover:bg-purple-600 disabled:opacity-40
              disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            {loadingState === 'quantum' ? <Spinner /> : <Atom size={15} />}
            {loadingState === 'quantum' ? loadingLabel : 'Run Quantum'}
          </button>

          <button
            onClick={handleCompare}
            disabled={loading || (!classicalResult && !quantumResult)}
            className="flex items-center gap-2 bg-green-700 hover:bg-green-600 disabled:opacity-40
              disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            {loadingState === 'compare' ? <Spinner /> : <GitCompare size={15} />}
            {loadingState === 'compare' ? 'Comparing…' : 'Compare'}
          </button>

          <button
            onClick={handleReset}
            disabled={loading}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-40
              disabled:cursor-not-allowed text-gray-200 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <RotateCcw size={15} />
            Reset
          </button>
        </div>
      </div>

      {/* ── v2 Nav links ── */}
      <div className="flex gap-3">
        <Link
          to="/benchmark"
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white bg-gray-800
            hover:bg-gray-700 border border-gray-700 rounded-lg px-3 py-1.5 transition-colors"
        >
          <BarChart2 size={14} />
          Benchmark
        </Link>
        <Link
          to="/analytics"
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white bg-gray-800
            hover:bg-gray-700 border border-gray-700 rounded-lg px-3 py-1.5 transition-colors"
        >
          <Activity size={14} />
          Analytics
        </Link>
      </div>

      {/* ── Fleet capacity warning (from /api/upload pre-check) ── */}
      {fleetCheck && !fleetOk && (
        <div className="flex items-start gap-3 bg-red-900/20 border border-red-700/60 rounded-xl px-4 py-3">
          <AlertTriangle size={18} className="text-red-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-red-300 text-sm font-medium">Fleet capacity insufficient</p>
            <p className="text-red-400/80 text-xs mt-0.5">{fleetWarning}</p>
          </div>
        </div>
      )}
      {fleetCheck && fleetOk && fleetCheck.utilization_pct > 90 && (
        <div className="flex items-start gap-3 bg-yellow-900/20 border border-yellow-700/50 rounded-xl px-4 py-3">
          <AlertCircle size={18} className="text-yellow-400 mt-0.5 shrink-0" />
          <p className="text-yellow-300 text-sm">
            Fleet utilisation is <strong>{fleetCheck.utilization_pct}%</strong> — very tight.
            OR-Tools may time-out finding a feasible solution.
          </p>
        </div>
      )}

      {/* ── Global loading indicator ── */}
      {loading && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3">
          <Loader2 size={18} className="animate-spin text-green-400 shrink-0" />
          <span className="text-gray-300 text-sm">{loadingLabel}</span>
        </div>
      )}

      {/* ── Auto-compare badge ── */}
      {comparisonResult && !loading && (
        <div className="flex items-center gap-2 text-green-400 text-sm bg-green-900/20
          border border-green-700/40 rounded-xl px-4 py-2">
          <CheckCircle2 size={15} className="shrink-0" />
          <span>Comparison complete — winner: <strong>{comparisonResult.winner ?? 'N/A'}</strong></span>
        </div>
      )}

      {/* ── Clustering notice ── */}
      {showClusteringNotice && (
        <div className="flex items-start gap-2 text-yellow-300 text-sm bg-yellow-900/20
          border border-yellow-700/50 rounded-xl px-4 py-3">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span>Dataset will be clustered for quantum demo purposes (QAOA supports 4–8 customers per instance).</span>
        </div>
      )}

      {/* ── Quantum infeasible / fallback badge ── */}
      {quantumResult && (quantumFallback || quantumInfeasible) && (
        <div className="flex items-start gap-2 text-orange-300 text-sm bg-orange-900/20
          border border-orange-700/50 rounded-xl px-4 py-3">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span>
            Fallback heuristic used — QAOA did not converge to a feasible route on this run.
            Results may differ from optimal.
          </span>
        </div>
      )}

      {/* ── Error banner ── */}
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* ── Statistics — side-by-side when both solvers ran ── */}
      {(statsSource || parsedCustomers.length > 0) && (
        <section>
          <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Statistics</h2>
          {classicalResult && quantumResult ? (
            /* Both ran — show two columns */
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Classical column */}
              <div className="bg-gray-900 border border-blue-900/50 rounded-2xl p-4 space-y-3">
                <p className="text-blue-400 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                  <Play size={11} /> Classical
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'Distance', value: classicalResult.stats?.distance_km, unit: 'km' },
                    { label: 'Fuel',     value: classicalResult.stats?.fuel_l,      unit: 'L'  },
                    { label: 'CO₂',      value: classicalResult.stats?.co2_kg,      unit: 'kg' },
                    { label: 'Routes',   value: classicalResult.routes?.length                  },
                    { label: 'Runtime',  value: classicalResult.stats?.runtime_s,   unit: 's'  },
                  ].map(({ label, value, unit }) => (
                    <div key={label} className="text-center">
                      <p className="text-gray-600 text-xs">{label}</p>
                      <p className="text-white text-sm font-bold leading-snug">
                        {value ?? '—'}{unit && value != null ? <span className="text-gray-500 text-xs font-normal"> {unit}</span> : ''}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
              {/* Quantum column */}
              <div className="bg-gray-900 border border-purple-900/50 rounded-2xl p-4 space-y-3">
                <p className="text-purple-400 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                  <Atom size={11} /> Quantum
                  {quantumResult.fallback_used && <span className="text-orange-400 text-xs font-normal">(fallback)</span>}
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'Distance', value: quantumResult.stats?.distance_km, unit: 'km' },
                    { label: 'Fuel',     value: quantumResult.stats?.fuel_l,      unit: 'L'  },
                    { label: 'CO₂',      value: quantumResult.stats?.co2_kg,      unit: 'kg' },
                    { label: 'Routes',   value: quantumResult.routes?.length                  },
                    { label: 'Runtime',  value: quantumResult.stats?.runtime_s,   unit: 's'  },
                  ].map(({ label, value, unit }) => (
                    <div key={label} className="text-center">
                      <p className="text-gray-600 text-xs">{label}</p>
                      <p className="text-white text-sm font-bold leading-snug">
                        {value ?? '—'}{unit && value != null ? <span className="text-gray-500 text-xs font-normal"> {unit}</span> : ''}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Single solver — classic card row */
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              <StatsCard label="Customers"  value={customerCount}                    icon={Users}  color="text-blue-400" />
              <StatsCard label="Vehicles"   value={statsSource?.vehicles ?? Object.values(vehicleConfig?.fleet ?? {}).reduce((s, n) => s + n, 0)} icon={Truck}  color="text-purple-400" />
              <StatsCard label="Distance"   value={statsSource?.distance_km ?? '—'}  unit="km"     icon={Route} color="text-yellow-400" />
              <StatsCard label="Fuel"       value={statsSource?.fuel_l      ?? '—'}  unit="L"      icon={Fuel}  color="text-orange-400" />
              <StatsCard label="CO₂"        value={statsSource?.co2_kg      ?? '—'}  unit="kg"     icon={Wind}  color="text-green-400" />
            </div>
          )}
        </section>
      )}

      {/* ── QUBO info panel ── */}
      {quantumResult && (
        <section>
          <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">QUBO Solver Info</h2>
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5
            grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              {
                label: 'Variables',
                value: quantumResult.n_vars ?? '—',
                icon: Hash,
                color: 'text-purple-400',
                sub: 'N × K qubits',
              },
              {
                label: 'Method',
                value: quantumResult.method === 'exhaustive'
                  ? 'Exhaustive'
                  : quantumResult.method === 'simulated_annealing'
                  ? 'Sim. Annealing'
                  : 'NN Fallback',
                icon: Cpu,
                color: quantumResult.method === 'exhaustive' ? 'text-green-400'
                  : quantumResult.method === 'simulated_annealing' ? 'text-yellow-400'
                  : 'text-orange-400',
                sub: quantumResult.method === 'exhaustive'
                  ? 'exact (≤16 vars)'
                  : quantumResult.method === 'simulated_annealing'
                  ? 'heuristic'
                  : 'no QUBO solved',
              },
              {
                label: 'Obj Best',
                value: quantumResult.objective_best != null
                  ? Number(quantumResult.objective_best).toFixed(2)
                  : '—',
                icon: Cpu,
                color: 'text-blue-400',
                sub: 'lowest QUBO energy',
              },
              {
                label: 'Obj Mean',
                value: quantumResult.objective_mean != null
                  ? Number(quantumResult.objective_mean).toFixed(2)
                  : '—',
                icon: Cpu,
                color: 'text-gray-400',
                sub: `${quantumResult.runs ?? 1} run${(quantumResult.runs ?? 1) !== 1 ? 's' : ''}`,
              },
            ].map(({ label, value, icon: Icon, color, sub }) => (
              <div key={label} className="flex flex-col gap-1">
                <div className="flex items-center gap-1.5">
                  <Icon size={14} className={color} />
                  <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">{label}</span>
                </div>
                <span className="text-white text-xl font-bold leading-none">{value}</span>
                <span className="text-gray-600 text-xs">{sub}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── Sustainability Summary ── */}
      {(savings || (classicalResult && quantumResult)) && (
        <SustainabilitySummary savings={savings} co2SavedKg={co2Saved} />
      )}

      {/* ── Route Map — pass both results so tab toggle works ── */}
      {(classicalResult || quantumResult) && (
        <section>
          <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Route Map</h2>
          <RouteMap
            depot={depot}
            customers={customers}
            classicalResult={classicalResult}
            quantumResult={quantumResult}
          />
        </section>
      )}

      {/* ── Per-route breakdown table ── */}
      {(() => {
        const activeResult = quantumResult ?? classicalResult
        const routeMeta = activeResult?.route_meta ?? []
        if (routeMeta.length === 0) return null
        const label = quantumResult ? 'quantum' : 'classical'
        return (
          <section>
            <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">
              Route Breakdown
              <span className="ml-2 text-gray-600 normal-case font-normal">({label})</span>
            </h2>
            <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-800">
                    {['Vehicle', 'Stops', 'Distance', 'Load', 'Utilisation'].map(h => (
                      <th key={h} className="text-left text-gray-500 text-xs font-semibold uppercase tracking-wider px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {routeMeta.map((meta, idx) => (
                    <RouteRow key={idx} idx={idx} meta={meta} />
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )
      })()}

      {/* ── Comparison: chart + table ── */}
      {(classicalResult || quantumResult) && (
        <section>
          <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">Comparison</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ResultChart classical={classicalResult?.stats} quantum={quantumResult?.stats} />
            <ComparisonTable
              classical={classicalResult?.stats}
              quantum={quantumResult?.stats}
              winner={comparisonResult?.winner}
            />
          </div>
        </section>
      )}

      {/* ── Empty state ── */}
      {!loading && !classicalResult && !quantumResult && (
        <div className="text-center py-16 text-gray-600">
          <Atom size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-lg font-medium text-gray-500">Ready to optimize</p>
          <p className="text-sm mt-1">
            Click <strong className="text-white">Run Classical</strong> or{' '}
            <strong className="text-white">Run Quantum</strong> to get started.
          </p>
        </div>
      )}
    </div>
  )
}
