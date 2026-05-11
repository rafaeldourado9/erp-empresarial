import { api } from './client'

export const financeiroApi = {
  listarMovimentos: (params?: object) => api.get('/financeiro/movimentos', { params }).then(r => r.data),
  criarMovimento: (data: object) => api.post('/financeiro/movimentos', data).then(r => r.data),
  resumo: (inicio: string, fim: string) => api.get('/financeiro/resumo', { params: { inicio, fim } }).then(r => r.data),
  dre: (inicio: string, fim: string) => api.get('/financeiro/dre', { params: { inicio, fim } }).then(r => r.data),
}
