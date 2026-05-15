import { api } from './client'

export const solarApi = {
  // Catálogo
  modulos:     (params?: Record<string, string>) => api.get('/solar/modulos', { params }).then(r => r.data),
  inversores:  (params?: Record<string, string>) => api.get('/solar/inversores', { params }).then(r => r.data),
  componentes: (params?: Record<string, string>) => api.get('/solar/componentes', { params }).then(r => r.data),
  estados:     () => api.get('/solar/estados').then(r => r.data),

  // Dimensionamento
  dimensionar: (data: object) => api.post('/solar/dimensionar', data).then(r => r.data),
  sugerirInversor: (potencia_kwp: number, tipo = 'string', fases = 3) =>
    api.get('/solar/dimensionar/sugerir-inversor', { params: { potencia_kwp, tipo, fases } }).then(r => r.data),
}
