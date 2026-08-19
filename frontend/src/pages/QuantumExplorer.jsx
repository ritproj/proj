import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  ChevronRight, ChevronLeft, ArrowLeft, Info, Zap, RotateCw, 
  GitCommit, Target, RefreshCw, Cpu, Layers, Trophy, AlertCircle, Database
} from 'lucide-react';

// ── Tooltip Helper ────────────────────────────────────────────────────────
const Tooltip = ({ term, text }) => (
  <span className="relative group inline-flex items-center cursor-help text-purple-300 border-b border-purple-500/50 border-dotted mx-1">
    {term}
    <Info size={12} className="ml-1 opacity-70" />
    <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-2 bg-gray-800 border border-purple-500/30 text-xs text-gray-200 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-center shadow-xl">
      {text}
      <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
    </span>
  </span>
);

// ── Sections ──────────────────────────────────────────────────────────────

// Section 1: Why Classical Optimization Struggles
const Section1 = () => {
  const [stage, setStage] = useState(0);
  useEffect(() => {
    const t1 = setTimeout(() => setStage(1), 1500);
    const t2 = setTimeout(() => setStage(2), 3500);
    const t3 = setTimeout(() => setStage(3), 5500);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full space-y-8">
      <h2 className="text-3xl font-bold text-white mb-4">Why Classical Optimization Struggles</h2>
      <div className="flex gap-12 text-center text-xl text-gray-300">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-5xl font-extrabold text-blue-400 mb-2">8</div>
          <div>Customers</div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <div className="text-5xl font-extrabold text-green-400 mb-2">3</div>
          <div>Vehicles</div>
        </motion.div>
      </div>
      
      <AnimatePresence>
        {stage >= 1 && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }} 
            animate={{ opacity: 1, scale: 1 }} 
            className="text-2xl font-mono text-gray-400 mt-8"
          >
            3⁸ × 8!
          </motion.div>
        )}
        {stage >= 2 && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="text-6xl font-extrabold text-red-400 mt-4 drop-shadow-[0_0_15px_rgba(248,113,113,0.5)]"
          >
            264,000,000+
          </motion.div>
        )}
        {stage >= 3 && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="text-xl text-gray-300 mt-8 flex items-center gap-2 bg-red-900/20 px-6 py-3 rounded-xl border border-red-500/30"
          >
            <AlertCircle className="text-red-400" />
            Impossible to brute force quickly.
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Section 2: Classical Search
const Section2 = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-12">Classical Local Search</h2>
      <div className="relative w-[600px] h-[300px] border-b-2 border-gray-700 flex items-end justify-center">
        {/* Landscape SVG */}
        <svg width="600" height="300" viewBox="0 0 600 300" className="absolute bottom-0">
          <path d="M 0 150 Q 150 50 300 250 T 600 100 L 600 300 L 0 300 Z" fill="rgba(59,130,246,0.1)" stroke="#3b82f6" strokeWidth="3" />
        </svg>
        {/* Animated Ball */}
        <motion.div
          initial={{ x: -280, y: -150 }}
          animate={{ x: -30, y: -45 }}
          transition={{ duration: 2, ease: "easeIn" }}
          className="w-8 h-8 bg-blue-400 rounded-full absolute shadow-[0_0_15px_rgba(59,130,246,0.8)]"
        />
        {/* Label */}
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ delay: 2.5 }}
          className="absolute left-[240px] bottom-[20px] text-red-400 font-bold"
        >
          Local Minimum
        </motion.div>
      </div>
      <p className="mt-12 text-xl text-gray-300 max-w-lg text-center">
        Classical local search can become trapped in a "good enough" solution, unable to climb the hill to find the global best.
      </p>
    </div>
  );
};

