import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Plus, Trash2, Calculator, ArrowLeft, ChevronDown } from 'lucide-react'
import { orcamentosApi, premissasApi } from '../../api/quotes'
import { clientesApi } from '../../api/clients'
import { operadoresApi } from '../../api/operators'
import { variaveisApi } from '../../api/settings'

const fmt = (v: number) =>
  `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

// ── Tabela de composição ──────────────────────────────────────────────────────

interface LinhaComposicao {
  nome: string
  qtd: number | null
  valor: number
  secao: 'base' | 'item' | 'premissa' | 'total'
  badge?: 'manual' | 'produto' | null
}

function TabelaComposicao({ linhas, valorVenda }: { linhas: LinhaComposicao[]; valorVenda: number }) {
  const pct = (v: number) =>
    valorVenda > 0 ? `${((v / valorVenda) * 100).toFixed(2)}%` : '—'

  return (
    <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
      <div className="px-5 py-3 border-b border-zinc-100 flex items-center justify-between">
        <span className="text-sm font-semibold text-zinc-800">Composição do Preço</span>
        <span className="text-xs text-zinc-400">% sobre o valor de venda</span>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #E4E4E7', background: '#FAFAFA' }}>
            <th style={{ padding: '8px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em' }}>ITEM</th>
            <th style={{ padding: '8px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 60 }}>QTD</th>
            <th style={{ padding: '8px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 150 }}>VALORES</th>
            <th style={{ padding: '8px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 90 }}>% DO TOTAL</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((row, i) => {
            const isTotal = row.secao === 'total'
            const isDivider = row.secao === 'premissa' && linhas[i - 1]?.secao !== 'premissa'
            return (
              <>
                {isDivider && (
                  <tr key={`div-${i}`} style={{ borderTop: '1px solid #E4E4E7', borderBottom: '1px solid #E4E4E7', background: '#FAFAFA' }}>
                    <td colSpan={4} style={{ padding: '3px 16px', fontSize: '10px', fontWeight: 700, color: '#A1A1AA', letterSpacing: '0.08em' }}>
                      PREMISSAS
                    </td>
                  </tr>
                )}
                <tr key={i} style={{
                  borderBottom: isTotal ? 'none' : '1px solid #F4F4F5',
                  borderTop: isTotal ? '2px solid #E4E4E7' : 'none',
                  background: isTotal ? '#FAFAFA' : 'white',
                }}>
                  <td style={{ padding: '9px 16px', fontSize: '13px', color: isTotal ? '#18181B' : '#3F3F46', fontWeight: isTotal ? 700 : 400 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {row.badge && (
                        <span style={{
                          fontSize: 10, fontWeight: 600, padding: '1px 5px', borderRadius: 3,
                          background: row.badge === 'manual' ? '#FEF3C7' : '#DCFCE7',
                          color: row.badge === 'manual' ? '#D97706' : '#16A34A',
                        }}>
                          {row.badge === 'manual' ? 'M' : 'P'}
                        </span>
                      )}
                      <span style={{ textTransform: row.secao === 'total' ? 'none' : 'uppercase', letterSpacing: row.secao === 'total' ? 'normal' : '0.02em' }}>
                        {row.nome}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'center', fontSize: '13px', color: '#A1A1AA', fontVariantNumeric: 'tabular-nums' }}>
                    {row.qtd ?? '—'}
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'right', fontSize: '13px', color: isTotal ? '#2563EB' : '#18181B', fontWeight: isTotal ? 700 : 400, fontVariantNumeric: 'tabular-nums' }}>
                    {fmt(row.valor)}
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'right', fontSize: '13px', color: isTotal ? '#2563EB' : '#71717A', fontWeight: isTotal ? 700 : 400, fontVariantNumeric: 'tabular-nums' }}>
                    {isTotal ? '100,00%' : pct(row.valor)}
                  </td>
                </tr>
              </>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

interface PremissaTemplate {
  id: string; nome: string; descricao?: string
  tipo: 'percentual' | 'fixo'; valor: number; ordem: number
}

interface PremissaAplicada {
  _key: string; premissa_id?: string; nome: string; descricao?: string
  tipo: 'percentual' | 'fixo'; valor: number; ordem: number
}

interface ItemOrcamento {
  _key: string; tipo: 'manual' | 'produto'; descricao: string
  item_estoque_id?: string; quantidade?: number; valor_unitario?: number; ordem: number
}

interface Calculado {
  custo_base: number; subtotal_premissas: number; subtotal_itens: number
  subtotal: number; valor_venda: number
  premissas: { nome: string; tipo: string; valor: number; valor_calculado: number }[]
  itens: { descricao: string; valor_calculado: number }[]
}

export function OrcamentoEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isNew = !id

  const [titulo, setTitulo] = useState('')
  const [custoBase, setCustoBase] = useState<number | ''>('')
  const [valorVendaManual, setValorVendaManual] = useState<number | ''>('')
  const [clienteId, setClienteId] = useState('')
  const [observacoes, setObservacoes] = useState('')
  const [premissasAplicadas, setPremissasAplicadas] = useState<PremissaAplicada[]>([])
  const [itens, setItens] = useState<ItemOrcamento[]>([])
  const [calculado, setCalculado] = useState<Calculado | null>(null)
  const [pvFormula, setPvFormula] = useState<number | null>(null)
  const [vendedorId, setVendedorId] = useState('')
  const [validadeDias, setValidadeDias] = useState(30)

  // Campos extras da proposta (variáveis do template DOCX)
  const [camposExtras, setCamposExtras] = useState<Record<string, string>>({})
  const [variaveisCustom, setVariaveisCustom] = useState<{ id: string; chave: string; label: string; grupo: string }[]>([])

  const [templates, setTemplates] = useState<PremissaTemplate[]>([])
  const [clientes, setClientes] = useState<any[]>([])
  const [vendedores, setVendedores] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    premissasApi.listar().then(setTemplates).catch(() => {})
    clientesApi.listar().then(setClientes).catch(() => {})
    operadoresApi.listar().then((ops: any[]) =>
      setVendedores(ops.filter(o => o.perfil?.toLowerCase() === 'vendedor' && o.ativo))
    ).catch(() => {})
    variaveisApi.listar().then(d => setVariaveisCustom(d.personalizadas)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!id) return
    orcamentosApi.obter(id).then((orc: any) => {
      setTitulo(orc.titulo)
      setCustoBase(orc.custo_base)
      setClienteId(orc.cliente_id || '')
      setVendedorId(orc.vendedor_id || '')
      setValidadeDias(orc.validade_dias || 30)
      setObservacoes(orc.observacoes || '')
      setCamposExtras(orc.campos_extras || {})
      setPremissasAplicadas((orc.premissas || []).map((p: any) => ({
        _key: crypto.randomUUID(),
        premissa_id: p.premissa_id, nome: p.nome, descricao: p.descricao,
        tipo: p.tipo, valor: p.valor, ordem: p.ordem,
      })))
      setItens((orc.itens || []).map((i: any) => ({
        _key: crypto.randomUUID(),
        tipo: i.tipo, descricao: i.descricao, item_estoque_id: i.item_estoque_id,
        quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: i.ordem,
      })))
    }).catch(() => {})
  }, [id])

  const recalcular = useCallback(async () => {
    const base = Number(custoBase)
    if (!base || base <= 0) { setCalculado(null); setPvFormula(null); return }
    const payload = {
      custo_base: base,
      premissas: premissasAplicadas.map((p, idx) => ({
        premissa_id: p.premissa_id || undefined, nome: p.nome, descricao: p.descricao,
        tipo: p.tipo, valor: p.valor, ordem: idx,
      })),
      itens: itens.map((i, idx) => ({
        tipo: i.tipo, descricao: i.descricao, item_estoque_id: i.item_estoque_id || undefined,
        quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: idx,
      })),
    }
    try {
      const formulaResult = await orcamentosApi.calcular(payload)
      setPvFormula(formulaResult.valor_venda)
      if (valorVendaManual && Number(valorVendaManual) > 0) {
        const overrideResult = await orcamentosApi.calcular({ ...payload, valor_venda: Number(valorVendaManual) })
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

  const premissasIdsUsados = new Set(
    premissasAplicadas.filter(p => p.premissa_id).map(p => p.premissa_id!)
  )

  const adicionarPremissa = (template?: PremissaTemplate) => {
    if (template) {
      if (premissasIdsUsados.has(template.id)) { alert('Esta premissa já foi adicionada.'); return }
      setPremissasAplicadas(prev => [...prev, {
        _key: crypto.randomUUID(), premissa_id: template.id, nome: template.nome,
        descricao: template.descricao, tipo: template.tipo, valor: template.valor, ordem: prev.length,
      }])
      return
    }
    setPremissasAplicadas(prev => [...prev, {
      _key: crypto.randomUUID(), nome: 'Nova premissa', tipo: 'percentual', valor: 0, ordem: prev.length,
    }])
  }

  const atualizarPremissa = (key: string, changes: Partial<PremissaAplicada>) =>
    setPremissasAplicadas(prev => prev.map(p => p._key === key ? { ...p, ...changes } : p))

  const removerPremissa = (key: string) =>
    setPremissasAplicadas(prev => prev.filter(p => p._key !== key))

  const trocarTemplate = (key: string, templateId: string) => {
    const t = templates.find(t => t.id === templateId)
    if (!t) return
    atualizarPremissa(key, { premissa_id: t.id, nome: t.nome, descricao: t.descricao, tipo: t.tipo, valor: t.valor })
  }

  const adicionarItem = (tipo: 'manual' | 'produto') =>
    setItens(prev => [...prev, {
      _key: crypto.randomUUID(), tipo, descricao: tipo === 'manual' ? 'Custo adicional' : 'Produto',
      quantidade: tipo === 'produto' ? 1 : undefined, valor_unitario: 0, ordem: prev.length,
    }])

  const atualizarItem = (key: string, changes: Partial<ItemOrcamento>) =>
    setItens(prev => prev.map(i => i._key === key ? { ...i, ...changes } : i))

  const removerItem = (key: string) => setItens(prev => prev.filter(i => i._key !== key))

  const handleSalvar = async () => {
    if (!titulo || !Number(custoBase)) return
    setLoading(true)
    try {
      const payload = {
        titulo, custo_base: Number(custoBase),
        valor_venda: valorVendaManual ? Number(valorVendaManual) : undefined,
        cliente_id: clienteId || undefined,
        vendedor_id: vendedorId || undefined,
        validade_dias: validadeDias,
        observacoes: observacoes || undefined,
        campos_extras: camposExtras,
        premissas: premissasAplicadas.map((p, idx) => ({
          premissa_id: p.premissa_id || undefined, nome: p.nome, descricao: p.descricao,
          tipo: p.tipo, valor: p.valor, ordem: idx,
        })),
        itens: itens.map((i, idx) => ({
          tipo: i.tipo, descricao: i.descricao, item_estoque_id: i.item_estoque_id || undefined,
          quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: idx,
        })),
      }
      if (isNew) { await orcamentosApi.criar(payload) } else { await orcamentosApi.atualizar(id!, payload) }
      navigate('/orcamentos')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    } finally {
      setLoading(false)
    }
  }

  const base = Number(custoBase) || 0

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/orcamentos')}
          className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{isNew ? 'Nova Proposta Comercial' : 'Editar Proposta'}</h1>
          <p className="text-sm text-gray-500 mt-0.5">Preencha os dados, premissas e itens do orçamento</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Coluna principal */}
        <div className="lg:col-span-2 space-y-5">

          {/* Dados básicos */}
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Dados do Orçamento</span>
            </div>
            <div className="panel-body space-y-3">
              <div>
                <label className="form-label">Título *</label>
                <input value={titulo} onChange={e => setTitulo(e.target.value)}
                  className="form-input" placeholder="Ex: Instalação elétrica residencial" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Custo Base (R$) *</label>
                  <input type="number" value={custoBase}
                    onChange={e => setCustoBase(e.target.value === '' ? '' : +e.target.value)}
                    min={0} step={0.01} placeholder="0,00" className="form-input" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="form-label mb-0">
                      Valor de Venda (R$)
                      <span className={`ml-2 text-xs px-1.5 py-0.5 rounded font-normal ${
                        valorVendaManual
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-green-100 text-green-700'
                      }`}>
                        {valorVendaManual ? 'manual' : 'auto'}
                      </span>
                    </label>
                    {pvFormula && (
                      <span className="text-xs text-gray-400">fórmula: {fmt(pvFormula)}</span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <input type="number" value={valorVendaManual}
                      onChange={e => setValorVendaManual(e.target.value === '' ? '' : +e.target.value)}
                      min={0} step={0.01}
                      placeholder={pvFormula ? fmt(pvFormula) : 'Calculado'}
                      className={`form-input flex-1 ${valorVendaManual ? 'border-yellow-300' : ''}`} />
                    {valorVendaManual && (
                      <button onClick={() => setValorVendaManual('')} className="btn-secondary text-xs whitespace-nowrap">
                        Usar fórmula
                      </button>
                    )}
                  </div>
                  {valorVendaManual && pvFormula && Number(valorVendaManual) < pvFormula && (
                    <p className="text-xs text-yellow-600 mt-1">
                      PV manual abaixo do calculado pela fórmula ({fmt(pvFormula)})
                    </p>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Cliente</label>
                  <select value={clienteId} onChange={e => setClienteId(e.target.value)} className="form-input">
                    <option value="">Sem cliente</option>
                    {clientes.map((c: any) => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                </div>
                <div>
                  <label className="form-label">Vendedor</label>
                  <select value={vendedorId} onChange={e => setVendedorId(e.target.value)} className="form-input">
                    <option value="">Sem vendedor</option>
                    {vendedores.map((v: any) => <option key={v.id} value={v.id}>{v.nome}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Validade (dias)</label>
                  <input type="number" value={validadeDias} min={1}
                    onChange={e => setValidadeDias(+e.target.value)} className="form-input" />
                </div>
                <div>
                  <label className="form-label">Observações</label>
                  <input value={observacoes} onChange={e => setObservacoes(e.target.value)} className="form-input" />
                </div>
              </div>
            </div>
          </div>

          {/* Dados da Proposta / Variáveis do Template DOCX */}
          {(() => {
            const setCE = (k: string, v: string) => setCamposExtras(prev => ({ ...prev, [k]: v }))
            const ce = (k: string) => camposExtras[k] ?? ''
            const field = (k: string, label: string, unit?: string, type = 'text') => (
              <div key={k}>
                <label className="block text-xs font-medium text-gray-600 mb-1">{label}{unit && <span className="text-gray-400 ml-1">({unit})</span>}</label>
                <input type={type} value={ce(k)} onChange={e => setCE(k, e.target.value)}
                  className="w-full border rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              </div>
            )
            return (
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <h2 className="font-semibold text-gray-800 mb-1">Dados da Proposta</h2>
                <p className="text-xs text-gray-400 mb-4">Variáveis preenchidas no template DOCX (proposta comercial)</p>

                {/* Dimensionamento Solar */}
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-2">Dimensionamento Solar</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {field('potencia_sistema', 'Potência Instalada', 'kWp')}
                  {field('geracao_mensal', 'Geração Mensal', 'kWh/mês')}
                  {field('consumo_mensal', 'Consumo Médio Mensal', 'kWh')}
                  {field('area_util', 'Área Necessária', 'm²')}
                </div>

                {/* Módulo Solar */}
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-2">Módulo Solar</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {field('modulo_fabricante', 'Fabricante do Módulo')}
                  {field('modulo_modelo', 'Modelo do Módulo')}
                  {field('modulo_potencia', 'Potência do Módulo', 'W')}
                  {field('modulo_quantidade', 'Quantidade de Módulos')}
                </div>

                {/* Inversor */}
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-2">Inversor</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {field('inversor_fabricante', 'Fabricante do Inversor')}
                  {field('inversor_potencia', 'Potência do Inversor', 'kW')}
                  {field('inversores_utilizados', 'Quantidade de Inversores')}
                </div>

                {/* Análise Financeira */}
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-2">Análise Financeira</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {field('economia_mensal', 'Economia Mensal Esperada', 'R$')}
                  {field('economia_mensal_p', 'Economia Esperada', '%')}
                  {field('vc_anual_atual', 'Conta de Luz Anual Atual', 'R$')}
                  {field('vc_anual_novo', 'Conta de Luz Anual com Solar', 'R$')}
                  {field('vc_economia_anual', 'Economia Anual', 'R$')}
                  {field('vc_servico', 'Valor dos Serviços', 'R$')}
                  {field('inflacao_energetica', 'Taxa de Inflação Energética', '% a.a.')}
                  {field('perda_eficiencia_anual', 'Perda de Eficiência Anual', '%')}
                  {field('gasto_total_mensal_atual', 'Gasto Total Mensal Atual', 'R$')}
                  {field('gasto_total_mensal_novo', 'Gasto Total Mensal Novo', 'R$')}
                  {field('capo_bancario', 'Campo Bancário / Conta')}
                </div>

                {/* Módulo - campos extras */}
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wide mb-2">Módulo Solar (extra)</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {field('vc_modulo_eficiencia', 'Eficiência do Módulo', '%')}
                  {field('inversor_potencia_nominal', 'Potência Nominal do Inversor')}
                  {field('cliente_complemento', 'Complemento do Endereço')}
                </div>

                {/* Campos personalizados */}
                {variaveisCustom.length > 0 && (() => {
                  const grupos = variaveisCustom.reduce<Record<string, typeof variaveisCustom>>((acc, v) => {
                    ;(acc[v.grupo] ||= []).push(v)
                    return acc
                  }, {})
                  return Object.entries(grupos).map(([grupo, vars]) => (
                    <div key={grupo} className="mb-4">
                      <p className="text-xs font-semibold text-orange-600 uppercase tracking-wide mb-2">{grupo}</p>
                      <div className="grid grid-cols-2 gap-3">
                        {vars.map(v => field(v.chave, v.label))}
                      </div>
                    </div>
                  ))
                })()}
              </div>
            )
          })()}

          {/* Premissas */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <span className="panel-title">Premissas de Custo</span>
                <p className="text-xs text-gray-400 mt-0.5">Percentuais calculados sobre o preço de venda</p>
              </div>
              <div className="flex gap-2 ml-auto">
                {templates.length > 0 && (
                  <div className="relative group">
                    <button className="btn-secondary text-xs">
                      <Plus className="w-3 h-3" /> Da lista <ChevronDown className="w-3 h-3" />
                    </button>
                    <div className="absolute right-0 top-full mt-1 w-52 bg-white border border-zinc-200 rounded-lg shadow-lg z-10 hidden group-hover:block">
                      {templates.map(t => {
                        const usado = premissasIdsUsados.has(t.id)
                        return (
                          <button key={t.id} onClick={() => adicionarPremissa(t)} disabled={usado}
                            className={`w-full text-left px-3 py-2 text-xs flex justify-between items-center ${
                              usado ? 'opacity-40 cursor-not-allowed' : 'hover:bg-zinc-50'
                            }`}>
                            <span className="text-zinc-800">{t.nome}</span>
                            <span className="text-zinc-500">
                              {usado ? '✓' : `${t.valor}${t.tipo === 'percentual' ? '%' : ' R$'}`}
                            </span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
                <button onClick={() => adicionarPremissa(undefined)} className="btn-secondary text-xs">
                  <Plus className="w-3 h-3" /> Personalizada
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="gov-table">
                <thead>
                  <tr>
                    <th>Premissa</th>
                    <th style={{ width: 140 }}>Tipo</th>
                    <th style={{ width: 110 }}>Valor</th>
                    <th style={{ width: 120 }} className="text-right">Calculado</th>
                    <th style={{ width: 40 }}></th>
                  </tr>
                </thead>
                <tbody>
                  {premissasAplicadas.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-gray-400">
                        Nenhuma premissa adicionada — use os botões acima
                      </td>
                    </tr>
                  )}
                  {premissasAplicadas.map((p, idx) => {
                    const calc = calculado?.premissas?.[idx]
                    return (
                      <tr key={p._key}>
                        <td>
                          {p.premissa_id ? (
                            <select value={p.premissa_id}
                              onChange={e => trocarTemplate(p._key, e.target.value)}
                              className="form-input h-8 text-xs">
                              {templates.map(t => <option key={t.id} value={t.id}>{t.nome}</option>)}
                            </select>
                          ) : (
                            <input value={p.nome}
                              onChange={e => atualizarPremissa(p._key, { nome: e.target.value })}
                              className="form-input h-8 text-xs" placeholder="Nome da premissa" />
                          )}
                        </td>
                        <td>
                          <select value={p.tipo}
                            onChange={e => atualizarPremissa(p._key, { tipo: e.target.value as 'percentual' | 'fixo' })}
                            className="form-input h-8 text-xs">
                            <option value="percentual">% do PV</option>
                            <option value="fixo">Fixo (R$)</option>
                          </select>
                        </td>
                        <td>
                          <div className="flex items-center gap-1.5">
                            <input type="number" value={p.valor}
                              onChange={e => atualizarPremissa(p._key, { valor: +e.target.value })}
                              min={0} step={0.01}
                              className="form-input h-8 text-xs flex-1" />
                            <span className="text-xs text-gray-400 w-5 shrink-0">
                              {p.tipo === 'percentual' ? '%' : 'R$'}
                            </span>
                          </div>
                        </td>
                        <td className="text-right font-semibold text-gray-800" style={{ fontVariantNumeric: 'tabular-nums' }}>
                          {calc ? fmt(calc.valor_calculado) : '—'}
                        </td>
                        <td>
                          <button onClick={() => removerPremissa(p._key)}
                            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Itens */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <span className="panel-title">Itens Adicionais</span>
                <p className="text-xs text-gray-400 mt-0.5">Produtos e custos avulsos não cobertos pelas premissas</p>
              </div>
              <div className="flex gap-2 ml-auto">
                <button onClick={() => adicionarItem('manual')} className="btn-secondary text-xs">
                  <Plus className="w-3 h-3" /> Custo Manual
                </button>
                <button onClick={() => adicionarItem('produto')} className="btn-secondary text-xs">
                  <Plus className="w-3 h-3" /> Produto
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="gov-table">
                <thead>
                  <tr>
                    <th style={{ width: 80 }}>Tipo</th>
                    <th>Descrição</th>
                    <th style={{ width: 80 }}>Qtd</th>
                    <th style={{ width: 120 }}>Valor Unit. (R$)</th>
                    <th style={{ width: 120 }} className="text-right">Total</th>
                    <th style={{ width: 40 }}></th>
                  </tr>
                </thead>
                <tbody>
                  {itens.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-gray-400">
                        Nenhum item adicionado — use os botões acima
                      </td>
                    </tr>
                  )}
                  {itens.map((item, idx) => {
                    const calc = calculado?.itens?.[idx]
                    return (
                      <tr key={item._key}>
                        <td>
                          <span className={item.tipo === 'manual' ? 'badge-yellow' : 'badge-green'}>
                            {item.tipo === 'manual' ? 'Manual' : 'Produto'}
                          </span>
                        </td>
                        <td>
                          <input value={item.descricao}
                            onChange={e => atualizarItem(item._key, { descricao: e.target.value })}
                            className="form-input h-8 text-xs" placeholder="Descrição do item" />
                        </td>
                        <td>
                          {item.tipo === 'produto' ? (
                            <input type="number" value={item.quantidade ?? 1}
                              onChange={e => atualizarItem(item._key, { quantidade: +e.target.value })}
                              min={0.001} step={0.001}
                              className="form-input h-8 text-xs" />
                          ) : (
                            <span className="text-gray-400 text-xs pl-3">—</span>
                          )}
                        </td>
                        <td>
                          <input type="number" value={item.valor_unitario ?? 0}
                            onChange={e => atualizarItem(item._key, { valor_unitario: +e.target.value })}
                            min={0} step={0.01}
                            className="form-input h-8 text-xs" />
                        </td>
                        <td className="text-right font-semibold text-gray-800" style={{ fontVariantNumeric: 'tabular-nums' }}>
                          {calc ? fmt(calc.valor_calculado) : '—'}
                        </td>
                        <td>
                          <button onClick={() => removerItem(item._key)}
                            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Composição do Preço */}
          {calculado && base > 0 && (
            <TabelaComposicao
              valorVenda={calculado.valor_venda}
              linhas={[
                { nome: 'Custo Base', qtd: 1, valor: calculado.custo_base, secao: 'base' },
                ...itens.map((item, idx) => ({
                  nome: item.descricao,
                  qtd: item.tipo === 'produto' ? (item.quantidade ?? 1) : 1,
                  valor: calculado.itens[idx]?.valor_calculado ?? 0,
                  secao: 'item' as const,
                  badge: item.tipo as 'manual' | 'produto',
                })),
                ...premissasAplicadas.map((p, idx) => ({
                  nome: p.nome,
                  qtd: null,
                  valor: calculado.premissas[idx]?.valor_calculado ?? 0,
                  secao: 'premissa' as const,
                })),
                { nome: 'Valor de Venda', qtd: 1, valor: calculado.valor_venda, secao: 'total' as const },
              ]}
            />
          )}
        </div>

        {/* Resumo lateral */}
        <div>
          <div className="bg-white rounded-xl border border-zinc-200 shadow-sm sticky top-6 overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100 flex items-center gap-2">
              <Calculator className="w-3.5 h-3.5 text-blue-600" />
              <span className="text-sm font-semibold text-zinc-800">Resumo do Cálculo</span>
            </div>
            <div className="p-5 space-y-1.5 text-sm">
              <div className="flex justify-between py-1.5 border-b border-zinc-100">
                <span className="text-gray-500">Custo base</span>
                <span className="font-medium text-gray-900" style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(base)}</span>
              </div>

              {(calculado?.premissas?.length ?? 0) > 0 && (
                <>
                  {calculado!.premissas.map((p, i) => (
                    <div key={i} className="flex justify-between text-xs">
                      <span className="text-gray-500 flex items-center gap-1.5 truncate mr-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-200 inline-block shrink-0" />
                        {p.nome}
                        {p.tipo === 'percentual' && (
                          <span className="text-gray-400">{p.valor}%</span>
                        )}
                      </span>
                      <span className="text-blue-600 shrink-0" style={{ fontVariantNumeric: 'tabular-nums' }}>+{fmt(p.valor_calculado)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between text-xs text-gray-500 pt-0.5 pb-1 border-b border-zinc-100">
                    <span>Subtotal premissas</span>
                    <span style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(calculado?.subtotal_premissas ?? 0)}</span>
                  </div>
                </>
              )}

              {(calculado?.itens?.length ?? 0) > 0 && (
                <>
                  {calculado!.itens.map((it, i) => (
                    <div key={i} className="flex justify-between text-xs">
                      <span className="text-gray-500 flex items-center gap-1.5 truncate mr-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-zinc-300 inline-block shrink-0" />
                        {it.descricao}
                      </span>
                      <span className="text-gray-500 shrink-0" style={{ fontVariantNumeric: 'tabular-nums' }}>+{fmt(it.valor_calculado)}</span>
                    </div>
                  ))}
                </>
              )}

              <div className="flex justify-between font-medium text-gray-800 pt-1.5 border-t border-zinc-100">
                <span>Subtotal</span>
                <span style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(calculado?.subtotal ?? base)}</span>
              </div>

              <div className="mt-3 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                <div className="flex justify-between font-bold text-blue-700">
                  <span>Valor de Venda</span>
                  <span style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(calculado?.valor_venda ?? base)}</span>
                </div>
                {calculado && calculado.valor_venda > 0 && calculado.custo_base > 0 && (
                  <div className="text-xs text-blue-400 mt-1 text-right" style={{ fontVariantNumeric: 'tabular-nums' }}>
                    Margem: {(((calculado.valor_venda - calculado.custo_base) / calculado.valor_venda) * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>

            <div className="px-5 pb-5">
              <button
                onClick={handleSalvar}
                disabled={loading || !titulo || !Number(custoBase)}
                className="btn-primary w-full justify-center">
                {loading ? 'Salvando...' : isNew ? 'Criar Orçamento' : 'Salvar Alterações'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
