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

export const variaveisApi = {
  listar: () => api.get('/orcamentos/variaveis').then(r => r.data) as Promise<{
    sistema: { chave: string; label: string; grupo: string }[]
    personalizadas: { id: string; chave: string; label: string; grupo: string }[]
  }>,
  criar: (data: { chave: string; label: string; grupo: string }) =>
    api.post('/orcamentos/variaveis', data).then(r => r.data),
  atualizar: (id: string, data: { chave: string; label: string; grupo: string }) =>
    api.put(`/orcamentos/variaveis/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/orcamentos/variaveis/${id}`),
}
