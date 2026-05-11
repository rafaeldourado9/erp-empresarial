import { api } from './client'

export const estoqueApi = {
  listar: (busca?: string) => api.get('/estoque', { params: busca ? { busca } : {} }).then(r => r.data),
  criar: (data: object) => api.post('/estoque', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/estoque/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/estoque/${id}`),
  baixa: (id: string, data: object) => api.post(`/estoque/${id}/baixa`, data).then(r => r.data),
  entrada: (id: string, data: object) => api.post(`/estoque/${id}/entrada`, data).then(r => r.data),
  ajuste: (id: string, data: object) => api.post(`/estoque/${id}/ajuste`, data).then(r => r.data),
  movimentos: (id: string) => api.get(`/estoque/${id}/movimentos`).then(r => r.data),
  alertas: () => api.get('/estoque/alertas').then(r => r.data),
  relatoriopdf: () => api.get('/estoque/relatorio.pdf', { responseType: 'blob' }).then(r => r.data),
}