// Section 3: Quantum Tunneling
const Section3 = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-12">Quantum-Inspired Search</h2>
      <div className="relative w-[600px] h-[300px] border-b-2 border-gray-700 flex items-end justify-center">
        <svg width="600" height="300" viewBox="0 0 600 300" className="absolute bottom-0">
          <path d="M 0 150 Q 150 50 300 250 T 600 100 L 600 300 L 0 300 Z" fill="rgba(168,85,247,0.1)" stroke="#a855f7" strokeWidth="3" />
        </svg>
        {/* Ball Starts at Local Min */}
        <motion.div
          initial={{ x: -30, y: -45, opacity: 1 }}
          animate={{ x: 130, y: -45, opacity: [1, 0, 1] }}
          transition={{ duration: 2, ease: "easeInOut", times: [0, 0.5, 1] }}
          className="w-8 h-8 bg-purple-400 rounded-full absolute shadow-[0_0_15px_rgba(168,85,247,0.8)]"
        />
        {/* Tunneling Effect */}
        <motion.div
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: [0, 1, 0], width: 160 }}
          transition={{ duration: 2, ease: "easeInOut" }}
          className="absolute left-[270px] bottom-[45px] h-[4px] bg-cyan-400 shadow-[0_0_10px_#22d3ee]"
          style={{ originX: 0 }}
        />
        {/* Labels */}
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ delay: 2.2 }}
          className="absolute right-[140px] bottom-[10px] text-green-400 font-bold"
        >
          Global Minimum!
        </motion.div>
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ delay: 1 }}
          className="absolute left-[330px] bottom-[60px] text-cyan-300 font-semibold text-sm"
        >
          Quantum Tunneling
        </motion.div>
      </div>
      <p className="mt-12 text-xl text-gray-300 max-w-2xl text-center">
        <Tooltip term="BQPhy" text="Quantum Inspired Evolutionary Optimizer" /> can escape local minima by using <Tooltip term="Tunneling" text="Jumping through energy barriers instead of climbing over them" /> mechanisms.
      </p>
    </div>
  );
};

