import React, { useMemo, useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'

// ── Offline-safe Leaflet icons (bundled via npm, no CDN) ──────────────────
import markerIcon2x   from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon     from 'leaflet/dist/images/marker-icon.png'
import markerShadow   from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl:       markerIcon,
  shadowUrl:     markerShadow,
})

// Vehicle route colours (Blue, Green, Orange, Purple, Pink)
const ROUTE_COLORS = ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ec4899']

function vehicleIcon(color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:13px;height:13px;border-radius:50%;
      background:${color};border:2.5px solid white;
      box-shadow:0 1px 4px rgba(0,0,0,0.5)">
    </div>`,
    iconSize: [13, 13],
    iconAnchor: [6, 6],
  })
}

const depotIcon = L.divIcon({
  className: '',
  html: `<div style="
    width:20px;height:20px;border-radius:50%;
    background:#111827;border:3px solid #6ee7b7;
    box-shadow:0 0 0 2px rgba(110,231,183,0.35),0 2px 8px rgba(0,0,0,0.6)">
  </div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
})

function MapResizer() {
  const map = useMap()
  useEffect(() => {
    const id = setTimeout(() => map.invalidateSize(), 100)
    return () => clearTimeout(id)
  }, [map])
  return null
}

function FitBounds({ points }) {
  const map = useMap()
  useEffect(() => {
    if (points.length === 0) return
    const bounds = L.latLngBounds(points)
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
  }, [map, points])
  return null
}

/**
 * RouteMap — shows classical and/or quantum routes with a tab toggle.
 *
 * Props:
 *   depot          : { lat, lng }
 *   customers      : [{ id, lat, lng, demand }]
 *   classicalResult: full /api/classical response (has .routes, .route_meta)
 *   quantumResult  : full /api/quantum response  (has .routes, .route_meta)
 *
 * Legacy single-mode: if only `routes` prop is passed, renders that set.
 */
