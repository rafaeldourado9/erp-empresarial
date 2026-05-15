import { useEffect, useState } from 'react'
import { DollarSign, TrendingUp, TrendingDown, FileText, FileX } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { financeiroApi } from '../../api/finance'
import { orcamentosApi } from '../../api/quotes'
import { MetricSkeleton, CardSkeleton, ListSkeleton } from '../../components/ui/Skeleton'

const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]
const lastDay = today.toISOString().split('T')[0]

function Card({ title, value, icon: Icon, color }: { title: string; value: string; icon: any; color: string }) {
  return (
    <div className="card-hover p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-zinc-500">{title}</p>
          <p className="text-2xl font-bold text-zinc-900 mt-1" style={{ fontVariantNumeric: 'tabular-nums' }}>{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color} shadow-md`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )
}

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

export function Dashboard() {
  const [resumo, setResumo] = useState<any>(null)
  const [orcamentos, setOrcamentos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      financeiroApi.resumo(firstDay, lastDay).catch(() => null),
      orcamentosApi.listar().catch(() => []),
    ]).then(([r, o]) => {
      setResumo(r)
      setOrcamentos(o ?? [])
    }).finally(() => setLoading(false))
  }, [])

  const aprovados = orcamentos.filter(o => o.status === 'aprovado')
  const totalAprovado = aprovados.reduce((s, o) => s + o.valor_venda, 0)
  const chartData = [
    { name: 'Entradas', valor: resumo?.total_entradas ?? 0 },
    { name: 'Saídas', valor: resumo?.total_saidas ?? 0 },
    { name: 'Saldo', valor: resumo?.saldo ?? 0 },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Visão geral do mês atual</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {loading ? (
          <>
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
          </>
        ) : (
          <>
            <Card title="Entradas (mês)" value={fmt(resumo?.total_entradas ?? 0)} icon={TrendingUp} color="bg-green-500" />
            <Card title="Saídas (mês)" value={fmt(resumo?.total_saidas ?? 0)} icon={TrendingDown} color="bg-red-500" />
            <Card title="Saldo" value={fmt(resumo?.saldo ?? 0)} icon={DollarSign} color="bg-blue-600" />
            <Card title="Orç. aprovados (mês)" value={fmt(totalAprovado)} icon={FileText} color="bg-purple-500" />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {loading ? (
          <>
            <CardSkeleton lines={5} />
            <div className="card p-5">
              <div className="space-y-3">
                <div className="skeleton rounded-md" style={{ height: 14, width: '40%' }} />
                <ListSkeleton rows={4} />
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="card p-5">
              <h2 className="text-base font-semibold text-zinc-800 mb-4">Fluxo de Caixa — Mês Atual</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
                  <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#71717a' }} />
                  <YAxis tickFormatter={v => `R$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 12, fill: '#71717a' }} />
                  <Tooltip formatter={(v: number) => fmt(v)} />
                  <Bar dataKey="valor" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h2 className="text-base font-semibold text-zinc-800 mb-4">Últimos Orçamentos</h2>
              <div className="space-y-3">
                {orcamentos.slice(0, 5).map(o => (
                  <div key={o.id} className="flex items-center justify-between text-sm py-1.5 border-b border-zinc-100 last:border-0">
                    <div className="min-w-0 mr-2">
                      <p className="font-medium text-zinc-800 truncate">{o.numero} — {o.titulo}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="font-semibold text-zinc-900" style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(o.valor_venda)}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        o.status === 'aprovado' ? 'bg-green-100 text-green-700' :
                        o.status === 'reprovado' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>{o.status}</span>
                    </div>
                  </div>
                ))}
                {orcamentos.length === 0 && (
                  <div className="text-center py-8 text-zinc-400">
                    <FileX className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Nenhum orçamento ainda</p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
