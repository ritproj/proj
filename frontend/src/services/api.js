/**
 * api.js — shared Axios instance used by all service modules.
 * Import this, not Axios directly, so the base URL and timeout
 * are configured in one place.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000, // QAOA can be slow on simulator
})

export default client
