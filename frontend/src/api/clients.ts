import { api } from './client'

export const clientesApi = {
  listar: (busca?: string) => api.get('/clientes', { params: busca ? { busca } : {} }).then(r => r.data),
  criar: (data: object) => api.post('/clientes', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/clientes/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/clientes/${id}`),
}
