import { api } from './client'

export const financeiroApi = {
  listarMovimentos: (params?: object) => api.get('/financeiro/movimentos', { params }).then(r => r.data),
  criarMovimento: (data: object) => api.post('/financeiro/movimentos', data).then(r => r.data),
  resumo: (inicio: string, fim: string) => api.get('/financeiro/resumo', { params: { inicio, fim } }).then(r => r.data),
  dre: (inicio: string, fim: string) => api.get('/financeiro/dre', { params: { inicio, fim } }).then(r => r.data),

  listarCategorias: () => api.get('/financeiro/categorias').then(r => r.data),
  criarCategoria: (data: object) => api.post('/financeiro/categorias', data).then(r => r.data),
  deletarCategoria: (id: string) => api.delete(`/financeiro/categorias/${id}`),

  listarContas: (params?: object) => api.get('/financeiro/contas', { params }).then(r => r.data),
  criarConta: (data: object) => api.post('/financeiro/contas', data).then(r => r.data),
  pagarConta: (id: string, data_pagamento?: string) =>
    api.patch(`/financeiro/contas/${id}/pagar`, null, { params: data_pagamento ? { data_pagamento } : {} }).then(r => r.data),
  cancelarConta: (id: string) => api.patch(`/financeiro/contas/${id}/cancelar`).then(r => r.data),
}
