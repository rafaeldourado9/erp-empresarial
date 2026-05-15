import { useEffect, useState } from 'react'
import { Plus, Eye, CheckCircle, XCircle, Send, Download, Inbox } from 'lucide-react'
import { Link } from 'react-router-dom'
import { orcamentosApi } from '../../api/quotes'
import { TableRowsSkeleton } from '../../components/ui/Skeleton'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const STATUS_CONFIG: Record<string, { label: string; cls: string }> = {
  rascunho: { label: 'Rascunho', cls: 'bg-yellow-100 text-yellow-700' },
  enviado:  { label: 'Enviado',  cls: 'bg-blue-100 text-blue-700' },
  aprovado: { label: 'Aprovado', cls: 'bg-green-100 text-green-700' },
  reprovado:{ label: 'Reprovado',cls: 'bg-red-100 text-red-700' },
  fechado:  { label: 'Fechado',  cls: 'bg-gray-100 text-gray-600' },
}

const FILTROS = [
  { v: '', label: 'Todos' },
  { v: 'rascunho', label: 'Rascunho' },
  { v: 'enviado', label: 'Enviado' },
  { v: 'aprovado', label: 'Aprovado' },
  { v: 'reprovado', label: 'Reprovado' },
]

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

  const handleEnviar = async (id: string) => {
    if (!confirm('Marcar orçamento como enviado?')) return
    await orcamentosApi.enviar(id)
    carregar()
  }

  const handleAprovar = async (id: string) => {
    await orcamentosApi.aprovar(id)
    carregar()
  }

  const handleReprovar = async (id: string) => {
    await orcamentosApi.reprovar(id)
    carregar()
  }

  const handleBaixarPdf = async (id: string, numero: string) => {
    try {
      const blob = await orcamentosApi.baixarPdf(id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `orcamento-${numero}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao gerar PDF')
    }
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

      <div className="flex gap-2 mb-4 flex-wrap">
        {FILTROS.map(f => (
          <button
            key={f.v}
            onClick={() => setFiltroStatus(f.v)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filtroStatus === f.v ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'
            }`}
          >
            {f.label}
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
            {loading && <TableRowsSkeleton rows={6} cols={6} />}
            {!loading && orcamentos.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-12 text-zinc-400">
                  <Inbox className="w-10 h-10 mx-auto mb-2 opacity-40" />
                  <p className="text-sm">Nenhum orçamento encontrado</p>
                </td>
              </tr>
            )}
            {orcamentos.map(o => {
              const sc = STATUS_CONFIG[o.status] ?? { label: o.status, cls: 'bg-gray-100 text-gray-600' }
              return (
                <tr key={o.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-gray-700">{o.numero}</td>
                  <td className="px-4 py-3 text-gray-800">{o.titulo}</td>
                  <td className="px-4 py-3 text-gray-700">{fmt(o.custo_base)}</td>
                  <td className="px-4 py-3 font-semibold text-gray-900">{fmt(o.valor_venda)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${sc.cls}`}>
                      {sc.label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <Link to={`/orcamentos/${o.id}`} className="p-1 text-gray-400 hover:text-blue-600" title="Editar">
                        <Eye className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => handleBaixarPdf(o.id, o.numero)}
                        className="p-1 text-gray-400 hover:text-red-500"
                        title="Baixar PDF"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      {o.status === 'rascunho' && (
                        <button onClick={() => handleEnviar(o.id)} className="p-1 text-gray-400 hover:text-blue-600" title="Enviar">
                          <Send className="w-4 h-4" />
                        </button>
                      )}
                      {(o.status === 'enviado' || o.status === 'rascunho') && (
                        <>
                          <button onClick={() => handleAprovar(o.id)} className="p-1 text-gray-400 hover:text-green-600" title="Aprovar">
                            <CheckCircle className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleReprovar(o.id)} className="p-1 text-gray-400 hover:text-red-600" title="Reprovar">
                            <XCircle className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
