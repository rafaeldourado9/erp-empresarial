import { useEffect, useState } from 'react'
import { Plus, TrendingUp, TrendingDown, DollarSign } from 'lucide-react'
import { financeiroApi } from '../../api/finance'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const hoje = new Date()
const anoMes = (d: Date) => d.toISOString().split('T')[0].slice(0, 7)
const primeiroDia = (ym: string) => `${ym}-01`
const ultimoDia = (ym: string) => {
  const [y, m] = ym.split('-').map(Number)
  return new Date(y, m, 0).toISOString().split('T')[0]
}

const categorias = ['Venda', 'Serviço', 'Comissão', 'Aluguel', 'Salário', 'Fornecedor', 'Imposto', 'Outros']

export function Financeiro() {
  const [mes, setMes] = useState(anoMes(hoje))
  const [aba, setAba] = useState<'movimentos' | 'dre'>('movimentos')
  const [movimentos, setMovimentos] = useState<any[]>([])
  const [resumo, setResumo] = useState<any>(null)
  const [dre, setDre] = useState<any>(null)
  const [filtroTipo, setFiltroTipo] = useState('')
  const [modal, setModal] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const inicio = primeiroDia(mes)
  const fim = ultimoDia(mes)

  const carregar = () => {
    setLoading(true)
    const params: any = { inicio, fim }
    if (filtroTipo) params.tipo = filtroTipo
    Promise.all([
      financeiroApi.listarMovimentos(params),
      financeiroApi.resumo(inicio, fim),
    ]).then(([movs, res]) => {
      setMovimentos(movs)
      setResumo(res)
    }).finally(() => setLoading(false))
  }

  const carregarDre = () => {
    financeiroApi.dre(inicio, fim).then(setDre)
  }

  useEffect(() => {
    carregar()
    if (aba === 'dre') carregarDre()
  }, [mes, filtroTipo, aba])

  const salvar = async () => {
    await financeiroApi.criarMovimento(modal)
    setModal(null)
    carregar()
  }

  const emptyMovimento = {
    tipo: 'entrada',
    categoria: 'Outros',
    descricao: '',
    valor: '',
    data: hoje.toISOString().split('T')[0],
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Financeiro</h1>
        <button onClick={() => setModal(emptyMovimento)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> Novo Lançamento
        </button>
      </div>

      {/* Resumo cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-green-500 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Entradas</p>
            <p className="text-xl font-bold text-gray-900">{fmt(resumo?.total_entradas ?? 0)}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-red-500 flex items-center justify-center">
            <TrendingDown className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Saídas</p>
            <p className="text-xl font-bold text-gray-900">{fmt(resumo?.total_saidas ?? 0)}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${(resumo?.saldo ?? 0) >= 0 ? 'bg-blue-600' : 'bg-orange-500'}`}>
            <DollarSign className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Saldo</p>
            <p className={`text-xl font-bold ${(resumo?.saldo ?? 0) >= 0 ? 'text-gray-900' : 'text-red-600'}`}>{fmt(resumo?.saldo ?? 0)}</p>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <input type="month" value={mes} onChange={e => setMes(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <div className="flex gap-1">
          {[
            { label: 'Movimentos', v: 'movimentos' },
            { label: 'DRE', v: 'dre' },
          ].map(t => (
            <button key={t.v} onClick={() => setAba(t.v as any)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${aba === t.v ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
              {t.label}
            </button>
          ))}
        </div>
        {aba === 'movimentos' && (
          <div className="flex gap-1">
            {['', 'entrada', 'saida'].map(t => (
              <button key={t} onClick={() => setFiltroTipo(t)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filtroTipo === t ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
                {t === '' ? 'Todos' : t === 'entrada' ? 'Entradas' : 'Saídas'}
              </button>
            ))}
          </div>
        )}
      </div>

      {aba === 'movimentos' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Data</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Categoria</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Tipo</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Valor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
              {!loading && movimentos.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhum lançamento no período</td></tr>}
              {movimentos.map(m => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-600">{new Date(m.data + 'T00:00:00').toLocaleDateString('pt-BR')}</td>
                  <td className="px-4 py-3 text-gray-800">{m.descricao || '—'}</td>
                  <td className="px-4 py-3 text-gray-600">{m.categoria}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${m.tipo === 'entrada' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {m.tipo}
                    </span>
                  </td>
                  <td className={`px-4 py-3 text-right font-semibold ${m.tipo === 'entrada' ? 'text-green-600' : 'text-red-600'}`}>
                    {m.tipo === 'saida' ? '−' : '+'}{fmt(m.valor)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {aba === 'dre' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-w-lg">
          <h2 className="font-semibold text-gray-800 mb-4">DRE — {mes}</h2>
          {!dre ? (
            <p className="text-gray-400 text-sm">Carregando...</p>
          ) : (
            <div className="space-y-2 text-sm">
              {(dre.linhas ?? []).map((linha: any, i: number) => (
                <div key={i} className={`flex justify-between ${linha.negrito ? 'font-semibold text-gray-800 border-t pt-2' : 'text-gray-600'}`}>
                  <span>{linha.descricao}</span>
                  <span className={linha.valor < 0 ? 'text-red-600' : ''}>{fmt(linha.valor)}</span>
                </div>
              ))}
              {(!dre.linhas || dre.linhas.length === 0) && (
                <p className="text-gray-400 text-sm text-center py-4">Sem dados para o período</p>
              )}
            </div>
          )}
        </div>
      )}

      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">Novo Lançamento</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select value={modal.tipo} onChange={e => setModal((m: any) => ({ ...m, tipo: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="entrada">Entrada</option>
                  <option value="saida">Saída</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                <select value={modal.categoria} onChange={e => setModal((m: any) => ({ ...m, categoria: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  {categorias.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                <input value={modal.descricao} onChange={e => setModal((m: any) => ({ ...m, descricao: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valor (R$)</label>
                  <input type="number" min={0} step={0.01} value={modal.valor}
                    onChange={e => setModal((m: any) => ({ ...m, valor: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
                  <input type="date" value={modal.data} onChange={e => setModal((m: any) => ({ ...m, data: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModal(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
