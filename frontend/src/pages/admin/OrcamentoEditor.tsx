import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Plus, Trash2, Calculator, ArrowLeft, ChevronDown } from 'lucide-react'
import { orcamentosApi, premissasApi } from '../../api/quotes'
import { clientesApi } from '../../api/clients'
import { operadoresApi } from '../../api/operators'

const fmt = (v: number) =>
  `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

// ── Tipos ─────────────────────────────────────────────────────────────────────

interface PremissaTemplate {
  id: string
  nome: string
  descricao?: string
  tipo: 'percentual' | 'fixo'
  valor: number
  ordem: number
}

interface PremissaAplicada {
  _key: string           // id local
  premissa_id?: string   // referência ao template
  nome: string
  descricao?: string
  tipo: 'percentual' | 'fixo'
  valor: number
  ordem: number
}

interface ItemOrcamento {
  _key: string
  tipo: 'manual' | 'produto'
  descricao: string
  item_estoque_id?: string
  quantidade?: number
  valor_unitario?: number
  ordem: number
}

interface Calculado {
  custo_base: number
  subtotal_premissas: number
  subtotal_itens: number
  subtotal: number
  valor_venda: number
  premissas: { nome: string; tipo: string; valor: number; valor_calculado: number }[]
  itens: { descricao: string; valor_calculado: number }[]
}

// ── Componente ────────────────────────────────────────────────────────────────

export function OrcamentoEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isNew = !id

  // Dados do orçamento
  const [titulo, setTitulo] = useState('')
  const [custoBase, setCustoBase] = useState<number | ''>('')
  const [valorVendaManual, setValorVendaManual] = useState<number | ''>('')
  const [clienteId, setClienteId] = useState('')
  const [observacoes, setObservacoes] = useState('')

  // Premissas aplicadas e itens
  const [premissasAplicadas, setPremissasAplicadas] = useState<PremissaAplicada[]>([])
  const [itens, setItens] = useState<ItemOrcamento[]>([])

  // Resultado do cálculo
  const [calculado, setCalculado] = useState<Calculado | null>(null)
  const [pvFormula, setPvFormula] = useState<number | null>(null)  // PV sem override

  // Dados extras
  const [vendedorId, setVendedorId] = useState('')
  const [validadeDias, setValidadeDias] = useState(30)

  // Dados externos
  const [templates, setTemplates] = useState<PremissaTemplate[]>([])
  const [clientes, setClientes] = useState<any[]>([])
  const [vendedores, setVendedores] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  // ── Inicialização ───────────────────────────────────────────────────────────

  useEffect(() => {
    premissasApi.listar().then(setTemplates).catch(() => {})
    clientesApi.listar().then(setClientes).catch(() => {})
    operadoresApi.listar().then((ops: any[]) =>
      setVendedores(ops.filter(o => o.perfil?.toLowerCase() === 'vendedor' && o.ativo))
    ).catch(() => {})
  }, [])

  useEffect(() => {
    if (!id) return
    orcamentosApi.obter(id).then((orc: any) => {
      setTitulo(orc.titulo)
      setCustoBase(orc.custo_base)
      // Não pré-populamos o campo manual — deixamos a fórmula recalcular
      setClienteId(orc.cliente_id || '')
      setVendedorId(orc.vendedor_id || '')
      setValidadeDias(orc.validade_dias || 30)
      setObservacoes(orc.observacoes || '')
      setPremissasAplicadas((orc.premissas || []).map((p: any) => ({
        _key: crypto.randomUUID(),
        premissa_id: p.premissa_id,
        nome: p.nome,
        descricao: p.descricao,
        tipo: p.tipo,
        valor: p.valor,
        ordem: p.ordem,
      })))
      setItens((orc.itens || []).map((i: any) => ({
        _key: crypto.randomUUID(),
        tipo: i.tipo,
        descricao: i.descricao,
        item_estoque_id: i.item_estoque_id,
        quantidade: i.quantidade,
        valor_unitario: i.valor_unitario,
        ordem: i.ordem,
      })))
    }).catch(() => {})
  }, [id])

  // ── Cálculo automático ──────────────────────────────────────────────────────

  const recalcular = useCallback(async () => {
    const base = Number(custoBase)
    if (!base || base <= 0) { setCalculado(null); setPvFormula(null); return }

    const payload = {
      custo_base: base,
      premissas: premissasAplicadas.map((p, idx) => ({
        premissa_id: p.premissa_id || undefined,
        nome: p.nome, descricao: p.descricao,
        tipo: p.tipo, valor: p.valor, ordem: idx,
      })),
      itens: itens.map((i, idx) => ({
        tipo: i.tipo, descricao: i.descricao,
        item_estoque_id: i.item_estoque_id || undefined,
        quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: idx,
      })),
    }

    try {
      // Sempre calcular o PV pela fórmula (sem override)
      const formulaResult = await orcamentosApi.calcular(payload)
      setPvFormula(formulaResult.valor_venda)

      // Se há override manual, recalcular com ele para mostrar os valores ajustados
      if (valorVendaManual && Number(valorVendaManual) > 0) {
        const overrideResult = await orcamentosApi.calcular({
          ...payload,
          valor_venda: Number(valorVendaManual),
        })
        setCalculado(overrideResult)
      } else {
        setCalculado(formulaResult)
      }
    } catch {}
  }, [custoBase, valorVendaManual, premissasAplicadas, itens])

  useEffect(() => {
    const t = setTimeout(recalcular, 400)
    return () => clearTimeout(t)
  }, [recalcular])

  // ── Gerenciar premissas ─────────────────────────────────────────────────────

  // IDs de templates já usados no orçamento
  const premissasIdsUsados = new Set(
    premissasAplicadas.filter(p => p.premissa_id).map(p => p.premissa_id!)
  )

  const adicionarPremissa = (template?: PremissaTemplate) => {
    if (template) {
      // Bloquear duplicata
      if (premissasIdsUsados.has(template.id)) {
        alert('Esta premissa já foi adicionada ao orçamento.')
        return
      }
      setPremissasAplicadas(prev => [...prev, {
        _key: crypto.randomUUID(),
        premissa_id: template.id,
        nome: template.nome,
        descricao: template.descricao,
        tipo: template.tipo,
        valor: template.valor,
        ordem: prev.length,
      }])
      return
    }
    // Premissa customizada (sem template)
    setPremissasAplicadas(prev => [...prev, {
      _key: crypto.randomUUID(),
      nome: 'Nova premissa',
      tipo: 'percentual',
      valor: 0,
      ordem: prev.length,
    }])
  }

  const atualizarPremissa = (key: string, changes: Partial<PremissaAplicada>) => {
    setPremissasAplicadas(prev => prev.map(p => p._key === key ? { ...p, ...changes } : p))
  }

  const removerPremissa = (key: string) => {
    setPremissasAplicadas(prev => prev.filter(p => p._key !== key))
  }

  const trocarTemplate = (key: string, templateId: string) => {
    const t = templates.find(t => t.id === templateId)
    if (!t) return
    atualizarPremissa(key, {
      premissa_id: t.id,
      nome: t.nome,
      descricao: t.descricao,
      tipo: t.tipo,
      valor: t.valor,
    })
  }

  // ── Gerenciar itens ─────────────────────────────────────────────────────────

  const adicionarItem = (tipo: 'manual' | 'produto') => {
    setItens(prev => [...prev, {
      _key: crypto.randomUUID(),
      tipo,
      descricao: tipo === 'manual' ? 'Custo adicional' : 'Produto',
      quantidade: tipo === 'produto' ? 1 : undefined,
      valor_unitario: 0,
      ordem: prev.length,
    }])
  }

  const atualizarItem = (key: string, changes: Partial<ItemOrcamento>) => {
    setItens(prev => prev.map(i => i._key === key ? { ...i, ...changes } : i))
  }

  const removerItem = (key: string) => setItens(prev => prev.filter(i => i._key !== key))

  // ── Salvar ──────────────────────────────────────────────────────────────────

  const handleSalvar = async () => {
    if (!titulo || !Number(custoBase)) return
    setLoading(true)
    try {
      const payload = {
        titulo,
        custo_base: Number(custoBase),
        valor_venda: valorVendaManual ? Number(valorVendaManual) : undefined,
        cliente_id: clienteId || undefined,
        vendedor_id: vendedorId || undefined,
        validade_dias: validadeDias,
        observacoes: observacoes || undefined,
        premissas: premissasAplicadas.map((p, idx) => ({
          premissa_id: p.premissa_id || undefined,
          nome: p.nome,
          descricao: p.descricao,
          tipo: p.tipo,
          valor: p.valor,
          ordem: idx,
        })),
        itens: itens.map((i, idx) => ({
          tipo: i.tipo,
          descricao: i.descricao,
          item_estoque_id: i.item_estoque_id || undefined,
          quantidade: i.quantidade,
          valor_unitario: i.valor_unitario,
          ordem: idx,
        })),
      }
      if (isNew) {
        await orcamentosApi.criar(payload)
      } else {
        await orcamentosApi.atualizar(id!, payload)
      }
      navigate('/orcamentos')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    } finally {
      setLoading(false)
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  const base = Number(custoBase) || 0

  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/orcamentos')} className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          {isNew ? 'Novo Orçamento' : 'Editar Orçamento'}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Coluna principal */}
        <div className="lg:col-span-2 space-y-4">

          {/* Dados básicos */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h2 className="font-semibold text-gray-800 mb-4">Dados do Orçamento</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Título *</label>
                <input value={titulo} onChange={e => setTitulo(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Instalação elétrica residencial" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Custo Base (R$) *</label>
                  <input type="number" value={custoBase} onChange={e => setCustoBase(e.target.value === '' ? '' : +e.target.value)}
                    min={0} step={0.01} placeholder="0,00"
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center justify-between">
                    <span>
                      Valor de Venda (R$)
                      {valorVendaManual
                        ? <span className="ml-2 text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-normal">manual</span>
                        : <span className="ml-2 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-normal">auto</span>
                      }
                    </span>
                    {pvFormula && <span className="text-xs text-gray-400 font-normal">fórmula: {fmt(pvFormula)}</span>}
                  </label>
                  <div className="flex gap-2">
                    <input type="number" value={valorVendaManual}
                      onChange={e => setValorVendaManual(e.target.value === '' ? '' : +e.target.value)}
                      min={0} step={0.01}
                      placeholder={pvFormula ? fmt(pvFormula) : 'Calculado pela fórmula'}
                      className={`flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 ${
                        valorVendaManual ? 'border-amber-300 focus:ring-amber-400' : 'focus:ring-blue-500'
                      }`} />
                    {valorVendaManual && (
                      <button onClick={() => setValorVendaManual('')}
                        className="text-xs px-2 py-1 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-500 whitespace-nowrap">
                        Usar fórmula
                      </button>
                    )}
                  </div>
                  {valorVendaManual && pvFormula && Number(valorVendaManual) < pvFormula && (
                    <p className="text-xs text-amber-600 mt-1">
                      ⚠ PV manual ({fmt(Number(valorVendaManual))}) está abaixo do PV da fórmula ({fmt(pvFormula)})
                    </p>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
                  <select value={clienteId} onChange={e => setClienteId(e.target.value)}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">Sem cliente</option>
                    {clientes.map((c: any) => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Vendedor</label>
                  <select value={vendedorId} onChange={e => setVendedorId(e.target.value)}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">Sem vendedor</option>
                    {vendedores.map((v: any) => <option key={v.id} value={v.id}>{v.nome}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Validade (dias)</label>
                <input type="number" value={validadeDias} min={1}
                  onChange={e => setValidadeDias(+e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
                <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)} rows={2}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
          </div>

          {/* Premissas */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-gray-800">Premissas</h2>
                <p className="text-xs text-gray-400 mt-0.5">Percentuais calculados sobre o preço de venda (markup)</p>
              </div>
              <div className="flex gap-2">
                {templates.length > 0 && (
                  <div className="relative group">
                    <button className="text-xs bg-purple-50 text-purple-700 px-3 py-1.5 rounded-lg hover:bg-purple-100 flex items-center gap-1">
                      <Plus className="w-3 h-3" /> Da lista <ChevronDown className="w-3 h-3" />
                    </button>
                    <div className="absolute right-0 top-full mt-1 w-52 bg-white border border-gray-200 rounded-lg shadow-lg z-10 hidden group-hover:block">
                      {templates.map(t => {
                        const usado = premissasIdsUsados.has(t.id)
                        return (
                          <button key={t.id} onClick={() => adicionarPremissa(t)}
                            disabled={usado}
                            className={`w-full text-left px-3 py-2 text-sm flex justify-between items-center ${
                              usado ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50'
                            }`}>
                            <span>{t.nome}</span>
                            <span className="text-gray-400 text-xs">
                              {usado ? '✓' : `${t.valor}${t.tipo === 'percentual' ? '%' : ' R$'}`}
                            </span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
                <button onClick={() => adicionarPremissa(undefined)}
                  className="text-xs bg-gray-50 text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-100 flex items-center gap-1">
                  <Plus className="w-3 h-3" /> Personalizada
                </button>
              </div>
            </div>

            <div className="space-y-2">
              {premissasAplicadas.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-6">
                  Nenhuma premissa adicionada. Use os botões acima para adicionar.
                </p>
              )}
              {premissasAplicadas.map((p, idx) => {
                const calc = calculado?.premissas?.[idx]
                return (
                  <div key={p._key} className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg border border-purple-100">
                    <div className="flex-1 grid grid-cols-3 gap-2">
                      {/* Nome / template */}
                      {p.premissa_id ? (
                        <select value={p.premissa_id}
                          onChange={e => trocarTemplate(p._key, e.target.value)}
                          className="bg-white border border-purple-200 rounded px-2 py-1.5 text-sm col-span-1">
                          {templates.map(t => <option key={t.id} value={t.id}>{t.nome}</option>)}
                        </select>
                      ) : (
                        <input value={p.nome}
                          onChange={e => atualizarPremissa(p._key, { nome: e.target.value })}
                          className="bg-white border border-purple-200 rounded px-2 py-1.5 text-sm col-span-1"
                          placeholder="Nome" />
                      )}
                      {/* Tipo */}
                      <select value={p.tipo}
                        onChange={e => atualizarPremissa(p._key, { tipo: e.target.value as 'percentual' | 'fixo' })}
                        className="bg-white border border-purple-200 rounded px-2 py-1.5 text-sm">
                        <option value="percentual">Percentual (%)</option>
                        <option value="fixo">Fixo (R$)</option>
                      </select>
                      {/* Valor */}
                      <div className="flex items-center gap-1">
                        <input type="number" value={p.valor}
                          onChange={e => atualizarPremissa(p._key, { valor: +e.target.value })}
                          min={0} step={0.01}
                          className="flex-1 bg-white border border-purple-200 rounded px-2 py-1.5 text-sm" />
                        <span className="text-xs text-purple-500 w-4">{p.tipo === 'percentual' ? '%' : 'R$'}</span>
                      </div>
                    </div>
                    {/* Valor calculado */}
                    <div className="text-sm font-semibold text-purple-700 w-28 text-right">
                      {calc ? fmt(calc.valor_calculado) : '—'}
                    </div>
                    <button onClick={() => removerPremissa(p._key)} className="text-purple-300 hover:text-red-500">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Itens adicionais */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-gray-800">Itens Adicionais</h2>
                <p className="text-xs text-gray-400 mt-0.5">Produtos e custos avulsos não cobertos pelas premissas</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => adicionarItem('manual')}
                  className="text-xs bg-orange-50 text-orange-700 px-3 py-1.5 rounded-lg hover:bg-orange-100 flex items-center gap-1">
                  <Plus className="w-3 h-3" /> Manual
                </button>
                <button onClick={() => adicionarItem('produto')}
                  className="text-xs bg-green-50 text-green-700 px-3 py-1.5 rounded-lg hover:bg-green-100 flex items-center gap-1">
                  <Plus className="w-3 h-3" /> Produto
                </button>
              </div>
            </div>

            <div className="space-y-2">
              {itens.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-6">
                  Nenhum item adicional.
                </p>
              )}
              {itens.map((item, idx) => {
                const calc = calculado?.itens?.[idx]
                return (
                  <div key={item._key} className={`flex items-center gap-2 p-3 rounded-lg border ${
                    item.tipo === 'manual'
                      ? 'bg-orange-50 border-orange-100'
                      : 'bg-green-50 border-green-100'
                  }`}>
                    <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${
                      item.tipo === 'manual' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
                    }`}>{item.tipo}</span>

                    <input value={item.descricao}
                      onChange={e => atualizarItem(item._key, { descricao: e.target.value })}
                      className="flex-1 bg-white border rounded px-2 py-1.5 text-sm"
                      placeholder="Descrição" />

                    {item.tipo === 'produto' && (
                      <>
                        <input type="number" value={item.quantidade ?? 1}
                          onChange={e => atualizarItem(item._key, { quantidade: +e.target.value })}
                          min={0.001} step={0.001}
                          className="w-20 bg-white border rounded px-2 py-1.5 text-sm"
                          placeholder="Qtd" />
                        <span className="text-xs text-gray-400">×</span>
                      </>
                    )}

                    <input type="number" value={item.valor_unitario ?? 0}
                      onChange={e => atualizarItem(item._key, { valor_unitario: +e.target.value })}
                      min={0} step={0.01}
                      className="w-28 bg-white border rounded px-2 py-1.5 text-sm"
                      placeholder="R$ unit." />

                    <div className={`text-sm font-semibold w-28 text-right ${
                      item.tipo === 'manual' ? 'text-orange-700' : 'text-green-700'
                    }`}>
                      {calc ? fmt(calc.valor_calculado) : '—'}
                    </div>

                    <button onClick={() => removerItem(item._key)} className="text-gray-300 hover:text-red-500">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Resumo lateral */}
        <div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 sticky top-6">
            <div className="flex items-center gap-2 mb-4">
              <Calculator className="w-4 h-4 text-blue-600" />
              <h2 className="font-semibold text-gray-800">Resumo</h2>
            </div>

            <div className="space-y-1.5 text-sm">
              <div className="flex justify-between text-gray-700 font-medium pb-1 border-b">
                <span>Custo base</span>
                <span>{fmt(base)}</span>
              </div>

              {/* Premissas */}
              {(calculado?.premissas?.length ?? 0) > 0 && (
                <>
                  {calculado!.premissas.map((p, i) => (
                    <div key={i} className="flex justify-between text-purple-600">
                      <span className="truncate mr-2 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block" />
                        {p.nome}
                        <span className="text-purple-300 text-xs">
                          {p.tipo === 'percentual' ? `${p.valor}%` : ''}
                        </span>
                      </span>
                      <span className="flex-shrink-0 font-medium">+{fmt(p.valor_calculado)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between text-purple-700 text-xs pt-0.5 pb-1">
                    <span>Subtotal premissas</span>
                    <span>{fmt(calculado?.subtotal_premissas ?? 0)}</span>
                  </div>
                </>
              )}

              {/* Itens */}
              {(calculado?.itens?.length ?? 0) > 0 && (
                <>
                  {calculado!.itens.map((it, i) => (
                    <div key={i} className="flex justify-between text-gray-500">
                      <span className="truncate mr-2 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-gray-300 inline-block" />
                        {it.descricao}
                      </span>
                      <span className="flex-shrink-0">+{fmt(it.valor_calculado)}</span>
                    </div>
                  ))}
                </>
              )}

              <div className="border-t pt-2 mt-1 flex justify-between font-semibold text-gray-800">
                <span>Subtotal</span>
                <span>{fmt(calculado?.subtotal ?? base)}</span>
              </div>

              <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mt-2">
                <div className="flex justify-between font-bold text-blue-700 text-base">
                  <span>Valor de Venda</span>
                  <span>{fmt(calculado?.valor_venda ?? base)}</span>
                </div>
                {calculado && calculado.valor_venda > 0 && calculado.custo_base > 0 && (
                  <div className="text-xs text-blue-500 mt-1 text-right">
                    Margem: {(((calculado.valor_venda - calculado.custo_base) / calculado.valor_venda) * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={handleSalvar}
              disabled={loading || !titulo || !Number(custoBase)}
              className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {loading ? 'Salvando...' : isNew ? 'Criar Orçamento' : 'Salvar Alterações'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
