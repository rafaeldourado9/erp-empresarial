import { useEffect, useState, useCallback } from 'react'
import { Plus, Pencil, Trash2, Search, ArrowDownCircle, ArrowUpCircle, AlertTriangle, FileText, History, X } from 'lucide-react'
import { estoqueApi } from '../../api/inventory'

const fmt = (v?: number | null) => v != null ? `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : '—'
const fmtQtd = (v: number, u: string) => `${v.toLocaleString('pt-BR', { maximumFractionDigits: 3 })} ${u}`

// ── Modal: Baixa / Entrada / Ajuste ──────────────────────────────────────────

type MovOp = 'baixa' | 'entrada' | 'ajuste'

function MovimentoModal({ item, op, onFechar, onSalvo }: {
  item: any
  op: MovOp
  onFechar: () => void
  onSalvo: () => void
}) {
  const [quantidade, setQuantidade] = useState<number | ''>('')
  const [observacao, setObservacao] = useState('')
  const [loading, setLoading] = useState(false)

  const labels: Record<MovOp, { titulo: string; btn: string; cor: string }> = {
    baixa:   { titulo: 'Dar Baixa',     btn: 'Confirmar Baixa',   cor: 'bg-red-600 hover:bg-red-700' },
    entrada: { titulo: 'Registrar Entrada', btn: 'Confirmar Entrada', cor: 'bg-green-600 hover:bg-green-700' },
    ajuste:  { titulo: 'Ajuste de Estoque', btn: 'Confirmar Ajuste',  cor: 'bg-blue-600 hover:bg-blue-700' },
  }
  const l = labels[op]

  const salvar = async () => {
    if (quantidade === '' || Number(quantidade) < 0) return
    setLoading(true)
    try {
      await estoqueApi[op](item.id, { quantidade: Number(quantidade), observacao: observacao || undefined })
      onSalvo()
      onFechar()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-lg">{l.titulo}</h2>
          <button onClick={onFechar}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Item: <strong>{item.descricao}</strong><br />
          Estoque atual: <strong>{fmtQtd(item.quantidade, item.unidade)}</strong>
        </p>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {op === 'ajuste' ? 'Novo estoque' : 'Quantidade'} ({item.unidade})
            </label>
            <input type="number" min={0} step={0.001} value={quantidade}
              onChange={e => setQuantidade(e.target.value === '' ? '' : +e.target.value)}
              autoFocus
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Observação</label>
            <input value={observacao} onChange={e => setObservacao(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Opcional" />
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={onFechar} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
          <button onClick={salvar} disabled={loading || quantidade === ''}
            className={`flex-1 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50 ${l.cor}`}>
            {loading ? 'Salvando...' : l.btn}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Modal: Histórico de movimentos ────────────────────────────────────────────

function HistoricoModal({ item, onFechar }: { item: any; onFechar: () => void }) {
  const [movimentos, setMovimentos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    estoqueApi.movimentos(item.id).then(setMovimentos).finally(() => setLoading(false))
  }, [item.id])

  const tipoLabel: Record<string, { label: string; cor: string }> = {
    baixa:   { label: 'Baixa',   cor: 'text-red-600 bg-red-50' },
    entrada: { label: 'Entrada', cor: 'text-green-600 bg-green-50' },
    ajuste:  { label: 'Ajuste',  cor: 'text-blue-600 bg-blue-50' },
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-lg">Histórico — {item.descricao}</h2>
          <button onClick={onFechar}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        {loading && <p className="text-center text-gray-400 py-8">Carregando...</p>}
        {!loading && movimentos.length === 0 && (
          <p className="text-center text-gray-400 py-8">Nenhum movimento registrado</p>
        )}
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {movimentos.map((m: any) => {
            const t = tipoLabel[m.tipo] ?? { label: m.tipo, cor: 'text-gray-600 bg-gray-50' }
            return (
              <div key={m.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm">
                <div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${t.cor}`}>{t.label}</span>
                  {m.observacao && <span className="ml-2 text-gray-500">{m.observacao}</span>}
                  <p className="text-xs text-gray-400 mt-0.5">
                    {m.quantidade_anterior} → {m.quantidade_posterior} {item.unidade}
                  </p>
                </div>
                <div className="text-right text-gray-600">
                  <p className={m.tipo === 'baixa' ? 'text-red-600 font-medium' : 'text-green-600 font-medium'}>
                    {m.tipo === 'baixa' ? '-' : '+'}{m.quantidade} {item.unidade}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(m.criado_em).toLocaleString('pt-BR')}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// ── Componente principal ──────────────────────────────────────────────────────

