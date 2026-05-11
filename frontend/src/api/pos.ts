import { api } from './client'

export const caixaApi = {
  statusSessao: () => api.get('/caixa/sessao').then(r => r.data),
  abrirSessao: (saldo_inicial: number) => api.post('/caixa/sessao/abrir', { saldo_inicial }).then(r => r.data),
  fecharSessao: () => api.post('/caixa/sessao/fechar').then(r => r.data),

  listarProdutos: () => api.get('/caixa/produtos').then(r => r.data),
  criarProduto: (data: object) => api.post('/caixa/produtos', data).then(r => r.data),
  atualizarProduto: (id: string, data: object) => api.put(`/caixa/produtos/${id}`, data).then(r => r.data),
  deletarProduto: (id: string) => api.delete(`/caixa/produtos/${id}`),

  listarOS: (params?: object) => api.get('/caixa/os', { params }).then(r => r.data),
  criarOS: (data: object) => api.post('/caixa/os', data).then(r => r.data),
  obterOS: (id: string) => api.get(`/caixa/os/${id}`).then(r => r.data),
  concluirOS: (id: string) => api.patch(`/caixa/os/${id}/concluir`).then(r => r.data),
  cancelarOS: (id: string) => api.patch(`/caixa/os/${id}/cancelar`).then(r => r.data),
}
