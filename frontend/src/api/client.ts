import axios from 'axios'
import { useAuthStore } from '../store/auth.store'

const BASE = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: `${BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  const empresa = useAuthStore.getState().empresaSelecionada
  if (empresa) config.headers['X-Empresa-Id'] = empresa
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const isAuthEndpoint = err.config?.url?.startsWith('/auth/')
    if (err.response?.status === 401 && !isAuthEndpoint) {
      const refresh = useAuthStore.getState().refreshToken
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE}/api/v1/auth/refresh`, { refresh_token: refresh })
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
          err.config.headers.Authorization = `Bearer ${data.access_token}`
          return axios(err.config)
        } catch {
          useAuthStore.getState().logout()
        }
      }
    }
    return Promise.reject(err)
  }
)
