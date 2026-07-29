/**
 * optimization.js — v1 solver endpoints (unchanged from shipped code).
 */
import client from './api.js'

/**
 * Upload CSV + fleet config.
 * @param {File} file
 * @param {{ fleet: Record<string,number>, capacities: Record<string,number> }} vehicleConfig
 */
export async function uploadDataset(file, vehicleConfig) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('fleet',      JSON.stringify(vehicleConfig.fleet))
  formData.append('capacities', JSON.stringify(vehicleConfig.capacities))

  const res = await client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/** POST /api/classical */
export async function runClassical() {
  return (await client.post('/classical')).data
}

/** POST /api/quantum */
export async function runQuantum() {
  return (await client.post('/quantum')).data
}

/** GET /api/compare */
export async function compareResults() {
  return (await client.get('/compare')).data
}
