import { api } from './client'

export const prospeccaoApi = {
  listar: (params?: object) => api.get('/prospeccao', { params }).then(r => r.data),
  criar: (data: object) => api.post('/prospeccao', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/prospeccao/${id}`, data).then(r => r.data),
  avancarEtapa: (id: string) => api.post(`/prospeccao/${id}/avancar`).then(r => r.data),
  deletar: (id: string) => api.delete(`/prospeccao/${id}`),
}