export function Estoque() {
  const [itens, setItens] = useState<any[]>([])
  const [alertas, setAlertas] = useState<any[]>([])
  const [busca, setBusca] = useState('')
  const [modal, setModal] = useState<any>(null)
  const [movModal, setMovModal] = useState<{ item: any; op: MovOp } | null>(null)
  const [historicoItem, setHistoricoItem] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<'todos' | 'alertas'>('todos')
  const [baixandoPdf, setBaixandoPdf] = useState(false)

  const carregar = useCallback(() => {
    setLoading(true)
    Promise.all([
      estoqueApi.listar(busca || undefined),
      estoqueApi.alertas(),
    ]).then(([its, als]) => {
      setItens(its)
      setAlertas(als)
    }).finally(() => setLoading(false))
  }, [busca])

  useEffect(() => { carregar() }, [carregar])

  const salvar = async () => {
    try {
      if (modal.id) {
        await estoqueApi.atualizar(modal.id, {
          descricao: modal.descricao, marca: modal.marca, modelo: modal.modelo,
          quantidade: modal.quantidade, estoque_minimo: modal.estoque_minimo || undefined,
          valor_unitario: modal.valor_unitario || undefined,
          valor_atribuido: modal.valor_atribuido || undefined,
          unidade: modal.unidade,
        })
      } else {
        await estoqueApi.criar({
          descricao: modal.descricao, marca: modal.marca, modelo: modal.modelo,
          quantidade: modal.quantidade, estoque_minimo: modal.estoque_minimo || undefined,
          valor_unitario: modal.valor_unitario || undefined,
          valor_atribuido: modal.valor_atribuido || undefined,
          unidade: modal.unidade,
        })
      }
      setModal(null)
      carregar()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    }
  }

  const deletar = async (id: string) => {
    if (!confirm('Remover item?')) return
    await estoqueApi.deletar(id)
    carregar()
  }

  const downloadPdf = async () => {
    setBaixandoPdf(true)
    try {
      const blob = await estoqueApi.relatoriopdf()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `estoque_${new Date().toISOString().slice(0, 10)}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      alert('Erro ao gerar relatório')
    } finally {
      setBaixandoPdf(false)
    }
  }

  const empty = { descricao: '', marca: '', modelo: '', quantidade: 0, estoque_minimo: '', valor_unitario: '', valor_atribuido: '', unidade: 'un' }

  const listaExibida = tab === 'alertas' ? alertas : itens

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-900">Estoque</h1>
          {alertas.length > 0 && (
            <span className="flex items-center gap-1 text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">
              <AlertTriangle className="w-3 h-3" /> {alertas.length} alerta(s)
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button onClick={downloadPdf} disabled={baixandoPdf}
            className="flex items-center gap-2 border border-gray-200 text-gray-600 hover:bg-gray-50 px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50">
            <FileText className="w-4 h-4" /> {baixandoPdf ? 'Gerando...' : 'Relatório PDF'}
          </button>
          <button onClick={() => setModal(empty)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
            <Plus className="w-4 h-4" /> Novo Item
          </button>
        </div>
      </div>

      {/* Tabs + busca */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          <button onClick={() => setTab('todos')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === 'todos' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}>
            Todos ({itens.length})
          </button>
          <button onClick={() => setTab('alertas')}
            className={`flex items-center gap-1 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === 'alertas' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}>
            <AlertTriangle className="w-3 h-3" /> Alertas ({alertas.length})
          </button>
        </div>

        {tab === 'todos' && (
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Buscar..."
              className="pl-9 w-60 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Marca / Modelo</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Qtd</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Mín.</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Valor Un.</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && listaExibida.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">
                {tab === 'alertas' ? 'Nenhum alerta de estoque' : 'Nenhum item cadastrado'}
              </td></tr>
            )}
            {listaExibida.map((i: any) => (
              <tr key={i.id} className={`hover:bg-gray-50 ${i.alerta_estoque_baixo ? 'bg-red-50' : ''}`}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {i.alerta_estoque_baixo && <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />}
                    <span className="text-gray-800 font-medium">{i.descricao}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">{[i.marca, i.modelo].filter(Boolean).join(' / ') || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`font-medium ${i.alerta_estoque_baixo ? 'text-red-600' : 'text-gray-700'}`}>
                    {fmtQtd(i.quantidade, i.unidade)}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{i.estoque_minimo != null ? fmtQtd(i.estoque_minimo, i.unidade) : '—'}</td>
                <td className="px-4 py-3 text-gray-700">{fmt(i.valor_unitario)}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <button title="Baixa" onClick={() => setMovModal({ item: i, op: 'baixa' })}
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                      <ArrowDownCircle className="w-4 h-4" />
                    </button>
                    <button title="Entrada" onClick={() => setMovModal({ item: i, op: 'entrada' })}
                      className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded">
                      <ArrowUpCircle className="w-4 h-4" />
                    </button>
                    <button title="Histórico" onClick={() => setHistoricoItem(i)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                      <History className="w-4 h-4" />
                    </button>
                    <button title="Editar" onClick={() => setModal({ ...i })}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button title="Remover" onClick={() => deletar(i.id)}
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal Criar/Editar */}
      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-lg">{modal.id ? 'Editar' : 'Novo'} Item</h2>
              <button onClick={() => setModal(null)}><X className="w-5 h-5 text-gray-400" /></button>
            </div>
            <div className="space-y-3">
              {[
                { k: 'descricao', label: 'Descrição *', required: true },
                { k: 'marca', label: 'Marca' },
                { k: 'modelo', label: 'Modelo' },
                { k: 'unidade', label: 'Unidade' },
              ].map(({ k, label }) => (
                <div key={k}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input value={modal[k] ?? ''}
                    onChange={e => setModal((m: any) => ({ ...m, [k]: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { k: 'quantidade', label: 'Quantidade' },
                  { k: 'estoque_minimo', label: 'Estoque Mínimo' },
                  { k: 'valor_unitario', label: 'Valor Un. (R$)' },
                  { k: 'valor_atribuido', label: 'Valor Atribuído (R$)' },
                ].map(({ k, label }) => (
                  <div key={k}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input type="number" min={0} step={k === 'quantidade' || k === 'estoque_minimo' ? 0.001 : 0.01}
                      value={modal[k] ?? ''}
                      onChange={e => setModal((m: any) => ({ ...m, [k]: e.target.value === '' ? '' : +e.target.value }))}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                ))}
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModal(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} disabled={!modal.descricao}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50">Salvar</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Baixa/Entrada/Ajuste */}
      {movModal && (
        <MovimentoModal
          item={movModal.item}
          op={movModal.op}
          onFechar={() => setMovModal(null)}
          onSalvo={carregar}
        />
      )}

      {/* Modal Histórico */}
      {historicoItem && (
        <HistoricoModal item={historicoItem} onFechar={() => setHistoricoItem(null)} />
      )}
    </div>
  )
}
