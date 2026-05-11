import { api } from './client'

export const authApi = {
  login: (email: string, senha: string) =>
    api.post('/auth/login', { email, senha }).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
  logout: () => api.post('/auth/logout'),
  registro: (data: object) => api.post('/auth/registro', data).then(r => r.data),
  refresh: (refresh_token: string) => api.post('/auth/refresh', { refresh_token }).then(r => r.data),
}

export const empresasApi = {
  listar: () => api.get('/empresas').then(r => r.data),
  criar: (data: object) => api.post('/empresas', data).then(r => r.data),
}

export const operadoresApi = {
  listar: () => api.get('/operadores').then(r => r.data),
  criar: (data: object) => api.post('/operadores', data).then(r => r.data),
}
