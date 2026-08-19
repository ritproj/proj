import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Leaf, Menu, X, Atom } from 'lucide-react'

const NAV_LINKS = [
  { to: '/',           label: 'Home' },
  { to: '/upload',     label: 'Upload' },
  { to: '/dashboard',  label: 'Dashboard' },
  { to: '/benchmark',  label: 'Benchmark' },
  { to: '/analytics',  label: 'Analytics' },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)

  return (
    <nav className="bg-gray-900/95 border-b border-gray-800 sticky top-0 z-50 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">

        {/* Brand */}
        <Link
          to="/"
          id="nav-brand"
          className="flex items-center gap-2 font-bold text-lg hover:opacity-90 transition-opacity"
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #6ee7b7 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          <Leaf size={20} className="text-green-400" style={{ WebkitTextFillColor: 'initial' }} />
          GreenRoute
        </Link>

        {/* Desktop links */}
        <div className="hidden sm:flex items-center gap-1">
          {NAV_LINKS.map(({ to, label }) => {
            const active = pathname === to
            return (
              <Link
                key={to}
                to={to}
                id={`nav-${label.toLowerCase()}`}
                className={`relative px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200
                  ${active
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
              >
                {/* Active background */}
                {active && (
                  <span
                    className="absolute inset-0 rounded-md"
                    style={{
                      background: 'linear-gradient(135deg, rgba(5,150,105,0.4) 0%, rgba(16,185,129,0.2) 100%)',
                      border: '1px solid rgba(16,185,129,0.35)',
                      boxShadow: '0 0 12px rgba(16,185,129,0.15)',
                    }}
                  />
                )}
                <span className="relative">{label}</span>
              </Link>
            )
          })}

          {/* Quantum badge */}
          <span className="ml-2 flex items-center gap-1 bg-purple-900/30 border border-purple-700/40
            text-purple-400 text-xs px-2 py-0.5 rounded-full">
            <Atom size={11} />
            BQPhy
          </span>
        </div>

        {/* Mobile hamburger */}
        <button
          className="sm:hidden text-gray-400 hover:text-white transition-colors"
          onClick={() => setOpen(o => !o)}
          aria-label="Toggle menu"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="sm:hidden border-t border-gray-800 bg-gray-900 px-4 py-3 flex flex-col gap-1">
          {NAV_LINKS.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                pathname === to
                  ? 'bg-green-900/40 border border-green-700/40 text-green-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
