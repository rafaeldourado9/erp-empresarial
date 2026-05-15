import { useEffect, useState, useCallback, ReactNode } from 'react'
import { Plus, Trash2, Power, ClipboardList, Package, CheckCircle, XCircle, Pencil, FileText, Download } from 'lucide-react'
import { caixaApi, downloadBlob } from '../../api/pos'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

const formasPagamento = ['Dinheiro', 'Débito', 'Crédito', 'Pix', 'Transferência']

interface Produto {
  id: string
  nome: string
  descricao?: string
  valor: number
  unidade: string
  ativo: boolean
}

interface ItemOS {
  _key: string
  produto_id?: string
  nome_produto?: string
  descricao: string
  quantidade: number
  valor_unitario: number
}

// ── Aba: Nova OS ──────────────────────────────────────────────────────────────

function NovaOSForm({ sessaoId: _sessaoId, produtos, onCriada, onProdutosChange }: {
  sessaoId: string
  produtos: Produto[]
  onCriada: () => void
  onProdutosChange: () => Promise<Produto[]> | void
}) {
  const [nomeCliente, setNomeCliente] = useState('')
  const [tipoServico, setTipoServico] = useState('')
  const [descricaoServico, setDescricaoServico] = useState('')
  const [valorServico, setValorServico] = useState<number | ''>('')
  const [itens, setItens] = useState<ItemOS[]>([])
  const [desconto, setDesconto] = useState<number | ''>(0)
  const [formaPagamento, setFormaPagamento] = useState('Dinheiro')
  const [observacoes, setObservacoes] = useState('')
  const [loading, setLoading] = useState(false)
  const [modalProduto, setModalProduto] = useState<{ nome: string; valor: number | ''; unidade: string; descricao?: string } | null>(null)

  const criarProdutoInline = async () => {
    if (!modalProduto?.nome || modalProduto.valor === '') return
    try {
      const novo = await caixaApi.criarProduto({
        nome: modalProduto.nome,
        descricao: modalProduto.descricao || undefined,
        valor: Number(modalProduto.valor),
        unidade: modalProduto.unidade || 'un',
      })
      setModalProduto(null)
      await onProdutosChange()
      // Adicionar imediatamente à OS em construção
      addItemProduto(novo as Produto)
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao criar produto')
    }
  }

  const addItemProduto = (p: Produto) => {
    setItens(prev => [...prev, {
      _key: crypto.randomUUID(),
      produto_id: p.id,
      nome_produto: p.nome,
      descricao: p.nome,
      quantidade: 1,
      valor_unitario: p.valor,
    }])
  }

  const addItemManual = () => {
    setItens(prev => [...prev, {
      _key: crypto.randomUUID(),
      descricao: '',
      quantidade: 1,
      valor_unitario: 0,
    }])
  }

  const updateItem = (key: string, changes: Partial<ItemOS>) => {
    setItens(prev => prev.map(i => i._key === key ? { ...i, ...changes } : i))
  }

  const removeItem = (key: string) => setItens(prev => prev.filter(i => i._key !== key))

  const valorServNum = Number(valorServico) || 0
  const valorProdutos = itens.reduce((s, i) => s + i.quantidade * i.valor_unitario, 0)
  const descontoNum = Number(desconto) || 0
  const total = Math.max(0, valorServNum + valorProdutos - descontoNum)

  const criar = async () => {
    if (!nomeCliente || !tipoServico || !descricaoServico) return
    setLoading(true)
    try {
      await caixaApi.criarOS({
        nome_cliente: nomeCliente,
        tipo_servico: tipoServico,
        descricao_servico: descricaoServico,
        valor_servico: valorServNum,
        forma_pagamento: formaPagamento,
        desconto: descontoNum,
        observacoes: observacoes || undefined,
        itens: itens.map(i => i.produto_id
          ? { produto_id: i.produto_id, quantidade: i.quantidade }
          : { descricao: i.descricao, quantidade: i.quantidade, valor_unitario: i.valor_unitario }),
      })
      setNomeCliente('')
      setTipoServico('')
      setDescricaoServico('')
      setValorServico('')
      setItens([])
      setDesconto(0)
      setObservacoes('')
      onCriada()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao criar OS')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Formulário */}
      <div className="lg:col-span-2 space-y-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">Dados da OS</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Cliente *</label>
              <input value={nomeCliente} onChange={e => setNomeCliente(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: João Silva" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Serviço *</label>
                <input value={tipoServico} onChange={e => setTipoServico(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Manutenção, Instalação..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Valor do Serviço (R$)</label>
                <input type="number" value={valorServico}
                  onChange={e => setValorServico(e.target.value === '' ? '' : +e.target.value)}
                  min={0} step={0.01} placeholder="0,00"
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descrição do Serviço *</label>
              <textarea value={descricaoServico} onChange={e => setDescricaoServico(e.target.value)} rows={2}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Descreva o serviço prestado..." />
            </div>
          </div>
        </div>

        {/* Produtos */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-800">Produtos</h2>
            <button onClick={addItemManual}
              className="text-xs bg-gray-50 text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-100 flex items-center gap-1">
              <Plus className="w-3 h-3" /> Avulso
            </button>
          </div>
          <div className="space-y-2">
            {itens.length === 0 && (
              <p className="text-center text-gray-400 text-sm py-4">
                Selecione produtos do catálogo ao lado ou adicione um item avulso
              </p>
            )}
            {itens.map(item => (
              <div key={item._key} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex-1 text-sm text-gray-700 truncate">
                  {item.produto_id
                    ? <span className="font-medium">{item.nome_produto}</span>
                    : <input value={item.descricao} placeholder="Descrição"
                        onChange={e => updateItem(item._key, { descricao: e.target.value })}
                        className="w-full bg-white border rounded px-2 py-1 text-sm" />
                  }
                </div>
                <input type="number" value={item.quantidade} min={0.001} step={0.001}
                  onChange={e => updateItem(item._key, { quantidade: +e.target.value })}
                  className="w-16 border rounded px-2 py-1 text-sm text-center bg-white" />
                <span className="text-gray-400 text-xs">×</span>
                <input type="number" value={item.valor_unitario} min={0} step={0.01}
                  onChange={e => updateItem(item._key, { valor_unitario: +e.target.value })}
                  disabled={!!item.produto_id}
                  className="w-24 border rounded px-2 py-1 text-sm bg-white disabled:bg-gray-100" />
                <span className="text-sm font-medium text-gray-700 w-24 text-right">
                  {fmt(item.quantidade * item.valor_unitario)}
                </span>
                <button onClick={() => removeItem(item._key)} className="text-gray-300 hover:text-red-500">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Painel lateral: catálogo + resumo */}
      <div className="space-y-4">
        {/* Catálogo rápido */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 text-sm">Catálogo</h3>
            <button
              onClick={() => setModalProduto({ nome: '', valor: '', unidade: 'un' })}
              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
              title="Criar novo produto"
            >
              <Plus className="w-3.5 h-3.5" /> Novo produto
            </button>
          </div>
          {produtos.length === 0 ? (
            <p className="text-xs text-gray-400 py-2">Nenhum produto cadastrado. Use o botão acima ou a aba Produtos.</p>
          ) : (
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {produtos.map(p => (
                <button key={p.id} onClick={() => addItemProduto(p)}
                  className="w-full text-left flex items-center justify-between p-2 hover:bg-blue-50 rounded-lg text-sm group">
                  <span className="text-gray-700 truncate">{p.nome}</span>
                  <span className="text-blue-600 font-medium flex-shrink-0 ml-2">{fmt(p.valor)}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Resumo + pagamento */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 sticky top-6">
          <h3 className="font-semibold text-gray-800 text-sm mb-3">Resumo</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-gray-600">
              <span>Serviço</span>
              <span>{fmt(valorServNum)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Produtos</span>
              <span>{fmt(valorProdutos)}</span>
            </div>
            <div className="flex items-center justify-between text-gray-600">
              <span>Desconto (R$)</span>
              <input type="number" min={0} step={0.01} value={desconto}
                onChange={e => setDesconto(e.target.value === '' ? '' : +e.target.value)}
                className="w-24 border rounded px-2 py-1 text-sm text-right" />
            </div>
            <div className="border-t pt-2 flex justify-between font-bold text-gray-900">
              <span>Total</span>
              <span>{fmt(total)}</span>
            </div>
          </div>

          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Forma de pagamento</label>
            <select value={formaPagamento} onChange={e => setFormaPagamento(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {formasPagamento.map(f => <option key={f}>{f}</option>)}
            </select>
          </div>

          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
            <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)} rows={2}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          <button onClick={criar}
            disabled={loading || !nomeCliente || !tipoServico || !descricaoServico}
            className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm disabled:opacity-50">
            {loading ? 'Criando...' : 'Criar Ordem de Serviço'}
          </button>
        </div>
      </div>

      {/* Modal: criar produto inline */}
      {modalProduto && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-1">Novo Produto</h2>
            <p className="text-xs text-gray-500 mb-4">Ao salvar, o produto entra no catálogo e é adicionado a esta OS.</p>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modalProduto.nome} autoFocus
                  onChange={e => setModalProduto(m => m && { ...m, nome: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Troca de tomada" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valor (R$) *</label>
                  <input type="number" min={0} step={0.01} value={modalProduto.valor}
                    onChange={e => setModalProduto(m => m && { ...m, valor: e.target.value === '' ? '' : +e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0,00" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unidade</label>
                  <input value={modalProduto.unidade}
                    onChange={e => setModalProduto(m => m && { ...m, unidade: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="un" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                <input value={modalProduto.descricao ?? ''}
                  onChange={e => setModalProduto(m => m && { ...m, descricao: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={() => setModalProduto(null)}
                className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={criarProdutoInline}
                disabled={!modalProduto.nome || modalProduto.valor === ''}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50">
                Salvar e adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Modal: Relatório do período ───────────────────────────────────────────────

function ModalRelatorio({ onClose }: { onClose: () => void }) {
  const hoje = new Date().toISOString().slice(0, 10)
  const trintaDiasAtras = new Date(Date.now() - 30 * 86400_000).toISOString().slice(0, 10)
  const [inicio, setInicio] = useState(trintaDiasAtras)
  const [fim, setFim] = useState(hoje)
  const [statusFiltro, setStatusFiltro] = useState('')
  const [baixando, setBaixando] = useState(false)

  const baixar = async () => {
    setBaixando(true)
    try {
      const params: Record<string, string> = {}
      if (inicio) params.inicio = inicio
      if (fim) params.fim = fim
      if (statusFiltro) params.status = statusFiltro
      const blob = await caixaApi.baixarRelatorioPdf(params)
      const partes = [inicio, fim].filter(Boolean).join('_')
      downloadBlob(blob, `relatorio-os${partes ? '-' + partes : ''}.pdf`)
      onClose()
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao gerar relatório')
    } finally {
      setBaixando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h2 className="font-semibold text-lg mb-1">Relatório do período</h2>
        <p className="text-xs text-gray-500 mb-4">PDF resumindo as ordens de serviço por intervalo e status.</p>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Início</label>
              <input type="date" value={inicio} onChange={e => setInicio(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fim</label>
              <input type="date" value={fim} onChange={e => setFim(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select value={statusFiltro} onChange={e => setStatusFiltro(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Todos</option>
              <option value="aberta">Aberta</option>
              <option value="concluida">Concluída</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button onClick={onClose} disabled={baixando}
            className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50">
            Cancelar
          </button>
          <button onClick={baixar} disabled={baixando}
            className="flex-1 flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50">
            <Download className="w-4 h-4" />
            {baixando ? 'Gerando...' : 'Baixar PDF'}
          </button>
        </div>
      </div>
    </div>
  )
}


// ── Aba: OS da sessão ─────────────────────────────────────────────────────────

function OrdensServico({ sessaoId }: { sessaoId: string }) {
  const [ordens, setOrdens] = useState<any[]>([])
  const [detalhe, setDetalhe] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [modalRelatorio, setModalRelatorio] = useState(false)

  const carregar = useCallback(() => {
    setLoading(true)
    caixaApi.listarOS({ sessao_id: sessaoId })
      .then(setOrdens)
      .finally(() => setLoading(false))
  }, [sessaoId])

  useEffect(() => { carregar() }, [carregar])

  const concluir = async (id: string) => {
    await caixaApi.concluirOS(id)
    carregar()
    if (detalhe?.id === id) setDetalhe((prev: any) => ({ ...prev, status: 'concluida' }))
  }

  const cancelar = async (id: string) => {
    if (!confirm('Cancelar esta OS?')) return
    await caixaApi.cancelarOS(id)
    carregar()
    if (detalhe?.id === id) setDetalhe(null)
  }

  const baixarPDF = async (os: any, e?: React.MouseEvent) => {
    e?.stopPropagation()
    try {
      const blob = await caixaApi.baixarPdfOS(os.id)
      downloadBlob(blob, `os-${os.numero}.pdf`)
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao gerar PDF')
    }
  }


  const statusBadge = (s: string) => {
    if (s === 'concluida') return <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Concluída</span>
    if (s === 'cancelada') return <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">Cancelada</span>
    return <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Aberta</span>
  }

  const totalSessao = ordens.filter(o => o.status === 'concluida').reduce((s, o) => s + o.total, 0)

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between gap-3">
          <h2 className="font-semibold text-gray-800">OS desta sessão</h2>
          <div className="flex items-center gap-3">
            <span className="text-sm text-green-600 font-medium">{fmt(totalSessao)} concluídas</span>
            <button onClick={() => setModalRelatorio(true)}
              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
              title="Relatório do período em PDF">
              <FileText className="w-3.5 h-3.5" /> Relatório
            </button>
          </div>
        </div>
        {loading && <p className="text-center py-8 text-gray-400 text-sm">Carregando...</p>}
        <div className="divide-y max-h-[500px] overflow-y-auto">
          {!loading && ordens.length === 0 && (
            <p className="text-center py-8 text-gray-400 text-sm">Nenhuma OS criada ainda</p>
          )}
          {ordens.map(os => (
            <div key={os.id}
              className={`flex items-center justify-between px-4 py-3 hover:bg-gray-50 cursor-pointer ${
                detalhe?.id === os.id ? 'bg-blue-50' : ''
              } ${os.status === 'cancelada' ? 'opacity-50' : ''}`}
              onClick={() => setDetalhe(os)}>
              <div>
                <p className="text-sm font-medium text-gray-800">{os.numero} — {os.nome_cliente}</p>
                <p className="text-xs text-gray-500">{os.tipo_servico} · {os.forma_pagamento}</p>
              </div>
              <div className="flex items-center gap-2">
                {statusBadge(os.status)}
                <span className="text-sm font-semibold text-gray-700">{fmt(os.total)}</span>
                <button onClick={(e) => baixarPDF(os, e)}
                  className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="Baixar PDF">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detalhe da OS */}
      {detalhe && (
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="font-semibold text-gray-800">{detalhe.numero}</h2>
              <p className="text-sm text-gray-500">{detalhe.nome_cliente}</p>
            </div>
            {statusBadge(detalhe.status)}
          </div>

          <div className="space-y-2 text-sm">
            <div><span className="text-gray-500">Tipo:</span> <span className="text-gray-800">{detalhe.tipo_servico}</span></div>
            <div><span className="text-gray-500">Descrição:</span> <span className="text-gray-800">{detalhe.descricao_servico}</span></div>
            {detalhe.observacoes && <div><span className="text-gray-500">Obs:</span> <span className="text-gray-800">{detalhe.observacoes}</span></div>}
          </div>

          {detalhe.itens?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-medium text-gray-500 mb-2">PRODUTOS</p>
              <div className="space-y-1">
                {detalhe.itens.map((i: any) => (
                  <div key={i.id} className="flex justify-between text-sm text-gray-700">
                    <span>{i.descricao} × {i.quantidade}</span>
                    <span>{fmt(i.valor_total)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="border-t mt-4 pt-3 space-y-1 text-sm">
            <div className="flex justify-between text-gray-600"><span>Serviço</span><span>{fmt(detalhe.valor_servico)}</span></div>
            <div className="flex justify-between text-gray-600"><span>Produtos</span><span>{fmt(detalhe.valor_produtos)}</span></div>
            {detalhe.desconto > 0 && <div className="flex justify-between text-gray-600"><span>Desconto</span><span>-{fmt(detalhe.desconto)}</span></div>}
            <div className="flex justify-between font-bold text-gray-900 pt-1 border-t"><span>Total</span><span>{fmt(detalhe.total)}</span></div>
          </div>

          <div className="flex gap-2 mt-4">
            <button onClick={() => baixarPDF(detalhe)}
              className="flex-1 flex items-center justify-center gap-1 border border-blue-200 text-blue-600 hover:bg-blue-50 py-2 rounded-lg text-sm">
              <Download className="w-4 h-4" /> PDF
            </button>
            {detalhe.status === 'aberta' && (
              <>
                <button onClick={() => cancelar(detalhe.id)}
                  className="flex-1 flex items-center justify-center gap-1 border border-red-200 text-red-600 hover:bg-red-50 py-2 rounded-lg text-sm">
                  <XCircle className="w-4 h-4" /> Cancelar
                </button>
                <button onClick={() => concluir(detalhe.id)}
                  className="flex-1 flex items-center justify-center gap-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-sm font-medium">
                  <CheckCircle className="w-4 h-4" /> Concluir
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {modalRelatorio && <ModalRelatorio onClose={() => setModalRelatorio(false)} />}
    </div>
  )
}

// ── Aba: Catálogo de Produtos ─────────────────────────────────────────────────

function CatalogoProdutos({ produtos, onAtualizar }: { produtos: Produto[]; onAtualizar: () => void }) {
  const [modal, setModal] = useState<any>(null)

  const salvar = async () => {
    try {
      if (modal.id) {
        await caixaApi.atualizarProduto(modal.id, { nome: modal.nome, descricao: modal.descricao, valor: modal.valor, unidade: modal.unidade })
      } else {
        await caixaApi.criarProduto({ nome: modal.nome, descricao: modal.descricao, valor: modal.valor, unidade: modal.unidade })
      }
      setModal(null)
      onAtualizar()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    }
  }

  const deletar = async (id: string) => {
    if (!confirm('Remover produto do catálogo?')) return
    await caixaApi.deletarProduto(id)
    onAtualizar()
  }

  const empty = { nome: '', descricao: '', valor: 0, unidade: 'un' }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800">Catálogo de Produtos do Caixa</h2>
        <button onClick={() => setModal(empty)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> Novo Produto
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Valor</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Unidade</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {produtos.length === 0 && (
              <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhum produto cadastrado</td></tr>
            )}
            {produtos.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-800 font-medium">{p.nome}</td>
                <td className="px-4 py-3 text-gray-500">{p.descricao || '—'}</td>
                <td className="px-4 py-3 text-gray-700">{fmt(p.valor)}</td>
                <td className="px-4 py-3 text-gray-600">{p.unidade}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => setModal({ ...p })} className="p-1 text-gray-400 hover:text-blue-600">
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button onClick={() => deletar(p.id)} className="p-1 text-gray-400 hover:text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-4">{modal.id ? 'Editar' : 'Novo'} Produto</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modal.nome} onChange={e => setModal((m: any) => ({ ...m, nome: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                <input value={modal.descricao || ''} onChange={e => setModal((m: any) => ({ ...m, descricao: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valor (R$) *</label>
                  <input type="number" min={0} step={0.01} value={modal.valor}
                    onChange={e => setModal((m: any) => ({ ...m, valor: +e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unidade</label>
                  <input value={modal.unidade} onChange={e => setModal((m: any) => ({ ...m, unidade: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModal(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} disabled={!modal.nome || modal.valor < 0}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Componente principal ──────────────────────────────────────────────────────

type Tab = 'nova-os' | 'ordens' | 'produtos'

export function Caixa() {
  const [sessao, setSessao] = useState<any>(null)
  const [loadingSessao, setLoadingSessao] = useState(true)
  const [saldoInicial, setSaldoInicial] = useState('')
  const [confirmandoFechamento, setConfirmandoFechamento] = useState(false)
  const [tab, setTab] = useState<Tab>('nova-os')
  const [produtos, setProdutos] = useState<Produto[]>([])

  const carregarSessao = () => {
    caixaApi.statusSessao().then(setSessao).catch(() => setSessao(null)).finally(() => setLoadingSessao(false))
  }

  const carregarProdutos = async () => {
    try {
      const lista = await caixaApi.listarProdutos()
      setProdutos(lista)
      return lista as Produto[]
    } catch {
      return [] as Produto[]
    }
  }

  useEffect(() => {
    carregarSessao()
    carregarProdutos()
  }, [])

  const abrirCaixa = async () => {
    if (!saldoInicial) return
    const s = await caixaApi.abrirSessao(+saldoInicial)
    setSessao(s)
    setSaldoInicial('')
  }

  const fecharCaixa = async () => {
    await caixaApi.fecharSessao()
    setConfirmandoFechamento(false)
    setSessao(null)
    setLoadingSessao(false)
  }

  if (loadingSessao) {
    return <div className="p-6 text-gray-400">Carregando...</div>
  }

  if (!sessao?.aberta) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 w-full max-w-sm text-center">
          <Power className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h2 className="font-semibold text-gray-800 text-lg mb-2">Caixa fechado</h2>
          <p className="text-gray-500 text-sm mb-6">Informe o saldo inicial para abrir o caixa</p>
          <input type="number" min={0} step={0.01} placeholder="Saldo inicial (R$)"
            value={saldoInicial} onChange={e => setSaldoInicial(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-center mb-4" />
          <button onClick={abrirCaixa} disabled={!saldoInicial}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg text-sm disabled:opacity-50">
            Abrir Caixa
          </button>
        </div>
      </div>
    )
  }

  const tabs: { id: Tab; label: string; icon: ReactNode }[] = [
    { id: 'nova-os', label: 'Nova OS', icon: <Plus className="w-4 h-4" /> },
    { id: 'ordens', label: 'OS do Dia', icon: <ClipboardList className="w-4 h-4" /> },
    { id: 'produtos', label: 'Produtos', icon: <Package className="w-4 h-4" /> },
  ]

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Caixa</h1>
          <p className="text-sm text-green-600 font-medium mt-0.5">Caixa aberto</p>
        </div>
        <button onClick={() => setConfirmandoFechamento(true)}
          className="flex items-center gap-2 border border-red-200 text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg text-sm font-medium">
          <Power className="w-4 h-4" /> Fechar Caixa
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.id
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Conteúdo */}
      {tab === 'nova-os' && (
        <NovaOSForm sessaoId={sessao.id} produtos={produtos} onCriada={() => setTab('ordens')}
          onProdutosChange={carregarProdutos} />
      )}
      {tab === 'ordens' && (
        <OrdensServico sessaoId={sessao.id} />
      )}
      {tab === 'produtos' && (
        <CatalogoProdutos produtos={produtos} onAtualizar={carregarProdutos} />
      )}

      {/* Modal fechar caixa */}
      {confirmandoFechamento && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-2">Fechar Caixa</h2>
            <p className="text-sm text-gray-600 mb-4">
              O saldo final será calculado com base nas OS concluídas. Deseja fechar o caixa agora?
            </p>
            <div className="flex gap-2">
              <button onClick={() => setConfirmandoFechamento(false)}
                className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={fecharCaixa}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg text-sm font-medium">
                Fechar Caixa
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
