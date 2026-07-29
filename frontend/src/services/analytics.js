/**
 * analytics.js — GET /api/analytics
 * Returns fleet / routing / customers / optimization / sustainability KPIs.
 * Each section is null when its prerequisite hasn't run yet.
 */
import client from './api.js'

export async function getAnalytics() {
  return (await client.get('/analytics')).data
}
