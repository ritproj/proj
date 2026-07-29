import React, { createContext, useContext, useState } from 'react'

const AppContext = createContext(null)

export const DEFAULT_VEHICLE_CONFIG = {
  fleet:      { Van: 3, Truck: 0, Bike: 0, 'Electric Van': 0 },
  capacities: { Van: 50, Truck: 120, Bike: 15, 'Electric Van': 60 },
}

export function AppProvider({ children }) {
  const [uploadedFile, setUploadedFile]         = useState(null)
  const [parsedCustomers, setParsedCustomers]   = useState([])
  const [vehicleConfig, setVehicleConfig]       = useState(DEFAULT_VEHICLE_CONFIG)
  const [fleetCheck, setFleetCheck]             = useState(null)   // v2: from /api/upload fleet_check

  // v1 solver results
  const [classicalResult, setClassicalResult]   = useState(null)
  const [quantumResult, setQuantumResult]       = useState(null)
  const [comparisonResult, setComparisonResult] = useState(null)

  // v2 results
  const [benchmarkResult, setBenchmarkResult]   = useState(null)   // /api/benchmark
  const [analyticsResult, setAnalyticsResult]   = useState(null)   // /api/analytics

  const [loadingState, setLoadingState]         = useState(null)
  const [error, setError]                       = useState(null)
  const [showClusteringNotice, setShowClusteringNotice] = useState(false)

  function reset() {
    setUploadedFile(null)
    setParsedCustomers([])
    setVehicleConfig(DEFAULT_VEHICLE_CONFIG)
    setFleetCheck(null)
    setClassicalResult(null)
    setQuantumResult(null)
    setComparisonResult(null)
    setBenchmarkResult(null)
    setAnalyticsResult(null)
    setLoadingState(null)
    setError(null)
    setShowClusteringNotice(false)
  }

  return (
    <AppContext.Provider value={{
      uploadedFile,      setUploadedFile,
      parsedCustomers,   setParsedCustomers,
      vehicleConfig,     setVehicleConfig,
      fleetCheck,        setFleetCheck,
      classicalResult,   setClassicalResult,
      quantumResult,     setQuantumResult,
      comparisonResult,  setComparisonResult,
      benchmarkResult,   setBenchmarkResult,
      analyticsResult,   setAnalyticsResult,
      loadingState,      setLoadingState,
      error,             setError,
      showClusteringNotice, setShowClusteringNotice,
      reset,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
