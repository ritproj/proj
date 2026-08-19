import axios from './api'

export async function getConvergence() {
  const res = await axios.get('/convergence')
  return res.data
}
