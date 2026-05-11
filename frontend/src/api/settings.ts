import { api } from './client'

export const premissasApi = {
  listar: () => api.get('/premissas').then(r => r.data),
  criar: (data: object) => api.post('/premissas', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/premissas/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/premissas/${id}`),
}

export const configEmpresaApi = {
  obter: () => api.get('/empresa/config').then(r => r.data),
  atualizar: (data: object) => api.put('/empresa/config', data).then(r => r.data),
}
