import { api } from './client'

export const premissasApi = {
  listar: () => api.get('/premissas').then(r => r.data),
  criar: (data: object) => api.post('/premissas', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/premissas/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/premissas/${id}`),
}

export const templatesApi = {
  listar: () => api.get('/orcamentos/templates').then(r => r.data as TemplateItem[]),
  criar: (nome: string, file: File, descricao?: string, tornarPadrao?: boolean) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/orcamentos/templates', form, {
      params: { nome, descricao, tornar_padrao: tornarPadrao ?? false },
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data as TemplateItem)
  },
  definirPadrao: (id: string) => api.patch(`/orcamentos/templates/${id}/padrao`).then(r => r.data as TemplateItem),
  deletar: (id: string) => api.delete(`/orcamentos/templates/${id}`),
  baixarOriginal: (id: string) =>
    api.get(`/orcamentos/templates/${id}/download`, { responseType: 'blob' }).then(r => r.data as Blob),
}

export interface TemplateItem {
  id: string
  nome: string
  descricao: string | null
  padrao: boolean
  ativo: boolean
  criado_em: string
}

export const orcamentosApi = {
  listar: (status?: string) => api.get('/orcamentos', { params: status ? { status } : {} }).then(r => r.data),
  obter: (id: string) => api.get(`/orcamentos/${id}`).then(r => r.data),
  criar: (data: object) => api.post('/orcamentos', data).then(r => r.data),
  atualizar: (id: string, data: object) => api.put(`/orcamentos/${id}`, data).then(r => r.data),
  deletar: (id: string) => api.delete(`/orcamentos/${id}`),
  calcular: (data: object) => api.post('/orcamentos/calcular', data).then(r => r.data),
  enviar: (id: string) => api.patch(`/orcamentos/${id}/enviar`).then(r => r.data),
  aprovar: (id: string) => api.patch(`/orcamentos/${id}/aprovar`).then(r => r.data),
  reprovar: (id: string) => api.patch(`/orcamentos/${id}/reprovar`).then(r => r.data),
  fechar: (id: string, data: object) => api.patch(`/orcamentos/${id}/fechar`, data).then(r => r.data),
  baixarPdf: (id: string) =>
    api.get(`/orcamentos/${id}/pdf`, { responseType: 'blob' }).then(r => r.data as Blob),
  baixarDocx: (id: string, templateId?: string) =>
    api.get(`/orcamentos/${id}/docx`, {
      responseType: 'blob',
      params: templateId ? { template_id: templateId } : {},
    }).then(r => r.data as Blob),
  baixarTemplateExemplo: () =>
    api.get(`/orcamentos/template/exemplo`, { responseType: 'blob' }).then(r => r.data as Blob),
}
