import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Leaf, Truck, Fuel, Wind, ChevronRight,
         Upload, Cpu, BarChart2, Atom, GitCompare, Map, Zap, Shield, Activity } from 'lucide-react'

/* ── Animated counter hook ── */
function useCounter(target, duration = 1200, started = false) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!started) return
    let start = null
    const step = ts => {
      if (!start) start = ts
      const progress = Math.min((ts - start) / duration, 1)
      setVal(Math.floor(progress * target))
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [target, duration, started])
  return val
}

const HOW_IT_WORKS = [
  {
    step: '01', icon: Upload, title: 'Upload CSV',
    desc: 'Drop your customer dataset (lat, lng, demand) and configure your fleet — vans, trucks, bikes, EVs.',
    color: 'text-blue-400', bg: 'bg-blue-900/20 border-blue-700/40', glow: 'shadow-blue-900/20',
  },
  {
    step: '02', icon: Cpu, title: 'Classical Solver',
    desc: 'OR-Tools CVRP solves the routing problem using Guided Local Search — production-grade exact baseline.',
    color: 'text-yellow-400', bg: 'bg-yellow-900/20 border-yellow-700/40', glow: 'shadow-yellow-900/20',
  },
  {
    step: '03', icon: Atom, title: 'BQPhy Quantum-Inspired',
    desc: 'The CVRP is formulated as a QUBO matrix (N×K binary variables). BQPhy\'s evolutionary optimizer searches for the minimum-energy bitstring — solving the same objective a QAOA circuit would target.',
    color: 'text-purple-400', bg: 'bg-purple-900/20 border-purple-700/40', glow: 'shadow-purple-900/20',
  },
  {
    step: '04', icon: GitCompare, title: 'Decision Engine',
    desc: 'Scores both solvers on distance (75%) and runtime (25%), picks a winner with a plain-language explanation.',
    color: 'text-green-400', bg: 'bg-green-900/20 border-green-700/40', glow: 'shadow-green-900/20',
  },
  {
    step: '05', icon: Map, title: 'Visualize Routes',
    desc: 'Interactive Leaflet map with colour-coded vehicle routes, depot marker, demand popups, and side-by-side comparison.',
    color: 'text-orange-400', bg: 'bg-orange-900/20 border-orange-700/40', glow: 'shadow-orange-900/20',
  },
  {
    step: '06', icon: BarChart2, title: 'Benchmark & Analytics',
    desc: 'Fleet analytics, per-route breakdown, QUBO convergence chart, and a head-to-head benchmark with composite scores.',
    color: 'text-pink-400', bg: 'bg-pink-900/20 border-pink-700/40', glow: 'shadow-pink-900/20',
  },
]

const FEATURES = [
  { icon: Truck,    label: 'Optimize Routes' },
  { icon: Fuel,     label: 'Reduce Fuel' },
  { icon: Wind,     label: 'Lower CO₂' },
  { icon: Zap,      label: 'QUBO Solver' },
  { icon: Shield,   label: '49 Tests Passing' },
  { icon: Activity, label: 'Live Analytics' },
]

