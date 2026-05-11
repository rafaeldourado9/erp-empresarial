import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { auditoriaApi } from '../../api/audit'

const acaoColor: Record<string, string> = {
  criar: 'bg-green-100 text-green-700',
  atualizar: 'bg-blue-100 text-blue-700',
  deletar: 'bg-red-100 text-red-700',
  login: 'bg-purple-100 text-purple-700',
  logout: 'bg-gray-100 text-gray-600',
  aprovar: 'bg-teal-100 text-teal-700',
  reprovar: 'bg-orange-100 text-orange-700',
}

export function Auditoria() {
  const [registros, setRegistros] = useState<any[]>([])
  const [busca, setBusca] = useState('')
  const [loading, setLoading] = useState(true)
  const [pagina, setPagina] = useState(1)
  const POR_PAGINA = 50

  const carregar = (p = 1) => {
    setLoading(true)
    auditoriaApi.listar({ pagina: p, por_pagina: POR_PAGINA, busca: busca || undefined })
      .then(setRegistros)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    setPagina(1)
    carregar(1)
  }, [busca])

  const formatarData = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Auditoria</h1>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Buscar..."
            className="pl-9 w-64 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Data/Hora</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Usuário</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ação</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Recurso</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Detalhes</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">IP</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && registros.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhum registro encontrado</td></tr>}
            {registros.map(r => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{formatarData(r.criado_em)}</td>
                <td className="px-4 py-3 text-gray-800">{r.usuario_nome || r.usuario_id || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${acaoColor[r.acao] ?? 'bg-gray-100 text-gray-600'}`}>
                    {r.acao}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{r.recurso}{r.recurso_id ? ` #${r.recurso_id.slice(0, 8)}` : ''}</td>
                <td className="px-4 py-3 text-gray-500 max-w-xs truncate" title={r.detalhes}>
                  {r.detalhes || '—'}
                </td>
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">{r.ip || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-center gap-2 mt-4">
        <button onClick={() => { const p = pagina - 1; setPagina(p); carregar(p) }} disabled={pagina === 1}
          className="px-4 py-1.5 border rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40">
          Anterior
        </button>
        <span className="px-4 py-1.5 text-sm text-gray-600">Página {pagina}</span>
        <button onClick={() => { const p = pagina + 1; setPagina(p); carregar(p) }} disabled={registros.length < POR_PAGINA}
          className="px-4 py-1.5 border rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40">
          Próxima
        </button>
      </div>
    </div>
  )
}
