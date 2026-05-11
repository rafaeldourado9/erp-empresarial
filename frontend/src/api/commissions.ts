import { api } from './client'

export const comissoesApi = {
  listar: (params?: object) => api.get('/comissoes', { params }).then(r => r.data),
  resumo: (inicio: string, fim: string) => api.get('/comissoes/resumo', { params: { inicio, fim } }).then(r => r.data),
}
