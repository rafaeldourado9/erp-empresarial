import { useEffect, useState } from 'react'
import { Plus, TrendingUp, TrendingDown, DollarSign, Pencil, Trash2, CheckCircle, XCircle, Bell } from 'lucide-react'
import { financeiroApi } from '../../api/finance'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const hoje = new Date()
const anoMes = (d: Date) => d.toISOString().split('T')[0].slice(0, 7)
const primeiroDia = (ym: string) => `${ym}-01`
const ultimoDia = (ym: string) => {
  const [y, m] = ym.split('-').map(Number)
  return new Date(y, m, 0).toISOString().split('T')[0]
}

type Aba = 'movimentos' | 'dre' | 'contas' | 'categorias'

export function Financeiro() {
  const [mes, setMes] = useState(anoMes(hoje))
  const [aba, setAba] = useState<Aba>('movimentos')
  const [movimentos, setMovimentos] = useState<any[]>([])
  const [resumo, setResumo] = useState<any>(null)
  const [dre, setDre] = useState<any>(null)
  const [contas, setContas] = useState<any[]>([])
  const [categorias, setCategorias] = useState<any[]>([])
  const [filtroTipo, setFiltroTipo] = useState('')
  const [filtroContaTipo, setFiltroContaTipo] = useState('')
  const [filtroContaStatus, setFiltroContaStatus] = useState('pendente')
  const [vencendoDias, setVencendoDias] = useState<number | ''>('')
  const [modal, setModal] = useState<any>(null)
  const [modalConta, setModalConta] = useState<any>(null)
  const [modalCategoria, setModalCategoria] = useState<any>(null)
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

  const carregarDre = () => financeiroApi.dre(inicio, fim).then(setDre)

  const carregarContas = () => {
    const params: any = {}
    if (filtroContaTipo) params.tipo = filtroContaTipo
    if (filtroContaStatus) params.status = filtroContaStatus
    if (vencendoDias !== '') params.vencendo_dias = vencendoDias
    financeiroApi.listarContas(params).then(setContas)
  }

  const carregarCategorias = () => financeiroApi.listarCategorias().then(setCategorias)

  useEffect(() => {
    carregar()
    if (aba === 'dre') carregarDre()
    if (aba === 'contas') carregarContas()
    if (aba === 'categorias') carregarCategorias()
  }, [mes, filtroTipo, aba])

  useEffect(() => {
    if (aba === 'contas') carregarContas()
  }, [filtroContaTipo, filtroContaStatus, vencendoDias])

  const salvarMovimento = async () => {
    await financeiroApi.criarMovimento(modal)
    setModal(null)
    carregar()
  }

  const salvarConta = async () => {
    await financeiroApi.criarConta(modalConta)
    setModalConta(null)
    carregarContas()
  }

  const pagarConta = async (id: string) => {
    await financeiroApi.pagarConta(id)
    carregarContas()
  }

  const cancelarConta = async (id: string) => {
    if (!confirm('Cancelar esta conta?')) return
    await financeiroApi.cancelarConta(id)
    carregarContas()
  }

  const salvarCategoria = async () => {
    await financeiroApi.criarCategoria(modalCategoria)
    setModalCategoria(null)
    carregarCategorias()
  }

  const deletarCategoria = async (id: string) => {
    if (!confirm('Remover categoria?')) return
    await financeiroApi.deletarCategoria(id)
    carregarCategorias()
  }

  const emptyMovimento = {
    tipo: 'entrada',
    categoria: 'Outros',
    descricao: '',
    valor: '',
    data: hoje.toISOString().split('T')[0],
  }

  const emptyConta = {
    tipo: 'pagar',
    descricao: '',
    parceiro: '',
    valor: '',
    data_vencimento: hoje.toISOString().split('T')[0],
    observacoes: '',
  }

  const ABAS: { v: Aba; label: string }[] = [
    { v: 'movimentos', label: 'Movimentos' },
    { v: 'dre', label: 'DRE' },
    { v: 'contas', label: 'Contas' },
    { v: 'categorias', label: 'Categorias' },
  ]

  const vencimentoClass = (data: string, status: string) => {
    if (status !== 'pendente') return ''
    const diff = (new Date(data).getTime() - hoje.getTime()) / 86400000
    if (diff < 0) return 'text-red-600 font-semibold'
    if (diff <= 3) return 'text-orange-500 font-semibold'
    return ''
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Financeiro</h1>
        <div className="flex gap-2">
          {aba === 'contas' && (
            <button onClick={() => setModalConta({ ...emptyConta })}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              <Plus className="w-4 h-4" /> Nova Conta
            </button>
          )}
          {aba === 'categorias' && (
            <button onClick={() => setModalCategoria({ nome: '', tipo: 'despesa', cor: '#6b7280' })}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              <Plus className="w-4 h-4" /> Nova Categoria
            </button>
          )}
          {(aba === 'movimentos' || aba === 'dre') && (
            <button onClick={() => setModal(emptyMovimento)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              <Plus className="w-4 h-4" /> Novo Lançamento
            </button>
          )}
        </div>
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
        <div className="flex gap-1 flex-wrap">
          {ABAS.map(t => (
            <button key={t.v} onClick={() => setAba(t.v)}
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
        {aba === 'contas' && (
          <div className="flex gap-2 flex-wrap items-center">
            <select value={filtroContaTipo} onChange={e => setFiltroContaTipo(e.target.value)}
              className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Pagar + Receber</option>
              <option value="pagar">A Pagar</option>
              <option value="receber">A Receber</option>
            </select>
            <select value={filtroContaStatus} onChange={e => setFiltroContaStatus(e.target.value)}
              className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Todos status</option>
              <option value="pendente">Pendente</option>
              <option value="pago">Pago</option>
              <option value="cancelado">Cancelado</option>
            </select>
            <div className="flex items-center gap-1">
              <Bell className="w-4 h-4 text-orange-500" />
              <input type="number" placeholder="Vence em X dias" min={0} value={vencendoDias}
                onChange={e => setVencendoDias(e.target.value === '' ? '' : +e.target.value)}
                className="border rounded-lg px-2 py-1.5 text-sm w-36 focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
          </div>
        )}
      </div>

      {/* ── Movimentos ── */}
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
                      {m.tipo === 'entrada' ? 'Entrada' : 'Saída'}
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

      {/* ── DRE ── */}
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
                  <span className={linha.valor < 0 ? 'text-red-600' : ''}>{fmt(Math.abs(linha.valor))}</span>
                </div>
              ))}
              {(!dre.linhas || dre.linhas.length === 0) && (
                <p className="text-gray-400 text-sm text-center py-4">Sem dados para o período</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Contas ── */}
      {aba === 'contas' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Tipo</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Parceiro</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Vencimento</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Valor</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {contas.length === 0 && <tr><td colSpan={7} className="text-center py-8 text-gray-400">Nenhuma conta encontrada</td></tr>}
              {contas.map(c => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.tipo === 'pagar' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                      {c.tipo === 'pagar' ? 'A Pagar' : 'A Receber'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-800">{c.descricao}</td>
                  <td className="px-4 py-3 text-gray-600">{c.parceiro || '—'}</td>
                  <td className={`px-4 py-3 ${vencimentoClass(c.data_vencimento, c.status)}`}>
                    {new Date(c.data_vencimento + 'T00:00:00').toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-gray-800">{fmt(c.valor)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      c.status === 'pago' ? 'bg-green-100 text-green-700'
                      : c.status === 'cancelado' ? 'bg-gray-100 text-gray-500'
                      : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {c.status === 'pago' ? 'Pago' : c.status === 'cancelado' ? 'Cancelado' : 'Pendente'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {c.status === 'pendente' && (
                      <div className="flex gap-1">
                        <button onClick={() => pagarConta(c.id)} title="Marcar como pago"
                          className="p-1 text-gray-400 hover:text-green-600">
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button onClick={() => cancelarConta(c.id)} title="Cancelar"
                          className="p-1 text-gray-400 hover:text-red-500">
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Categorias ── */}
      {aba === 'categorias' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {categorias.map(c => (
            <div key={c.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c.cor }} />
                <div>
                  <p className="font-medium text-gray-800 text-sm">{c.nome}</p>
                  <p className="text-xs text-gray-400 capitalize">{c.tipo}</p>
                </div>
              </div>
              <button onClick={() => deletarCategoria(c.id)} className="p-1 text-gray-300 hover:text-red-500">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {categorias.length === 0 && (
            <p className="col-span-3 text-center text-gray-400 text-sm py-8">Nenhuma categoria</p>
          )}
        </div>
      )}

      {/* ── Modal Movimento ── */}
      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">Novo Lançamento</h2>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
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
                    {categorias.map(c => <option key={c.id} value={c.nome}>{c.nome}</option>)}
                    {categorias.length === 0 && <option>Outros</option>}
                  </select>
                </div>
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
              <button onClick={salvarMovimento} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Conta ── */}
      {modalConta && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">Nova Conta</h2>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select value={modalConta.tipo} onChange={e => setModalConta((m: any) => ({ ...m, tipo: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="pagar">A Pagar (Fornecedor)</option>
                    <option value="receber">A Receber (Cliente)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valor (R$)</label>
                  <input type="number" min={0} step={0.01} value={modalConta.valor}
                    onChange={e => setModalConta((m: any) => ({ ...m, valor: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição *</label>
                <input value={modalConta.descricao} onChange={e => setModalConta((m: any) => ({ ...m, descricao: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fornecedor / Cliente</label>
                <input value={modalConta.parceiro} onChange={e => setModalConta((m: any) => ({ ...m, parceiro: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data de Vencimento *</label>
                <input type="date" value={modalConta.data_vencimento} onChange={e => setModalConta((m: any) => ({ ...m, data_vencimento: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
                <textarea value={modalConta.observacoes} onChange={e => setModalConta((m: any) => ({ ...m, observacoes: e.target.value }))}
                  rows={2} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalConta(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvarConta} className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Categoria ── */}
      {modalCategoria && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-4">Nova Categoria</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modalCategoria.nome} onChange={e => setModalCategoria((m: any) => ({ ...m, nome: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select value={modalCategoria.tipo} onChange={e => setModalCategoria((m: any) => ({ ...m, tipo: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="receita">Receita</option>
                    <option value="custo">Custo</option>
                    <option value="despesa">Despesa</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cor</label>
                  <input type="color" value={modalCategoria.cor} onChange={e => setModalCategoria((m: any) => ({ ...m, cor: e.target.value }))}
                    className="w-full h-[38px] border rounded-lg px-1 py-1 cursor-pointer" />
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalCategoria(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvarCategoria} className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
