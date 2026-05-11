import { useEffect, useState } from 'react'
import { comissoesApi } from '../../api/commissions'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const hoje = new Date()
const anoMes = (d: Date) => d.toISOString().split('T')[0].slice(0, 7)
const primeiroDia = (ym: string) => `${ym}-01`
const ultimoDia = (ym: string) => {
  const [y, m] = ym.split('-').map(Number)
  return new Date(y, m, 0).toISOString().split('T')[0]
}

export function Comissoes() {
  const [mes, setMes] = useState(anoMes(hoje))
  const [comissoes, setComissoes] = useState<any[]>([])
  const [resumo, setResumo] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const inicio = primeiroDia(mes)
    const fim = ultimoDia(mes)
    Promise.all([
      comissoesApi.listar({ inicio, fim }),
      comissoesApi.resumo(inicio, fim),
    ]).then(([c, r]) => {
      setComissoes(c)
      setResumo(r)
    }).finally(() => setLoading(false))
  }, [mes])

  const statusColor: Record<string, string> = {
    pendente: 'bg-yellow-100 text-yellow-700',
    pago: 'bg-green-100 text-green-700',
    cancelado: 'bg-red-100 text-red-700',
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Comissões</h1>
        <input type="month" value={mes} onChange={e => setMes(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {resumo && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs text-gray-500 mb-1">Total a pagar</p>
            <p className="text-xl font-bold text-gray-900">{fmt(resumo.total_pendente ?? 0)}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs text-gray-500 mb-1">Total pago</p>
            <p className="text-xl font-bold text-green-600">{fmt(resumo.total_pago ?? 0)}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs text-gray-500 mb-1">Vendedores ativos</p>
            <p className="text-xl font-bold text-gray-900">{resumo.vendedores_ativos ?? 0}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Vendedor</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Orçamento</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Venda</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">%</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Comissão</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && comissoes.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhuma comissão no período</td></tr>
            )}
            {comissoes.map(c => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-800 font-medium">{c.vendedor_nome}</td>
                <td className="px-4 py-3 text-gray-600 font-mono">{c.orcamento_numero}</td>
                <td className="px-4 py-3 text-gray-700">{fmt(c.valor_venda)}</td>
                <td className="px-4 py-3 text-gray-600">{c.percentual}%</td>
                <td className="px-4 py-3 font-semibold text-gray-900">{fmt(c.valor_comissao)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColor[c.status] ?? 'bg-gray-100 text-gray-600'}`}>
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
