import { useEffect, useState } from 'react'
import { Plus, Eye, CheckCircle, XCircle, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { orcamentosApi } from '../../api/quotes'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
const statusColor: Record<string, string> = {
  rascunho: 'bg-yellow-100 text-yellow-700',
  enviado: 'bg-blue-100 text-blue-700',
  aprovado: 'bg-green-100 text-green-700',
  reprovado: 'bg-red-100 text-red-700',
}

export function Orcamentos() {
  const [orcamentos, setOrcamentos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filtroStatus, setFiltroStatus] = useState('')

  const carregar = () => {
    setLoading(true)
    orcamentosApi.listar(filtroStatus || undefined)
      .then(setOrcamentos)
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [filtroStatus])

  const handleAprovar = async (id: string) => {
    await orcamentosApi.aprovar(id)
    carregar()
  }

  const handleReprovar = async (id: string) => {
    await orcamentosApi.reprovar(id)
    carregar()
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Orçamentos</h1>
        <Link
          to="/orcamentos/novo"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          Novo Orçamento
        </Link>
      </div>

      <div className="flex gap-2 mb-4">
        {['', 'rascunho', 'enviado', 'aprovado', 'reprovado'].map(s => (
          <button
            key={s}
            onClick={() => setFiltroStatus(s)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filtroStatus === s ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'
            }`}
          >
            {s || 'Todos'}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Número</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Título</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Custo Base</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Valor Venda</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>
            )}
            {!loading && orcamentos.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhum orçamento encontrado</td></tr>
            )}
            {orcamentos.map(o => (
              <tr key={o.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-gray-700">{o.numero}</td>
                <td className="px-4 py-3 text-gray-800">{o.titulo}</td>
                <td className="px-4 py-3 text-gray-700">{fmt(o.custo_base)}</td>
                <td className="px-4 py-3 font-semibold text-gray-900">{fmt(o.valor_venda)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor[o.status] ?? 'bg-gray-100 text-gray-600'}`}>
                    {o.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Link to={`/orcamentos/${o.id}`} className="p-1 text-gray-400 hover:text-blue-600">
                      <Eye className="w-4 h-4" />
                    </Link>
                    {o.status === 'rascunho' && (
                      <>
                        <button onClick={() => handleAprovar(o.id)} className="p-1 text-gray-400 hover:text-green-600">
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleReprovar(o.id)} className="p-1 text-gray-400 hover:text-red-600">
                          <XCircle className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
