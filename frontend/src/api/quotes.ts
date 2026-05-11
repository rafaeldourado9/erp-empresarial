import { api } from './client'

export const premissasApi = {
  listar: () => api.get('/premissas').then(r => r.data),
  criar: (data: object) => api.post('/premissas', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/premissas/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/premissas/${id}`),
}

export const orcamentosApi = {
  listar: (status?: string) => api.get('/orcamentos', { params: status ? { status } : {} }).then(r => r.data),
  obter: (id: string) => api.get(`/orcamentos/${id}`).then(r => r.data),
  criar: (data: object) => api.post('/orcamentos', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/orcamentos/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/orcamentos/${id}`),
  calcular: (data: object) => api.post('/orcamentos/calcular', data).then(r => r.data),
  aprovar: (id: string) => api.patch(`/orcamentos/${id}/aprovar`).then(r => r.data),
  reprovar: (id: string) => api.patch(`/orcamentos/${id}/reprovar`).then(r => r.data),
  fechar: (id: string, data: object) => api.patch(`/orcamentos/${id}/fechar`, data).then(r => r.data),
}
