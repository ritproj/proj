import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart2, RefreshCw, Loader2, AlertCircle, ArrowLeft } from 'lucide-react'
import { useApp } from '../context/AppContext'
import { getBenchmark } from '../services/benchmark'
import BenchmarkTable from '../components/benchmark/BenchmarkTable'
import DecisionEnginePanel from '../components/benchmark/DecisionEnginePanel'

export default function Benchmark() {
  const navigate = useNavigate()
  const {
    uploadedFile,
    classicalResult,
    quantumResult,
    benchmarkResult, setBenchmarkResult,
  } = useApp()

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const bothRan = classicalResult && quantumResult

  async function handleFetch() {
    setLoading(true)
    setError(null)
    try {
      const data = await getBenchmark()
      setBenchmarkResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Benchmark fetch failed.')
    } finally {
      setLoading(false)
    }
  }

  // Auto-fetch if we have both results but no benchmark yet
  React.useEffect(() => {
    if (bothRan && !benchmarkResult && !loading) {
      handleFetch()
    }
  }, [bothRan]) // eslint-disable-line

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <BarChart2 size={22} className="text-green-400" />
              Benchmark
            </h1>
            <p className="text-gray-400 text-sm mt-0.5">
              Decision Engine verdict · QUBO vs OR-Tools
            </p>
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

      {/* Guard — no dataset */}
      {!uploadedFile && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4 text-gray-400">
          <AlertCircle size={18} className="shrink-0 text-yellow-400" />
          <span className="text-sm">No dataset uploaded. Go to <button onClick={() => navigate('/upload')} className="text-green-400 underline">Upload</button> first.</span>
        </div>
      )}

      {/* Guard — solvers not run */}
      {uploadedFile && !bothRan && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4 text-gray-400">
          <AlertCircle size={18} className="shrink-0 text-yellow-400" />
          <span className="text-sm">
            Run both <strong className="text-white">Classical</strong> and <strong className="text-white">Quantum</strong> solvers on the{' '}
            <button onClick={() => navigate('/dashboard')} className="text-green-400 underline">Dashboard</button> to see the full benchmark.
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 text-red-400 text-sm bg-red-900/20 border border-red-800/50 rounded-xl px-4 py-3">
          <AlertCircle size={15} className="mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
          <Loader2 size={18} className="animate-spin text-green-400 shrink-0" />
          <span className="text-gray-300 text-sm">Fetching benchmark data…</span>
        </div>
      )}

      {/* Main content */}
      {benchmarkResult && !loading && (
        <div className="space-y-6">
          {/* Decision Engine — top of page, most important */}
          <section>
            <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">
              Decision Engine
            </h2>
            <DecisionEnginePanel
              winner={benchmarkResult.winner}
              decision={benchmarkResult.decision}
              quantum={benchmarkResult.quantum}
            />
          </section>

          {/* Full comparison table */}
          <section>
            <h2 className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-3">
              Full Comparison
            </h2>
            <BenchmarkTable
              classical={benchmarkResult.classical}
              quantum={benchmarkResult.quantum}
            />
          </section>
        </div>
      )}

      {/* Empty state — both ran but benchmark not loaded yet */}
      {!loading && !error && !benchmarkResult && bothRan && (
        <div className="text-center py-16 text-gray-600">
          <BarChart2 size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-gray-500">Click <strong className="text-white">Refresh</strong> to load benchmark results.</p>
        </div>
      )}

    </div>
  )
}
