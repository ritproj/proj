import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Leaf, Truck, Fuel, Wind, ChevronRight,
         Upload, Cpu, BarChart2, Atom, GitCompare, Map } from 'lucide-react'

const FEATURES = [
  { icon: Truck,  label: 'Optimize Routes' },
  { icon: Fuel,   label: 'Reduce Fuel' },
  { icon: Wind,   label: 'Reduce Carbon Emission' },
]

const HOW_IT_WORKS = [
  {
    step: '01',
    icon: Upload,
    title: 'Upload CSV',
    desc: 'Drop your customer dataset (lat, lng, demand) and configure your fleet — vans, trucks, bikes, EVs.',
    color: 'text-blue-400',
    bg: 'bg-blue-900/20 border-blue-700/40',
  },
  {
    step: '02',
    icon: Cpu,
    title: 'Classical Solver',
    desc: 'OR-Tools CVRP solves the routing problem using Guided Local Search — production-grade baseline.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-900/20 border-yellow-700/40',
  },
  {
    step: '03',
    icon: Atom,
    title: 'Quantum QUBO',
    desc: 'The same problem is encoded as a QUBO matrix and solved via exhaustive enumeration or Simulated Annealing — the quantum-inspired approach.',
    color: 'text-purple-400',
    bg: 'bg-purple-900/20 border-purple-700/40',
  },
  {
    step: '04',
    icon: GitCompare,
    title: 'Compare & Decide',
    desc: 'The Decision Engine scores both solvers on distance and runtime, picks a winner, and explains why.',
    color: 'text-green-400',
    bg: 'bg-green-900/20 border-green-700/40',
  },
  {
    step: '05',
    icon: Map,
    title: 'Visualize',
    desc: 'Interactive Leaflet map with colour-coded vehicle routes, depot marker, demand popups, and sustainability savings.',
    color: 'text-orange-400',
    bg: 'bg-orange-900/20 border-orange-700/40',
  },
  {
    step: '06',
    icon: BarChart2,
    title: 'Benchmark & Analytics',
    desc: 'Full fleet analytics, per-route breakdown, QUBO stats panel, and a head-to-head benchmark with composite scores.',
    color: 'text-pink-400',
    bg: 'bg-pink-900/20 border-pink-700/40',
  },
]

const STATS = [
  { value: '4',     label: 'Vehicle Types' },
  { value: 'QUBO',  label: 'Quantum Encoding' },
  { value: '2-opt', label: 'Route Improvement' },
  { value: '7',     label: 'API Endpoints' },
]

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col">

      {/* ── Hero ── */}
      <div className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-green-950 pointer-events-none" />
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px]
          rounded-full bg-green-900/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 text-center px-6 max-w-2xl">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-green-900/40 border border-green-700/50
            rounded-full px-4 py-1.5 text-green-400 text-sm font-medium mb-8">
            <Leaf size={15} />
            QT-6.22 · Quantum Assisted Vehicle Routing
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl font-extrabold text-white leading-tight mb-4">
            Green<span className="text-green-400">Route</span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-300 font-semibold mb-3">
            Quantum Assisted<br />Vehicle Routing
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-10">
            {FEATURES.map(({ icon: Icon, label }) => (
              <span key={label}
                className="flex items-center gap-1.5 bg-gray-800 border border-gray-700
                  text-gray-300 text-sm px-3 py-1.5 rounded-full">
                <Icon size={14} className="text-green-400" />
                {label}
              </span>
            ))}
          </div>

          {/* CTA */}
          <button
            onClick={() => navigate('/upload')}
            className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500
              active:bg-green-700 text-white font-semibold text-lg px-8 py-3.5 rounded-xl
              shadow-lg shadow-green-900/40 transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2
              focus:ring-offset-gray-950"
          >
            Start
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Stats strip */}
        <div className="relative z-10 mt-16 grid grid-cols-2 sm:grid-cols-4 gap-px
          bg-gray-800 border border-gray-800 rounded-2xl overflow-hidden max-w-2xl w-full mx-6">
          {STATS.map(({ value, label }) => (
            <div key={label} className="bg-gray-900 px-6 py-5 text-center">
              <p className="text-2xl font-extrabold text-white">{value}</p>
              <p className="text-gray-500 text-xs mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── How it works ── */}
      <div className="bg-gray-950 border-t border-gray-800 py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-green-400 text-sm font-semibold uppercase tracking-wider mb-2">Workflow</p>
            <h2 className="text-3xl font-extrabold text-white">How it works</h2>
            <p className="text-gray-400 mt-3 max-w-xl mx-auto">
              From CSV upload to quantum-vs-classical comparison in five minutes.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {HOW_IT_WORKS.map(({ step, icon: Icon, title, desc, color, bg }) => (
              <div key={step} className={`border rounded-2xl p-6 ${bg} flex flex-col gap-3`}>
                <div className="flex items-center gap-3">
                  <span className="text-gray-600 text-xs font-mono font-bold">{step}</span>
                  <Icon size={20} className={color} />
                </div>
                <h3 className="text-white font-semibold text-base">{title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/upload')}
              className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500
                text-white font-semibold px-6 py-3 rounded-xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              Get Started
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>

    </div>
  )
}
