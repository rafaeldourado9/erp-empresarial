import { api } from './client'

export const auditoriaApi = {
  listar: (params?: object) => api.get('/auditoria', { params }).then(r => r.data),
}
