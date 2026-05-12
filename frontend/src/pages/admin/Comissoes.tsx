import { useEffect, useState } from 'react'
import { CheckCircle, DollarSign, Users, Clock } from 'lucide-react'
import { comissoesApi } from '../../api/commissions'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const hoje = new Date()
const anoMes = (d: Date) => d.toISOString().split('T')[0].slice(0, 7)
const primeiroDia = (ym: string) => `${ym}-01`
const ultimoDia = (ym: string) => {
  const [y, m] = ym.split('-').map(Number)
  return new Date(y, m, 0).toISOString().split('T')[0]
}

const STATUS_TABS = [
  { v: '',          label: 'Todas' },
  { v: 'pendente',  label: 'A Pagar' },
  { v: 'pago',      label: 'Pagas' },
  { v: 'cancelado', label: 'Canceladas' },
]

const statusCls: Record<string, string> = {
  pendente:  'badge-yellow',
  pago:      'badge-green',
  cancelado: 'badge-gray',
}

const statusLabel: Record<string, string> = {
  pendente:  'A Pagar',
  pago:      'Pago',
  cancelado: 'Cancelado',
}

export function Comissoes() {
  const [mes, setMes] = useState(anoMes(hoje))
  const [statusFiltro, setStatusFiltro] = useState('')
  const [comissoes, setComissoes] = useState<any[]>([])
  const [resumo, setResumo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [pagando, setPagando] = useState<string | null>(null)

  const carregar = () => {
    setLoading(true)
    const inicio = primeiroDia(mes)
    const fim = ultimoDia(mes)
    const params: any = { inicio, fim }
    if (statusFiltro) params.status = statusFiltro
    Promise.all([
      comissoesApi.listar(params),
      comissoesApi.resumo(inicio, fim),
    ]).then(([c, r]) => {
      setComissoes(c)
      setResumo(r)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [mes, statusFiltro])

  const pagar = async (id: string) => {
    if (!confirm('Marcar comissão como paga?')) return
    setPagando(id)
    try {
      await comissoesApi.pagar(id)
      carregar()
    } finally {
      setPagando(null)
    }
  }

  const totalExibido = comissoes.reduce((s, c) => s + c.valor_comissao, 0)

  return (
    <div className="p-6">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Comissões de Vendedores</h1>
          <p className="text-sm text-gray-500 mt-1">
            Geradas automaticamente ao aprovar uma proposta com vendedor vinculado
          </p>
        </div>
        <input
          type="month" value={mes}
          onChange={e => setMes(e.target.value)}
          className="form-input w-36"
        />
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100" style={{ borderTop: '3px solid #D97706' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">A Pagar</p>
              <p className="text-2xl font-bold text-gray-900 mt-1.5" style={{ fontVariantNumeric: 'tabular-nums' }}>
                {fmt(resumo?.total_pendente ?? 0)}
              </p>
            </div>
            <div className="w-10 h-10 flex items-center justify-center rounded-xl bg-yellow-50">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100" style={{ borderTop: '3px solid #16A34A' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Pago</p>
              <p className="text-2xl font-bold text-green-600 mt-1.5" style={{ fontVariantNumeric: 'tabular-nums' }}>
                {fmt(resumo?.total_pago ?? 0)}
              </p>
            </div>
            <div className="w-10 h-10 flex items-center justify-center rounded-xl bg-green-50">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100" style={{ borderTop: '3px solid #2563EB' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Vendedores c/ Comissão</p>
              <p className="text-2xl font-bold text-gray-900 mt-1.5">{resumo?.vendedores_ativos ?? 0}</p>
            </div>
            <div className="w-10 h-10 flex items-center justify-center rounded-xl bg-blue-50">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-100 flex items-center flex-wrap gap-3">
          <span className="text-sm font-semibold text-gray-800">Detalhamento</span>

          <div className="flex border border-gray-200 rounded-lg overflow-hidden">
            {STATUS_TABS.map(t => (
              <button key={t.v} onClick={() => setStatusFiltro(t.v)}
                className={`px-3 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors ${
                  statusFiltro === t.v
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
                }`}>
                {t.label}
              </button>
            ))}
          </div>

          {comissoes.length > 0 && (
            <span className="text-xs text-gray-400 ml-auto">
              {comissoes.length} registro(s) · {fmt(totalExibido)}
            </span>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="gov-table">
            <thead>
              <tr>
                <th>Vendedor</th>
                <th>Nº Proposta</th>
                <th>Data</th>
                <th className="text-right">Valor da Venda</th>
                <th>% Comissão</th>
                <th className="text-right">Valor Comissão</th>
                <th>Situação</th>
                <th style={{ width: 60 }}>Ação</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={8} className="text-center py-10 text-gray-400">Carregando...</td></tr>
              )}
              {!loading && comissoes.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-gray-400">
                    {statusFiltro === 'pendente'
                      ? 'Nenhuma comissão a pagar no período'
                      : statusFiltro === 'pago'
                      ? 'Nenhuma comissão paga no período'
                      : 'Nenhuma comissão gerada no período'}
                    <p className="text-xs mt-1 text-gray-300">
                      Comissões são criadas automaticamente ao aprovar uma proposta com vendedor e % cadastrado
                    </p>
                  </td>
                </tr>
              )}
              {comissoes.map(c => (
                <tr key={c.id}>
                  <td className="font-medium">{c.vendedor_nome}</td>
                  <td className="font-mono text-gray-500" style={{ fontVariantNumeric: 'tabular-nums' }}>{c.orcamento_numero ?? '—'}</td>
                  <td className="text-gray-500 whitespace-nowrap" style={{ fontVariantNumeric: 'tabular-nums' }}>
                    {new Date(c.criado_em).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="text-right text-gray-500" style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(c.valor_venda)}</td>
                  <td>
                    <span className="badge-blue">{c.percentual}%</span>
                  </td>
                  <td className="text-right font-semibold text-gray-900" style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(c.valor_comissao)}</td>
                  <td>
                    <span className={statusCls[c.status] ?? 'badge-yellow'}>
                      {statusLabel[c.status] ?? c.status}
                    </span>
                  </td>
                  <td>
                    {c.status === 'pendente' && (
                      <button
                        onClick={() => pagar(c.id)}
                        disabled={pagando === c.id}
                        title="Marcar como pago"
                        className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded hover:bg-green-600 hover:text-white transition-colors disabled:opacity-50">
                        <DollarSign className="w-3 h-3" />
                        {pagando === c.id ? '...' : 'Pagar'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
