import { api } from './client'

export const operadoresApi = {
  listar: () => api.get('/operadores').then(r => r.data),
  criar: (data: object) => api.post('/operadores', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/operadores/${id}`, data).then(r => r.data),
  toggleAtivo: (id: string) => api.post(`/operadores/${id}/toggle`).then(r => r.data),
  redefinirSenha: (id: string, nova_senha: string) => api.post(`/operadores/${id}/senha`, { nova_senha }).then(r => r.data),
}
