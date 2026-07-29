/**
 * benchmark.js — GET /api/benchmark
 * Returns classical + quantum stats plus the Decision Engine verdict.
 * 400 if neither solver has run yet — caller should surface as guided prompt,
 * not a generic error.
 */
import client from './api.js'

export async function getBenchmark() {
  return (await client.get('/benchmark')).data
}
