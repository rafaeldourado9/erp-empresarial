import { useEffect, useState } from 'react'
import { DollarSign, TrendingUp, TrendingDown, FileText } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { financeiroApi } from '../../api/finance'
import { orcamentosApi } from '../../api/quotes'

const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]
const lastDay = today.toISOString().split('T')[0]

function Card({ title, value, icon: Icon, color }: { title: string; value: string; icon: any; color: string }) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
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

  useEffect(() => {
    financeiroApi.resumo(firstDay, lastDay).then(setResumo).catch(() => {})
    orcamentosApi.listar().then(setOrcamentos).catch(() => {})
  }, [])

  const aprovados = orcamentos.filter(o => o.status === 'aprovado')
  const totalAprovado = aprovados.reduce((s, o) => s + o.valor_venda, 0)
  const chartData = [
    { name: 'Entradas', valor: resumo?.total_entradas ?? 0 },
    { name: 'Saídas', valor: resumo?.total_saidas ?? 0 },
    { name: 'Saldo', valor: resumo?.saldo ?? 0 },
  ]

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card title="Entradas (mês)" value={fmt(resumo?.total_entradas ?? 0)} icon={TrendingUp} color="bg-green-500" />
        <Card title="Saídas (mês)" value={fmt(resumo?.total_saidas ?? 0)} icon={TrendingDown} color="bg-red-500" />
        <Card title="Saldo" value={fmt(resumo?.saldo ?? 0)} icon={DollarSign} color="bg-blue-600" />
        <Card title="Orç. aprovados (mês)" value={fmt(totalAprovado)} icon={FileText} color="bg-purple-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Fluxo de Caixa — Mês Atual</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={v => `R$${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => fmt(v)} />
              <Bar dataKey="valor" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Últimos Orçamentos</h2>
          <div className="space-y-3">
            {orcamentos.slice(0, 5).map(o => (
              <div key={o.id} className="flex items-center justify-between text-sm">
                <div>
                  <p className="font-medium text-gray-800">{o.numero} — {o.titulo}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{fmt(o.valor_venda)}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    o.status === 'aprovado' ? 'bg-green-100 text-green-700' :
                    o.status === 'reprovado' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>{o.status}</span>
                </div>
              </div>
            ))}
            {orcamentos.length === 0 && (
              <p className="text-gray-400 text-sm text-center py-4">Nenhum orçamento ainda</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