export default function RouteMap({
  depot,
  customers = [],
  routes: legacyRoutes,          // backwards-compat single-mode
  classicalResult = null,
  quantumResult   = null,
}) {
  const hasBoth = classicalResult?.routes?.length > 0 && quantumResult?.routes?.length > 0
  const [tab, setTab] = useState('quantum')   // 'classical' | 'quantum' | 'both'

  // Resolve which routes to display
  const activeRoutes = useMemo(() => {
    if (legacyRoutes) return legacyRoutes          // legacy fallback
    if (!hasBoth) {
      return (quantumResult ?? classicalResult)?.routes ?? []
    }
    if (tab === 'both')      return null            // handled separately
    if (tab === 'quantum')   return quantumResult?.routes  ?? []
    return classicalResult?.routes ?? []
  }, [legacyRoutes, hasBoth, tab, classicalResult, quantumResult])

  const center = useMemo(() => {
    if (depot) return [depot.lat, depot.lng]
    if (customers.length > 0)
      return [
        customers.reduce((s, c) => s + c.lat, 0) / customers.length,
        customers.reduce((s, c) => s + c.lng, 0) / customers.length,
      ]
    return [20, 0]
  }, [depot, customers])

  const allPoints = useMemo(() => {
    const pts = []
    if (depot) pts.push([depot.lat, depot.lng])
    customers.forEach(c => pts.push([c.lat, c.lng]))
    return pts
  }, [depot, customers])

  const mapKey = useMemo(
    () => `${depot?.lat}-${depot?.lng}-${customers.length}-${tab}`,
    [depot, customers, tab]
  )

  // Routes to actually render on the map
  const renderRoutes = tab === 'both' && hasBoth
    ? [
        ...(classicalResult?.routes ?? []).map((r, i) => ({ pts: r, color: ROUTE_COLORS[i % ROUTE_COLORS.length], label: `C-V${i + 1}`, dashed: true })),
        ...(quantumResult?.routes   ?? []).map((r, i) => ({ pts: r, color: ROUTE_COLORS[i % ROUTE_COLORS.length], label: `Q-V${i + 1}`, dashed: false })),
      ]
    : (activeRoutes ?? []).map((r, i) => ({ pts: r, color: ROUTE_COLORS[i % ROUTE_COLORS.length], label: `V${i + 1}`, dashed: false }))

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">

      {/* ── Tab bar (only shown when both solvers ran) ── */}
      {hasBoth && (
        <div className="flex border-b border-gray-800 bg-gray-900/80 px-4 pt-3 gap-1">
          {[
            { key: 'quantum',   label: 'Quantum',   color: 'text-purple-400' },
            { key: 'classical', label: 'Classical', color: 'text-blue-400'   },
            { key: 'both',      label: 'Both',      color: 'text-green-400'  },
          ].map(({ key, label, color }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`px-3 py-1.5 rounded-t-md text-xs font-semibold transition-colors ${
                tab === key
                  ? `bg-gray-800 border border-b-0 border-gray-700 ${color}`
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {label}
            </button>
          ))}
          <div className="flex-1" />
          {tab === 'both' && (
            <span className="text-gray-600 text-xs self-center pr-1">
              dashed = classical
            </span>
          )}
        </div>
      )}

      {/* ── Map ── */}
      <div style={{ height: 440, position: 'relative' }}>
        <MapContainer
          key={mapKey}
          center={center}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom
        >
          <MapResizer />
          {allPoints.length > 0 && <FitBounds points={allPoints} />}

          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Depot */}
          {depot && (
            <Marker position={[depot.lat, depot.lng]} icon={depotIcon}>
              <Popup><b>Depot</b><br />Start / End for all vehicles</Popup>
            </Marker>
          )}

          {/* Unassigned customers (before any solver runs) */}
          {renderRoutes.length === 0 && customers.map(c => (
            <Marker key={`c-${c.id}`} position={[c.lat, c.lng]} icon={vehicleIcon('#6b7280')}>
              <Popup><b>Customer {c.id}</b><br />Demand: {c.demand} kg</Popup>
            </Marker>
          ))}

          {/* Routes */}
          {renderRoutes.map(({ pts, color, label, dashed }, rIdx) => {
            const positions = pts.map(p => [p.lat, p.lng])
            return (
              <React.Fragment key={`route-${rIdx}-${label}`}>
                <Polyline
                  positions={positions}
                  pathOptions={{
                    color,
                    weight:    dashed ? 2.5 : 3.5,
                    opacity:   dashed ? 0.6 : 0.9,
                    dashArray: dashed ? '6 4' : null,
                  }}
                />
                {pts.map((p, pIdx) =>
                  p.id != null ? (
                    <Marker key={`r${rIdx}-p${pIdx}`} position={[p.lat, p.lng]} icon={vehicleIcon(color)}>
                      <Popup>
                        <b>Customer {p.id}</b><br />
                        {label}<br />
                        {p.demand != null && `Demand: ${p.demand} kg`}
                      </Popup>
                    </Marker>
                  ) : null
                )}
              </React.Fragment>
            )
          })}
        </MapContainer>

        {/* Legend */}
        {renderRoutes.length > 0 && (
          <div style={{
            position: 'absolute', bottom: 12, left: 12, zIndex: 1000,
            background: 'rgba(17,24,39,0.90)', borderRadius: 8, padding: '6px 10px',
            backdropFilter: 'blur(4px)', border: '1px solid rgba(255,255,255,0.08)',
          }}>
            <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 4, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              {tab === 'both' ? 'Routes (C=classical, Q=quantum)' : `Routes · ${tab}`}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#111827', border: '2px solid #6ee7b7' }} />
              <span style={{ fontSize: 11, color: '#d1d5db' }}>Depot</span>
            </div>
            {renderRoutes.map(({ color, label }, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                <div style={{ width: 20, height: 3, background: color, borderRadius: 2 }} />
                <span style={{ fontSize: 11, color: '#d1d5db' }}>{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