export default function Landing() {
  const navigate = useNavigate()
  const heroRef  = useRef(null)
  const [inView, setInView]     = useState(false)
  const [statsIn, setStatsIn]   = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setInView(true), 100)
    const t2 = setTimeout(() => setStatsIn(true), 600)
    return () => { clearTimeout(t); clearTimeout(t2) }
  }, [])

  const tests     = useCounter(49,   1000, statsIn)
  const customers = useCounter(50,   900,  statsIn)
  const apis      = useCounter(8,    700,  statsIn)
  const vars      = useCounter(500,  1100, statsIn)

  const STATS = [
    { value: tests,     suffix: '',    label: 'Tests Passing' },
    { value: customers, suffix: '+',   label: 'Max Customers' },
    { value: apis,      suffix: '',    label: 'API Endpoints' },
    { value: vars,      suffix: '',    label: 'Max QUBO Vars' },
  ]

  return (
    <div className="flex flex-col">

      {/* ── Hero ── */}
      <div className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center relative overflow-hidden">

        {/* Layered gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-green-950 pointer-events-none" />

        {/* Animated radial glows */}
        <div
          className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full pointer-events-none transition-opacity duration-1000"
          style={{
            background: 'radial-gradient(ellipse, rgba(16,185,129,0.07) 0%, transparent 70%)',
            opacity: inView ? 1 : 0,
          }}
        />
        <div
          className="absolute bottom-0 right-0 w-[400px] h-[400px] rounded-full pointer-events-none"
          style={{ background: 'radial-gradient(ellipse, rgba(168,85,247,0.06) 0%, transparent 70%)' }}
        />

        {/* Animated quantum orbit SVG */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none opacity-10">
          <svg width="600" height="600" viewBox="0 0 600 600">
            <ellipse cx="300" cy="300" rx="240" ry="90" fill="none" stroke="#10b981" strokeWidth="1"
              style={{ transformOrigin: '300px 300px', animation: 'spin 12s linear infinite' }} />
            <ellipse cx="300" cy="300" rx="240" ry="90" fill="none" stroke="#a855f7" strokeWidth="1"
              style={{ transformOrigin: '300px 300px', animation: 'spin 18s linear infinite reverse', transform: 'rotate(60deg)' }} />
            <ellipse cx="300" cy="300" rx="240" ry="90" fill="none" stroke="#3b82f6" strokeWidth="1"
              style={{ transformOrigin: '300px 300px', animation: 'spin 24s linear infinite', transform: 'rotate(120deg)' }} />
            <circle cx="300" cy="300" r="6" fill="#10b981" opacity="0.8" />
          </svg>
        </div>

        <style>{`
          @keyframes spin { from { transform: rotateX(70deg) rotateZ(0deg); } to { transform: rotateX(70deg) rotateZ(360deg); } }
          @keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
          @keyframes pulseGlow { 0%,100% { box-shadow: 0 0 20px rgba(16,185,129,0.3); } 50% { box-shadow: 0 0 40px rgba(16,185,129,0.6); } }
          @keyframes spinAtom { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          .fade-up { animation: fadeUp 0.7s ease forwards; }
          .fade-up-1 { animation: fadeUp 0.7s 0.1s ease both; }
          .fade-up-2 { animation: fadeUp 0.7s 0.25s ease both; }
          .fade-up-3 { animation: fadeUp 0.7s 0.4s ease both; }
          .fade-up-4 { animation: fadeUp 0.7s 0.55s ease both; }
          .pulse-glow { animation: pulseGlow 2.5s ease-in-out infinite; }
          .atom-inline { width: 70px; height: 70px; animation: spinAtom 10s linear infinite; margin-left: 10px; }
        `}</style>

        {/* Hero content */}
        <div className="relative z-10 text-center px-6 max-w-2xl" ref={heroRef}>

          {/* Badge */}
          <div className="fade-up-1 inline-flex items-center gap-2 bg-green-900/40 border border-green-700/50
            rounded-full px-4 py-1.5 text-green-400 text-sm font-medium mb-8 backdrop-blur-sm">
            <Leaf size={15} className="animate-pulse" />
            QT-6.22 · Quantum Assisted Vehicle Routing
          </div>

          {/* Headline */}
          <h1 className="fade-up-2 text-6xl sm:text-7xl font-extrabold leading-tight mb-4 flex justify-center items-center">
            <span className="text-white">Green</span>
            <span style={{
              background: 'linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>Route</span>
            <img src="/atom.png" alt="atom" className="atom-inline" />
          </h1>

          <p className="fade-up-3 text-xl sm:text-2xl text-gray-300 font-semibold mb-2">
            Quantum-Inspired Vehicle Routing
          </p>
          <p className="fade-up-3 text-gray-500 text-sm mb-8 max-w-md mx-auto leading-relaxed">
            QUBO-formulated CVRP solved by BQPhy evolutionary optimizer —
            the same objective a QAOA circuit targets, without Qiskit dependencies.
          </p>

          {/* Feature pills */}
          <div className="fade-up-3 flex flex-wrap justify-center gap-2 mb-10">
            {FEATURES.map(({ icon: Icon, label }) => (
              <span key={label}
                className="flex items-center gap-1.5 bg-gray-800/80 border border-gray-700/60
                  text-gray-300 text-xs px-3 py-1.5 rounded-full backdrop-blur-sm
                  hover:border-green-700/50 hover:text-green-300 transition-colors duration-200">
                <Icon size={13} className="text-green-400" />
                {label}
              </span>
            ))}
          </div>

          {/* CTA */}
          <div className="fade-up-4 flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              id="hero-start-btn"
              onClick={() => navigate('/upload')}
              className="pulse-glow inline-flex items-center gap-2 text-white font-bold text-lg
                px-10 py-4 rounded-2xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2
                focus:ring-offset-gray-950 hover:scale-105 active:scale-95"
              style={{
                background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
              }}
            >
              Start Optimizing
              <ChevronRight size={20} />
            </button>
            <button
              id="quantum-explorer-btn"
              onClick={() => navigate('/quantum-explorer')}
              className="inline-flex items-center gap-2 text-purple-100 font-bold text-lg
                px-10 py-4 rounded-2xl transition-all duration-200 border border-purple-500/50
                focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2
                focus:ring-offset-gray-950 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_40px_rgba(168,85,247,0.6)]"
              style={{
                background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.2) 0%, rgba(168, 85, 247, 0.4) 100%)',
                backdropFilter: 'blur(8px)',
              }}
            >
              <Atom size={20} className="text-purple-300" style={{ animation: 'spinAtom 6s linear infinite' }} />
              Explore Quantum Optimization
            </button>
          </div>
        </div>

        {/* Stats strip */}
        <div className="relative z-10 mt-16 grid grid-cols-2 sm:grid-cols-4 gap-px
          bg-gray-800/50 border border-gray-700/50 rounded-2xl overflow-hidden max-w-2xl w-full mx-6
          backdrop-blur-sm">
          {STATS.map(({ value, suffix, label }) => (
            <div key={label} className="bg-gray-900/80 px-6 py-5 text-center hover:bg-gray-800/80 transition-colors">
              <p className="text-3xl font-extrabold text-white tabular-nums">
                {value}{suffix}
              </p>
              <p className="text-gray-500 text-xs mt-1">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── How it works ── */}
      <div className="bg-gray-950 border-t border-gray-800 py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-green-400 text-sm font-semibold uppercase tracking-widest mb-3">Workflow</p>
            <h2 className="text-4xl font-extrabold text-white">How it works</h2>
            <p className="text-gray-400 mt-4 max-w-xl mx-auto leading-relaxed">
              From CSV upload to quantum-vs-classical comparison in minutes.
              Every step is traceable and every claim is backed by live test results.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {HOW_IT_WORKS.map(({ step, icon: Icon, title, desc, color, bg, glow }) => (
              <div key={step}
                className={`border rounded-2xl p-6 ${bg} flex flex-col gap-3
                  hover:shadow-lg ${glow} transition-all duration-300 hover:-translate-y-0.5 group`}>
                <div className="flex items-center gap-3">
                  <span className="text-gray-700 text-xs font-mono font-bold">{step}</span>
                  <div className={`p-2 rounded-lg ${bg} group-hover:scale-110 transition-transform duration-200`}>
                    <Icon size={18} className={color} />
                  </div>
                </div>
                <h3 className="text-white font-semibold text-base">{title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>

          {/* QUBO explanation callout */}
          <div className="mt-10 bg-purple-900/10 border border-purple-700/30 rounded-2xl p-6 flex gap-4">
            <Atom size={24} className="text-purple-400 shrink-0 mt-1" />
            <div>
              <p className="text-purple-300 font-semibold mb-1">What is QUBO?</p>
              <p className="text-gray-400 text-sm leading-relaxed">
                A <strong className="text-white">Quadratic Unconstrained Binary Optimization</strong> (QUBO) is
                the mathematical form quantum computers natively solve. We encode the CVRP as{' '}
                <span className="text-purple-300 font-mono">min xᵀQx</span> over binary assignment variables
                y[i,k] = 1 if customer i rides vehicle k. BQPhy's quantum-inspired evolutionary
                search finds the minimum-energy bitstring, which is then decoded into feasible delivery routes.
              </p>
            </div>
          </div>

          <div className="text-center mt-12">
            <button
              id="hiw-start-btn"
              onClick={() => navigate('/upload')}
              className="inline-flex items-center gap-2 bg-green-700 hover:bg-green-600
                text-white font-semibold px-8 py-3.5 rounded-xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-green-400 hover:scale-105"
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