// Section 4: Superposition
const Section4 = () => {
  const [stage, setStage] = useState(0);
  useEffect(() => {
    const t1 = setTimeout(() => setStage(1), 2000);
    const t2 = setTimeout(() => setStage(2), 4000);
    const t3 = setTimeout(() => setStage(3), 6000);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  const probs = [
    [40, 35, 25],
    [55, 30, 15],
    [90, 8, 2],
    [100, 0, 0]
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-8">Superposition Concept</h2>
      <div className="bg-gray-800/50 p-8 rounded-2xl border border-gray-700 w-[500px]">
        <h3 className="text-xl text-center text-white mb-6">Customer 5</h3>
        <div className="space-y-6">
          {['Vehicle 1', 'Vehicle 2', 'Vehicle 3'].map((v, i) => (
            <div key={v}>
              <div className="flex justify-between text-sm mb-2 text-gray-400">
                <span>{v}</span>
                <motion.span animate={{ color: probs[stage][i] > 50 ? '#4ade80' : '#9ca3af' }}>
                  {probs[stage][i]}%
                </motion.span>
              </div>
              <div className="h-4 bg-gray-900 rounded-full overflow-hidden">
                <motion.div 
                  className={`h-full ${i === 0 ? 'bg-green-500' : i === 1 ? 'bg-blue-500' : 'bg-purple-500'}`}
                  initial={{ width: `${probs[0][i]}%` }}
                  animate={{ width: `${probs[stage][i]}%` }}
                  transition={{ type: "spring", stiffness: 50 }}
                />
              </div>
            </div>
          ))}
        </div>
        <AnimatePresence>
          {stage === 3 && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-8 text-center text-green-400 font-bold bg-green-900/20 py-2 rounded-lg border border-green-500/30">
              Hard Decode: Assigned to Vehicle 1
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <p className="mt-10 text-lg text-gray-300 max-w-xl text-center">
        During optimization, the algorithm explores multiple assignment possibilities simultaneously in <Tooltip term="Superposition" text="A state representing multiple possibilities at once" /> before selecting the strongest one.
      </p>
    </div>
  );
};

// Section 5: Population Evolution
const Section5 = () => {
  const [gen, setGen] = useState(1);
  useEffect(() => {
    const interval = setInterval(() => {
      setGen(prev => (prev < 20 ? prev + 1 : prev));
    }, 300);
    return () => clearInterval(interval);
  }, []);

  // Generate dots converging
  const dots = Array.from({ length: 100 }).map((_, i) => {
    // Target is center (0,0)
    const startX = (Math.random() - 0.5) * 400;
    const startY = (Math.random() - 0.5) * 400;
    const currentX = startX * Math.pow(0.8, gen - 1);
    const currentY = startY * Math.pow(0.8, gen - 1);
    return { id: i, x: currentX, y: currentY };
  });

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-4">Population Evolution</h2>
      <div className="text-purple-400 font-mono text-xl mb-8">Generation: {gen}/20</div>
      
      <div className="relative w-[400px] h-[400px] bg-gray-900 border border-gray-700 rounded-xl overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 opacity-20" style={{ background: 'radial-gradient(circle at center, #a855f7 0%, transparent 70%)' }}></div>
        {dots.map(dot => (
          <motion.div
            key={dot.id}
            animate={{ x: dot.x, y: dot.y }}
            transition={{ duration: 0.3 }}
            className="absolute w-2 h-2 bg-cyan-400 rounded-full opacity-80"
          />
        ))}
        {gen === 20 && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="absolute w-6 h-6 bg-green-400 rounded-full shadow-[0_0_20px_#4ade80] z-10 flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full"></div>
          </motion.div>
        )}
      </div>

      <p className="mt-10 text-lg text-gray-300 max-w-xl text-center">
        Unlike classical single-solution search, BQPhy evolves an entire <Tooltip term="Population" text="Collection of candidate solutions" /> simultaneously, clustering around the optimal answer.
      </p>
    </div>
  );
};

// Section 6: QUBO Construction
const Section6 = () => {
  const [stage, setStage] = useState(0);
  useEffect(() => {
    const sequence = async () => {
      await new Promise(r => setTimeout(r, 1000)); setStage(1);
      await new Promise(r => setTimeout(r, 1500)); setStage(2);
      await new Promise(r => setTimeout(r, 1500)); setStage(3);
    };
    sequence();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-12"><Tooltip term="QUBO" text="Quadratic Unconstrained Binary Optimization" /> Construction</h2>
      
      <div className="flex items-center gap-6">
        {/* Customer List */}
        <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 w-40 text-center text-sm">
          <div className="font-bold text-gray-300 mb-2">Customers</div>
          <div className="space-y-1 opacity-70">
            <div className="bg-gray-700 rounded px-2 py-1">C1 (10kg)</div>
            <div className="bg-gray-700 rounded px-2 py-1">C2 (15kg)</div>
            <div className="bg-gray-700 rounded px-2 py-1">C3 (8kg)</div>
          </div>
        </div>

        {stage >= 1 && <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}><ArrowLeft className="rotate-180 text-gray-500" /></motion.div>}

        {/* Binary Matrix */}
        {stage >= 1 && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-gray-800 p-4 rounded-xl border border-blue-500/50 w-48 text-center text-sm">
            <div className="font-bold text-blue-300 mb-2">Binary Variables (y_ik)</div>
            <div className="grid grid-cols-2 gap-1 text-xs opacity-80 font-mono">
              <div className="bg-blue-900/30 p-1">y_1,1</div><div className="bg-blue-900/30 p-1">y_1,2</div>
              <div className="bg-blue-900/30 p-1">y_2,1</div><div className="bg-blue-900/30 p-1">y_2,2</div>
              <div className="bg-blue-900/30 p-1">y_3,1</div><div className="bg-blue-900/30 p-1">y_3,2</div>
            </div>
          </motion.div>
        )}

        {stage >= 2 && <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}><ArrowLeft className="rotate-180 text-gray-500" /></motion.div>}

        {/* Q Matrix */}
        {stage >= 2 && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-gray-800 p-4 rounded-xl border border-purple-500/50 w-56 text-center text-sm shadow-[0_0_20px_rgba(168,85,247,0.2)]">
            <div className="font-bold text-purple-300 mb-2">Q Matrix</div>
            <div className="text-xs text-gray-400 mb-2">Distance + Assignment + Capacity Penalties</div>
            <div className="grid grid-cols-4 gap-0.5 opacity-60">
              {Array.from({length: 16}).map((_, i) => (
                <div key={i} className={`h-4 w-full ${Math.random() > 0.5 ? 'bg-purple-500' : 'bg-gray-600'}`}></div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {stage >= 3 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mt-12 text-2xl font-mono text-green-400 bg-green-900/20 px-8 py-4 rounded-2xl border border-green-500/30">
          Energy E(x) = x<sup className="text-lg">T</sup>Qx
        </motion.div>
      )}
    </div>
  );
};

// Section 7: Quantum Principles Used
const Section7 = () => {
  const [active, setActive] = useState(null);
  const cards = [
    { id: 'sup', title: 'Superposition', icon: Layers, desc: 'Candidate solutions exist in combinations of multiple states simultaneously.' },
    { id: 'rot', title: 'Rotation (ΔΘ)', icon: RotateCw, desc: 'Controls the balance between exploration and exploitation in the search space.' },
    { id: 'int', title: 'Interference', icon: Zap, desc: 'Constructive interference amplifies good solutions; destructive suppresses bad ones.' },
    { id: 'tun', title: 'Tunneling', icon: ArrowLeft, desc: 'Allows the optimizer to pass through energy barriers to escape local minima.' },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full w-full max-w-4xl">
      <h2 className="text-3xl font-bold text-white mb-12">Quantum Principles in BQPhy</h2>
      <div className="grid grid-cols-2 gap-6 w-full">
        {cards.map(c => (
          <motion.div 
            key={c.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActive(c.id)}
            className={`p-6 rounded-2xl border cursor-pointer transition-colors ${active === c.id ? 'bg-purple-900/40 border-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.3)]' : 'bg-gray-800/50 border-gray-700 hover:border-gray-500'}`}
          >
            <div className="flex items-center gap-3 mb-3">
              <c.icon className={active === c.id ? 'text-purple-400' : 'text-gray-400'} />
              <h3 className={`text-xl font-bold ${active === c.id ? 'text-white' : 'text-gray-300'}`}>{c.title}</h3>
            </div>
            <AnimatePresence>
              {active === c.id && (
                <motion.p initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="text-gray-300 text-sm">
                  {c.desc}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Section 8: Pipeline
const Section8 = () => {
  const steps = ['CSV', 'Distance Matrix', 'QUBO', 'Initialize Population', 'Evolution', 'Best Solution', 'Decode', 'Repair', 'Optimized Routes'];
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep(prev => (prev < steps.length - 1 ? prev + 1 : 0)); // loop for demo
    }, 1000);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="flex flex-col items-center justify-center h-full w-full max-w-3xl">
      <h2 className="text-3xl font-bold text-white mb-12">Optimization Pipeline</h2>
      <div className="flex flex-wrap justify-center gap-4">
        {steps.map((step, i) => (
          <React.Fragment key={step}>
            <div className={`px-4 py-2 rounded-lg border text-sm font-semibold transition-all duration-500 ${activeStep >= i ? 'bg-green-900/40 border-green-500 text-green-300 shadow-[0_0_15px_rgba(16,185,129,0.4)]' : 'bg-gray-800 border-gray-700 text-gray-500'}`}>
              {step}
            </div>
            {i < steps.length - 1 && (
              <div className="flex items-center">
                <ChevronRight className={`transition-colors duration-500 ${activeStep > i ? 'text-green-500' : 'text-gray-700'}`} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

// Section 9: Dual Decode
const Section9 = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-3xl font-bold text-white mb-8">Dual Decode Mechanism</h2>
      
      <div className="flex flex-col items-center gap-6">
        <div className="bg-gray-800 border border-gray-700 p-4 rounded-xl text-center">
          <div className="text-xs text-purple-400 mb-1">BQPhy Output Vector</div>
          <div className="font-mono text-gray-300">[0.92, 0.11, 0.67, 0.44]</div>
        </div>

        <div className="w-px h-8 bg-gray-600"></div>

        <div className="flex gap-16 relative">
          <div className="w-full h-px bg-gray-600 absolute top-0"></div>
          
          <div className="flex flex-col items-center pt-6">
            <div className="bg-blue-900/30 border border-blue-500/50 p-4 rounded-xl text-center w-48">
              <div className="font-bold text-blue-300 mb-2">Hard Decode</div>
              <div className="text-xs text-gray-400 mb-2">Round to 0 or 1</div>
              <div className="font-mono text-white">[1, 0, 1, 0]</div>
            </div>
            <div className="w-px h-6 bg-gray-600 my-2"></div>
            <div className="bg-gray-800 border border-gray-700 py-1 px-3 rounded text-sm text-gray-300">Validation</div>
            <div className="w-px h-6 bg-gray-600 my-2"></div>
            <div className="bg-red-900/20 border border-red-500/30 py-1 px-3 rounded text-sm text-red-400 flex items-center gap-1">
              <AlertCircle size={14} /> Failed (Capacity)
            </div>
          </div>

          <div className="flex flex-col items-center pt-6 opacity-50 hover:opacity-100 transition-opacity">
            <div className="bg-orange-900/30 border border-orange-500/50 p-4 rounded-xl text-center w-48">
              <div className="font-bold text-orange-300 mb-2">Soft Decode</div>
              <div className="text-xs text-gray-400 mb-2">Argmax Assignment</div>
              <div className="font-mono text-white">Assign to max prob</div>
            </div>
            <div className="w-px h-6 bg-gray-600 my-2"></div>
            <div className="bg-gray-800 border border-gray-700 py-1 px-3 rounded text-sm text-gray-300">Repair Pipeline</div>
            <div className="w-px h-6 bg-gray-600 my-2"></div>
            <div className="bg-green-900/20 border border-green-500/30 py-1 px-3 rounded text-sm text-green-400 flex items-center gap-1">
               Success
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Section 10: Interactive Playground
const Section10 = () => {
  const [cust, setCust] = useState(8);
  const [veh, setVeh] = useState(3);
  const [pop, setPop] = useState(100);
  const [gen, setGen] = useState(500);
  const [theta, setTheta] = useState(0.1);

  const vars = cust * veh;
  const space = Math.pow(2, vars).toExponential(2);
  const time = (vars * pop * gen * 0.00001).toFixed(2);

  return (
    <div className="flex flex-col items-center justify-center h-full w-full max-w-4xl">
      <h2 className="text-3xl font-bold text-white mb-8">Interactive Optimization Simulator</h2>
      <div className="grid grid-cols-2 gap-8 w-full">
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-2xl space-y-6">
          <h3 className="text-lg font-bold text-gray-300 border-b border-gray-700 pb-2">Parameters</h3>
          <div>
            <div className="flex justify-between text-sm mb-1 text-gray-400"><label>Customers</label><span>{cust}</span></div>
            <input type="range" min="4" max="25" value={cust} onChange={e=>setCust(e.target.value)} className="w-full accent-purple-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1 text-gray-400"><label>Vehicles</label><span>{veh}</span></div>
            <input type="range" min="1" max="5" value={veh} onChange={e=>setVeh(e.target.value)} className="w-full accent-purple-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1 text-gray-400"><label>Population</label><span>{pop}</span></div>
            <input type="range" min="10" max="500" step="10" value={pop} onChange={e=>setPop(e.target.value)} className="w-full accent-blue-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1 text-gray-400"><label>Generations</label><span>{gen}</span></div>
            <input type="range" min="100" max="2000" step="100" value={gen} onChange={e=>setGen(e.target.value)} className="w-full accent-blue-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1 text-gray-400"><label><Tooltip term="Delta Theta" text="Rotation angle controlling exploration." /></label><span>{theta}</span></div>
            <input type="range" min="0.01" max="0.5" step="0.01" value={theta} onChange={e=>setTheta(e.target.value)} className="w-full accent-cyan-500" />
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <motion.div key={vars} initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-gray-800/50 border border-blue-500/30 p-6 rounded-2xl flex-1 flex flex-col justify-center items-center text-center">
            <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">QUBO Variables</div>
            <div className="text-5xl font-mono font-bold text-blue-400">{vars}</div>
          </motion.div>
          
          <motion.div key={space} initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-gray-800/50 border border-purple-500/30 p-6 rounded-2xl flex-1 flex flex-col justify-center items-center text-center">
            <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">Search Space Size</div>
            <div className="text-4xl font-mono font-bold text-purple-400">{space}</div>
          </motion.div>

          <motion.div key={time} initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-gray-800/50 border border-green-500/30 p-6 rounded-2xl flex-1 flex flex-col justify-center items-center text-center">
            <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">Est. Opt. Time (s)</div>
            <div className="text-4xl font-mono font-bold text-green-400">{time}s</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

// Section 11: Multi Restart
const Section11 = () => {
  const restarts = [
    { id: 1, energy: -66400, winner: false },
    { id: 2, energy: -77100, winner: false },
    { id: 3, energy: -74500, winner: false },
    { id: 4, energy: -79346, winner: true },
    { id: 5, energy: -61800, winner: false },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full w-full">
      <h2 className="text-3xl font-bold text-white mb-12">Multi-Restart Visualization</h2>
      <div className="flex gap-4">
        {restarts.map((r, i) => (
          <motion.div 
            key={r.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.2 }}
            className={`flex flex-col items-center justify-between p-6 rounded-2xl border w-32 h-40 ${r.winner ? 'bg-purple-900/40 border-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.4)]' : 'bg-gray-800 border-gray-700'}`}
          >
            <div className="text-xs text-gray-400 uppercase">Restart {r.id}</div>
            <div className={`text-lg font-mono font-bold ${r.winner ? 'text-white' : 'text-gray-300'}`}>{r.energy}</div>
            {r.winner ? (
               <div className="bg-purple-500/20 text-purple-300 text-xs px-2 py-1 rounded flex items-center gap-1"><Trophy size={12}/> Best</div>
            ) : (
               <div className="text-gray-600 text-xs">Suboptimal</div>
            )}
          </motion.div>
        ))}
      </div>
      <p className="mt-12 text-lg text-gray-300">
        Lowest Energy = Best Assignment. Multiple parallel restarts ensure the global minimum is found.
      </p>
    </div>
  );
};

// Section 12: Classical vs Quantum
const Section12 = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full max-w-4xl">
      <h2 className="text-3xl font-bold text-white mb-12">Comparison</h2>
      <div className="flex gap-8 w-full">
        <div className="flex-1 bg-blue-900/10 border border-blue-500/30 p-8 rounded-2xl">
          <div className="flex items-center gap-2 text-2xl font-bold text-blue-400 mb-6">
            <Cpu /> Classical (OR-Tools)
          </div>
          <ul className="space-y-4 text-gray-300">
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Single Solution Tracking</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Guided Local Search</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Prone to local minima entrapment</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Sequential execution</li>
          </ul>
        </div>
        <div className="flex-1 bg-purple-900/10 border border-purple-500/30 p-8 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-3xl rounded-full"></div>
          <div className="flex items-center gap-2 text-2xl font-bold text-purple-400 mb-6 relative z-10">
            <Zap /> Quantum-Inspired
          </div>
          <ul className="space-y-4 text-gray-300 relative z-10">
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-400"></div> Population Search</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-400"></div> Evolutionary Optimizer</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-400"></div> Quantum Tunneling escapes minima</li>
            <li className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-400"></div> Parallel processing</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Section 13: GreenRoute Integration & Outro
const Section13 = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.8, type: 'spring' }} className="mb-12">
        <Trophy size={64} className="text-yellow-400 mx-auto mb-6 drop-shadow-[0_0_20px_rgba(250,204,21,0.5)]" />
        <h2 className="text-4xl font-bold text-white mb-4">Congratulations!</h2>
        <p className="text-xl text-gray-400 max-w-xl">
          You now understand how GreenRoute's Quantum Inspired Optimizer works.
        </p>
      </motion.div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-left max-w-2xl mx-auto">
        {['QUBO Formulation', 'Population Evolution', 'Superposition Concept', 'Rotation Angles', 'Constructive Interference', 'Quantum Tunneling', 'Dual Decode Mechanism', 'Route Repairing', 'Decision Engine Selection'].map((item, i) => (
          <motion.div key={item} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.1 }} className="flex items-center gap-2 text-gray-300 bg-gray-800/50 py-2 px-3 rounded-lg border border-gray-700">
            <div className="text-green-400 font-bold">✓</div> {item}
          </motion.div>
        ))}
      </div>
    </div>
  );
};


// ── Main Component ────────────────────────────────────────────────────────
const SECTIONS = [
  { id: 1, component: Section1 },
  { id: 2, component: Section2 },
  { id: 3, component: Section3 },
  { id: 4, component: Section4 },
  { id: 5, component: Section5 },
  { id: 6, component: Section6 },
  { id: 7, component: Section7 },
  { id: 8, component: Section8 },
  { id: 9, component: Section9 },
  { id: 10, component: Section10 },
  { id: 11, component: Section11 },
  { id: 12, component: Section12 },
  { id: 13, component: Section13 },
];

export default function QuantumExplorer() {
  const navigate = useNavigate();
  const [current, setCurrent] = useState(0);

  const handleNext = () => { if (current < SECTIONS.length - 1) setCurrent(c => c + 1); };
  const handlePrev = () => { if (current > 0) setCurrent(c => c - 1); };

  const CurrentSection = SECTIONS[current].component;
  const progress = ((current + 1) / SECTIONS.length) * 100;

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex flex-col bg-gray-950 text-gray-100 overflow-hidden relative">
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-purple-950/20 pointer-events-none" />
      
      {/* Header & Progress */}
      <div className="relative z-20 w-full p-6 flex flex-col items-center">
        <div className="w-full max-w-4xl flex justify-between items-center mb-4">
          <button onClick={() => navigate('/')} className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
            <ArrowLeft size={16} /> Back to Home
          </button>
          <div className="text-purple-400 font-mono text-sm tracking-widest">
            QUANTUM EXPLORER
          </div>
          <div className="w-24 text-right text-gray-500 font-mono text-sm">
            {current + 1} / {SECTIONS.length}
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full max-w-4xl h-1 bg-gray-800 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-purple-600 to-cyan-400"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ type: 'spring', stiffness: 50 }}
          />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 relative z-10 w-full max-w-5xl mx-auto flex items-center justify-center p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={current}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="w-full h-full min-h-[500px]"
          >
            <CurrentSection />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Footer Controls */}
      <div className="relative z-20 w-full p-8 flex justify-center gap-4">
        <button 
          onClick={handlePrev}
          disabled={current === 0}
          className="px-6 py-3 rounded-xl border border-gray-700 bg-gray-900 text-gray-300 font-semibold disabled:opacity-30 hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <ChevronLeft size={18} /> Previous
        </button>
        
        {current === SECTIONS.length - 1 ? (
           <button 
             onClick={() => navigate('/')}
             className="px-8 py-3 rounded-xl border border-green-500/50 bg-green-900/20 text-green-400 font-bold hover:bg-green-900/40 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.2)]"
           >
             Finish & Optimize
           </button>
        ) : (
          <button 
            onClick={handleNext}
            className="px-8 py-3 rounded-xl border border-purple-500/50 bg-purple-900/20 text-purple-300 font-bold hover:bg-purple-900/40 transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(168,85,247,0.2)]"
          >
            Next <ChevronRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
