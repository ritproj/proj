import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, Info, Zap, Truck, Bike, Package, Download } from 'lucide-react'
import UploadBox from '../components/UploadBox'
import { useApp, DEFAULT_VEHICLE_CONFIG } from '../context/AppContext'
import { uploadDataset } from '../services/optimization'

// ── Demo presets ───────────────────────────────────────────────────────────
const DEMO_PRESETS = [
  {
    id: 'small',
    label: 'Small (8 customers)',
    desc: 'Quantum-win dataset · 2× Van @ 68 kg',
    fleet: { Van: 2, Truck: 0, Bike: 0, 'Electric Van': 0 },
    capacities: { Van: 68, Truck: 120, Bike: 15, 'Electric Van': 60 },
    csv: `Customer_ID,Latitude,Longitude,Demand
1,11.0174,76.9198,10
2,10.9825,76.9351,19
3,10.9666,76.9689,20
4,11.0376,76.9826,18
5,11.0051,76.9811,11
6,11.0115,76.9859,18
7,11.0061,76.9120,17
8,10.9980,76.9690,10
`,
  },
  {
    id: 'medium',
    label: 'Medium (15 customers)',
    desc: 'Clustered BQPhy demo · 3× Van @ 75 kg',
    fleet: { Van: 3, Truck: 0, Bike: 0, 'Electric Van': 0 },
    capacities: { Van: 75, Truck: 120, Bike: 15, 'Electric Van': 60 },
    csv: `Customer_ID,Latitude,Longitude,Demand
1,11.0174,76.9198,10
2,10.9825,76.9351,19
3,10.9666,76.9689,20
4,11.0376,76.9826,18
5,11.0051,76.9811,11
6,11.0115,76.9859,18
7,11.0061,76.9120,17
8,10.9980,76.9690,10
9,11.0250,76.9500,14
10,11.0050,76.9200,12
11,10.9900,76.9750,16
12,11.0300,76.9650,11
13,10.9750,76.9400,13
14,11.0150,76.9350,15
15,11.0000,76.9600,10
`,
  },
  {
    id: 'mixed',
    label: 'Mixed Fleet (10 customers)',
    desc: 'Van + Electric Van + Bike combo',
    fleet: { Van: 1, Truck: 0, Bike: 1, 'Electric Van': 1 },
    capacities: { Van: 60, Truck: 120, Bike: 15, 'Electric Van': 60 },
    csv: `Customer_ID,Latitude,Longitude,Demand
1,11.0174,76.9198,8
2,10.9825,76.9351,12
3,10.9666,76.9689,10
4,11.0376,76.9826,5
5,11.0051,76.9811,7
6,11.0115,76.9859,9
7,11.0061,76.9120,11
8,10.9980,76.9690,6
9,11.0250,76.9500,8
10,11.0050,76.9200,4
`,
  },
]

const SAMPLE_CSV = DEMO_PRESETS[0].csv

