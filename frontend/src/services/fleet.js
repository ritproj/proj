/**
 * fleet.js — GET /api/fleet
 * Returns demand vs capacity pre-flight check for the current dataset + fleet.
 */
import client from './api.js'

export async function getFleetCapacity() {
  return (await client.get('/fleet')).data
}