// Recommended fleet for this sample: 2× Van @ 68 kg
// Total demand = 123 kg, fleet capacity = 136 kg (utilisation ~90%)
// Quantum (exhaustive QUBO on 16 vars) matches OR-Tools exactly on this dataset.
function downloadSampleCSV() {
  const blob = new Blob([SAMPLE_CSV], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = 'sample_customers.csv'
  a.click()
  URL.revokeObjectURL(url)
}

const VEHICLE_TYPES = [
  { key: 'Van',          label: 'Van',          icon: Package, color: 'text-blue-400',   rate: '0.11 L/km' },
  { key: 'Truck',        label: 'Truck',         icon: Truck,   color: 'text-orange-400', rate: '0.18 L/km' },
  { key: 'Bike',         label: 'Bike',          icon: Bike,    color: 'text-green-400',  rate: '0.03 L/km' },
  { key: 'Electric Van', label: 'Electric Van',  icon: Zap,     color: 'text-purple-400', rate: '0.00 L/km' },
]

export default function Upload() {
  const navigate = useNavigate()
  const {
    setUploadedFile, setParsedCustomers,
    vehicleConfig, setVehicleConfig,
    setShowClusteringNotice, setFleetCheck,
    setError: setGlobalError,
  } = useApp()

  const [csvError,     setCsvError]     = useState(null)
  const [pendingFile,  setPendingFile]  = useState(null)
  const [pendingRows,  setPendingRows]  = useState([])
  const [pendingCluster, setPendingCluster] = useState(false)
  const [submitting,   setSubmitting]   = useState(false)
  const [submitError,  setSubmitError]  = useState(null)

  // Local string state for capacity inputs so fields can be fully cleared while typing
  const [capStrings, setCapStrings] = useState(() => {
    const init = {}
    VEHICLE_TYPES.forEach(({ key }) => {
      init[key] = String(DEFAULT_VEHICLE_CONFIG.capacities[key] ?? 50)
    })
    return init
  })

  const fleet      = vehicleConfig.fleet      ?? DEFAULT_VEHICLE_CONFIG.fleet
  const capacities = vehicleConfig.capacities ?? DEFAULT_VEHICLE_CONFIG.capacities
  const totalVehicles = Object.values(fleet).reduce((s, n) => s + n, 0)

  function setFleetCount(type, raw) {
    const n = Math.max(0, Math.min(20, parseInt(raw) || 0))
    setVehicleConfig(prev => ({
      ...prev,
      fleet: { ...(prev.fleet ?? DEFAULT_VEHICLE_CONFIG.fleet), [type]: n },
    }))
  }

  // While typing: update the string display only
  function handleCapChange(type, raw) {
    setCapStrings(prev => ({ ...prev, [type]: raw }))
  }

  // On blur: commit the parsed value (minimum 1) to context
  function handleCapBlur(type) {
    const parsed = parseInt(capStrings[type])
    const value  = isNaN(parsed) || parsed < 1 ? 1 : parsed
    setCapStrings(prev => ({ ...prev, [type]: String(value) }))
    setVehicleConfig(prev => ({
      ...prev,
      capacities: { ...(prev.capacities ?? DEFAULT_VEHICLE_CONFIG.capacities), [type]: value },
    }))
  }

  function handleFileAccepted(file, rows, clusterNotice) {
    setPendingFile(file); setPendingRows(rows)
    setPendingCluster(clusterNotice); setCsvError(null)
  }

  function loadPreset(preset) {
    // Parse CSV rows
    const lines = preset.csv.trim().split('\n')
    const headers = lines[0].split(',')
    const rows = lines.slice(1).map(line => {
      const vals = line.split(',')
      const obj = {}
      headers.forEach((h, i) => { obj[h.trim()] = vals[i]?.trim() })
      return obj
    })
    // Create a File object from the CSV string
    const blob = new Blob([preset.csv], { type: 'text/csv' })
    const file = new File([blob], `${preset.id}_demo.csv`, { type: 'text/csv' })
    setPendingFile(file)
    setPendingRows(rows)
    setPendingCluster(rows.length > 50)
    setCsvError(null)
    setSubmitError(null)
    // Update fleet config
    setVehicleConfig({ fleet: preset.fleet, capacities: preset.capacities })
    setCapStrings(
      Object.fromEntries(Object.entries(preset.capacities).map(([k, v]) => [k, String(v)]))
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!pendingFile)         { setCsvError('Please select a CSV file.'); return }
    if (totalVehicles < 1)    { setSubmitError('Add at least 1 vehicle.'); return }

    setSubmitting(true); setSubmitError(null); setGlobalError(null)

    try {
      const res = await uploadDataset(pendingFile, { fleet, capacities })
      setUploadedFile(pendingFile)
      setParsedCustomers(pendingRows)
      setShowClusteringNotice(pendingCluster)
      if (res.fleet_check) setFleetCheck(res.fleet_check)
      navigate('/dashboard')
    } catch (err) {
      setSubmitError(err?.response?.data?.detail || err.message || 'Upload failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-white mb-1">Upload Dataset</h1>
      <p className="text-gray-400 text-sm mb-6">Provide your CSV and configure the fleet.</p>

      {/* ── Demo Presets ── */}
      <div className="mb-6">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Quick Demo</p>
        <div className="grid grid-cols-3 gap-2">
          {DEMO_PRESETS.map(preset => (
            <button
              key={preset.id}
              id={`preset-${preset.id}`}
              type="button"
              onClick={() => loadPreset(preset)}
              className={`text-left border rounded-xl px-3 py-2.5 transition-all duration-150 group
                ${ pendingFile?.name === `${preset.id}_demo.csv`
                  ? 'bg-green-900/30 border-green-700/60 text-green-300'
                  : 'bg-gray-900 border-gray-700 hover:border-green-700/50 hover:bg-gray-800 text-gray-300 hover:text-white'
                }`}
            >
              <p className="text-xs font-semibold leading-tight">{preset.label}</p>
              <p className="text-gray-500 text-xs mt-0.5 leading-tight group-hover:text-gray-400">{preset.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* ── CSV Upload ── */}
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Upload CSV</h2>
          <UploadBox onFileAccepted={handleFileAccepted} onError={setCsvError} />

          {/* Sample CSV download */}
          <button
            type="button"
            onClick={downloadSampleCSV}
            className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-green-400 transition-colors"
          >
            <Download size={13} />
            Download sample CSV (8 customers · use 2× Van @ 68 kg)
          </button>
          {csvError && (
            <div className="flex items-start gap-2 text-red-400 text-sm bg-red-900/20 border border-red-800/50 rounded-lg px-3 py-2">
              <AlertCircle size={15} className="mt-0.5 shrink-0" /><span>{csvError}</span>
            </div>
          )}
          {pendingCluster && !csvError && (
            <div className="flex items-start gap-2 text-yellow-300 text-sm bg-yellow-900/20 border border-yellow-700/50 rounded-lg px-3 py-2">
              <Info size={15} className="mt-0.5 shrink-0" />
              <span>Large dataset — BQPhy supports up to 50 customers directly; above that, k-means clustering splits into sub-groups solved in parallel.</span>
            </div>
          )}
          {pendingRows.length > 0 && !csvError && (
            <div className="flex items-center justify-between text-xs">
              <p className="text-green-400">{pendingRows.length} customers loaded.</p>
              {(() => {
                const totalDemand = pendingRows.reduce((s, r) => s + (parseFloat(r.Demand) || 0), 0)
                return <p className="text-gray-500">Total demand: <span className="text-gray-300">{totalDemand.toFixed(0)} kg</span></p>
              })()}
            </div>
          )}
        </section>

        {/* ── Fleet Configuration ── */}
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Fleet Configuration</h2>
            {totalVehicles > 0 && (
              <span className="text-xs text-green-400 font-medium">
                {totalVehicles} vehicle{totalVehicles !== 1 ? 's' : ''} total
              </span>
            )}
          </div>

          {/* Header row */}
          <div className="grid grid-cols-[1fr_auto_auto] gap-x-3 gap-y-0 items-center text-xs text-gray-500 uppercase tracking-wider px-1 pb-1 border-b border-gray-800">
            <span>Type</span>
            <span className="w-24 text-center">Count</span>
            <span className="w-24 text-center">Capacity (kg)</span>
          </div>

          {/* Per-type rows */}
          {VEHICLE_TYPES.map(({ key, label, icon: Icon, color, rate }) => (
            <div key={key} className="grid grid-cols-[1fr_auto_auto] gap-x-3 items-center">
              {/* Label */}
              <div className="flex items-center gap-2 min-w-0">
                <Icon size={15} className={color} />
                <div className="min-w-0">
                  <p className="text-gray-200 text-sm font-medium leading-none">{label}</p>
                  <p className="text-gray-600 text-xs mt-0.5">{rate}</p>
                </div>
              </div>

              {/* Count stepper */}
              <div className="flex items-center gap-1 w-24 justify-center">
                <button type="button"
                  onClick={() => setFleetCount(key, (fleet[key] ?? 0) - 1)}
                  className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 text-white text-sm font-bold flex items-center justify-center transition-colors">−</button>
                <input type="number" min={0} max={20}
                  value={fleet[key] ?? 0}
                  onChange={e => setFleetCount(key, e.target.value)}
                  className="w-9 text-center bg-gray-800 border border-gray-700 text-white rounded py-0.5 text-sm focus:outline-none focus:ring-1 focus:ring-green-500" />
                <button type="button"
                  onClick={() => setFleetCount(key, (fleet[key] ?? 0) + 1)}
                  className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 text-white text-sm font-bold flex items-center justify-center transition-colors">+</button>
              </div>

              {/* Capacity input — only active when count > 0 */}
              <div className="w-24">
                <input type="number" min={1}
                  value={capStrings[key] ?? '50'}
                  disabled={(fleet[key] ?? 0) === 0}
                  onChange={e => handleCapChange(key, e.target.value)}
                  onBlur={() => handleCapBlur(key)}
                  className="w-full text-center bg-gray-800 border border-gray-700 text-white rounded py-1 text-sm
                    focus:outline-none focus:ring-1 focus:ring-green-500
                    disabled:opacity-30 disabled:cursor-not-allowed" />
              </div>
            </div>
          ))}

          {totalVehicles === 0 && (
            <p className="text-yellow-400 text-xs text-center">Add at least 1 vehicle to continue.</p>
          )}

          {/* Live demand vs capacity summary */}
          {totalVehicles > 0 && pendingRows.length > 0 && (() => {
            const totalDemand   = pendingRows.reduce((s, r) => s + (parseFloat(r.Demand) || 0), 0)
            const totalCapacity = Object.entries(fleet)
              .reduce((s, [type, cnt]) => s + cnt * (capacities[type] ?? 0), 0)
            const pct = totalCapacity > 0 ? (totalDemand / totalCapacity * 100).toFixed(0) : null
            const ok  = totalCapacity >= totalDemand
            return (
              <div className={`flex items-center justify-between text-xs rounded-lg px-3 py-2 ${
                ok ? 'bg-green-900/20 border border-green-800/40 text-green-400'
                   : 'bg-red-900/20 border border-red-800/40 text-red-400'
              }`}>
                <span>{ok ? '✓ Fleet capacity sufficient' : '✗ Fleet capacity insufficient'}</span>
                <span className="font-mono">
                  {totalDemand.toFixed(0)} kg demand / {totalCapacity.toFixed(0)} kg capacity
                  {pct && ` (${pct}%)`}
                </span>
              </div>
            )
          })()}
        </section>

        {submitError && (
          <div className="flex items-start gap-2 text-red-400 text-sm bg-red-900/20 border border-red-800/50 rounded-lg px-3 py-2">
            <AlertCircle size={15} className="mt-0.5 shrink-0" /><span>{submitError}</span>
          </div>
        )}

        <button type="submit"
          disabled={!pendingFile || !!csvError || submitting || totalVehicles < 1}
          className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500
            disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl
            transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-400">
          <Zap size={17} />
          {submitting ? 'Uploading...' : 'Run Optimization'}
        </button>
      </form>
    </div>
  )
}
