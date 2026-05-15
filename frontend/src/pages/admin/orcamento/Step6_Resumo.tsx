import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Plus, Trash2, ChevronDown, Lock, Calculator, Check, UserCheck } from 'lucide-react'
import { orcamentosApi, premissasApi } from '../../../api/quotes'
import { operadoresApi } from '../../../api/operators'
import { useOrcamentoDraft, type PremissaAplicada, type ItemOrcamento } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'
import { TabelaComposicao } from '../../../components/TabelaComposicao'

const fmt = (v: number) =>
  `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

interface PremissaTemplate {
  id: string; nome: string; descricao?: string
  tipo: 'percentual' | 'fixo'; valor: number; ordem: number
  obrigatoria?: boolean
}

interface Calculado {
  custo_base: number; subtotal_premissas: number; subtotal_itens: number
  subtotal: number; valor_venda: number
  premissas: { nome: string; tipo: string; valor: number; valor_calculado: number }[]
  itens: { descricao: string; valor_calculado: number }[]
}

export function Step6_Resumo() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { draft, setDraft, resetDraft } = useOrcamentoDraft()
  const [templates, setTemplates] = useState<PremissaTemplate[]>([])
  const [vendedores, setVendedores] = useState<any[]>([])
  const [calculado, setCalculado] = useState<Calculado | null>(null)
  const [pvFormula, setPvFormula] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  useEffect(() => { premissasApi.listar().then(setTemplates).catch(() => {}) }, [])
  useEffect(() => { operadoresApi.listar().then(setVendedores).catch(() => {}) }, [])

  const base = Number(draft.custoBase) || 0
  const premissas = draft.premissasAplicadas
  const itens = draft.itens

  const recalcular = useCallback(async () => {
    if (!base || base <= 0) { setCalculado(null); setPvFormula(null); return }
    const payload = {
      custo_base: base,
      premissas: premissas.map((p, idx) => ({
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
      if (draft.valorVendaManual && Number(draft.valorVendaManual) > 0) {
        const overrideResult = await orcamentosApi.calcular({ ...payload, valor_venda: Number(draft.valorVendaManual) })
        setCalculado(overrideResult)
      } else {
        setCalculado(formulaResult)
      }
    } catch {}
  }, [base, draft.valorVendaManual, premissas, itens])

  useEffect(() => { const t = setTimeout(recalcular, 400); return () => clearTimeout(t) }, [recalcular])

  const premissasIdsUsados = new Set(premissas.filter(p => p.premissa_id).map(p => p.premissa_id!))

  const adicionarPremissa = (template?: PremissaTemplate) => {
    if (template) {
      if (premissasIdsUsados.has(template.id)) return
      setDraft({ premissasAplicadas: [...premissas, {
        _key: crypto.randomUUID(), premissa_id: template.id, nome: template.nome,
        descricao: template.descricao, tipo: template.tipo, valor: template.valor, ordem: premissas.length,
        obrigatoria: template.obrigatoria,
      }] })
      return
    }
    setDraft({ premissasAplicadas: [...premissas, {
      _key: crypto.randomUUID(), nome: 'Nova premissa', tipo: 'percentual', valor: 0, ordem: premissas.length,
    }] })
  }

  const atualizarPremissa = (key: string, changes: Partial<PremissaAplicada>) =>
    setDraft({ premissasAplicadas: premissas.map(p => p._key === key ? { ...p, ...changes } : p) })

  const removerPremissa = (key: string) => {
    const p = premissas.find(p => p._key === key)
    if (p?.obrigatoria) return
    setDraft({ premissasAplicadas: premissas.filter(p => p._key !== key) })
  }

  const adicionarItem = (tipo: 'manual' | 'produto') =>
    setDraft({ itens: [...itens, {
      _key: crypto.randomUUID(), tipo, descricao: tipo === 'manual' ? 'Custo adicional' : 'Produto',
      quantidade: tipo === 'produto' ? 1 : undefined, valor_unitario: 0, ordem: itens.length,
    }] })

  const atualizarItem = (key: string, changes: Partial<ItemOrcamento>) =>
    setDraft({ itens: itens.map(i => i._key === key ? { ...i, ...changes } : i) })

  const removerItem = (key: string) =>
    setDraft({ itens: itens.filter(i => i._key !== key) })

  const economiaMensal = (() => {
    const tarifa = Number(draft.tarifaEnergia) || 0
    const consumo = Number(draft.consumoMensal) || 0
    const pct = Number(draft.economiaMensalP) || 0
    return tarifa > 0 && consumo > 0 ? consumo * tarifa * (pct / 100) : 0
  })()

  const areaUtilCalc = (() => {
    const qtd = Number(draft.qtdModulos) || Number(draft.qtdPlacas) || 0
    return qtd > 0 ? (qtd * 1.9).toFixed(1) : (draft.areaUtil ? String(draft.areaUtil) : '')
  })()

  const geracaoMensal = Number(draft.consumoMensal) || 0

  const handleSalvar = async () => {
    if (!draft.titulo) { setSaveError('Informe o título do orçamento'); return }
    if (!base) { setSaveError('Informe o custo base'); return }
    setSaveError(null)
    setLoading(true)
    try {
      // Build campos_extras with all solar + financial data + user custom fields
      const solarData: Record<string, string> = {
        // Dimensionamento
        consumo_mensal: String(draft.consumoMensal || ''),
        potencia_sistema: draft.kwpSistema ? String(draft.kwpSistema) : '',
        geracao_mensal: geracaoMensal ? String(geracaoMensal) : '',
        area_util: areaUtilCalc,
        // Módulo
        modulo_fabricante: draft.moduloMarca || '',
        modulo_modelo: draft.moduloModelo || '',
        modulo_potencia: draft.moduloPotencia ? String(draft.moduloPotencia) : '',
        modulo_quantidade: draft.qtdModulos ? String(draft.qtdModulos) : '',
        vc_modulo_eficiencia: draft.moduloEficiencia ? String(draft.moduloEficiencia) : '',
        // Inversor
        inversor_fabricante: draft.inversorMarca || '',
        inversor_potencia: draft.inversorPotencia ? String(draft.inversorPotencia) : '',
        inversor_potencia_nominal: draft.inversorPotencia ? String(draft.inversorPotencia * 1000) : '',
        inversores_utilizados: draft.qtdInversores ? String(draft.qtdInversores) : '',
        // Análise econômica
        tarifa_energia: String(draft.tarifaEnergia || ''),
        economia_mensal: economiaMensal ? economiaMensal.toFixed(2) : '',
        economia_mensal_p: String(draft.economiaMensalP || ''),
        inflacao_energetica: String(draft.inflacaoEnergetica || ''),
        perda_eficiencia_anual: String(draft.perdaEficienciaAnual || ''),
        // Endereço instalação
        cliente_complemento: draft.clienteComplemento || '',
      }
      const campos_extras = { ...solarData, ...draft.camposExtras }

      const payload = {
        titulo: draft.titulo, custo_base: base,
        valor_venda: draft.valorVendaManual ? Number(draft.valorVendaManual) : undefined,
        cliente_id: draft.clienteId || undefined,
        vendedor_id: draft.vendedorId || undefined,
        validade_dias: draft.validadeDias,
        observacoes: draft.observacoes || undefined,
        campos_extras,
        premissas: premissas.map((p, idx) => ({
          premissa_id: p.premissa_id || undefined, nome: p.nome, descricao: p.descricao,
          tipo: p.tipo, valor: p.valor, ordem: idx,
        })),
        itens: itens.map((i, idx) => ({
          tipo: i.tipo, descricao: i.descricao, item_estoque_id: i.item_estoque_id || undefined,
          quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: idx,
        })),
      }
      if (!id) { await orcamentosApi.criar(payload) } else { await orcamentosApi.atualizar(id, payload) }
      resetDraft()
      navigate('/orcamentos')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <WizardLayout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <h2 className="text-2xl font-bold text-zinc-900">Resumo do Orçamento</h2>

          {/* System summary — só exibe se há dados solares */}
          {(draft.moduloMarca || draft.inversorMarca || draft.kwpSistema) && (
            <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-5 border border-indigo-100">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div><span className="text-xs text-indigo-500 font-semibold">Módulo</span><p className="font-bold text-indigo-900">{draft.moduloMarca || '—'} {draft.moduloPotencia ? `${draft.moduloPotencia}W` : ''}</p></div>
                <div><span className="text-xs text-indigo-500 font-semibold">Qtd Módulos</span><p className="font-bold text-indigo-900">{draft.qtdModulos || '—'}</p></div>
                <div><span className="text-xs text-indigo-500 font-semibold">Inversor</span><p className="font-bold text-indigo-900">{draft.inversorMarca || '—'} {draft.inversorPotencia ? `${draft.inversorPotencia}kW` : ''}</p></div>
                <div><span className="text-xs text-indigo-500 font-semibold">kWp</span><p className="font-bold text-indigo-900">{draft.kwpSistema ? `${draft.kwpSistema} kWp` : '—'}</p></div>
              </div>
            </div>
          )}

          {/* Análise Econômica — sempre visível para preenchimento do template */}
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Análise Econômica</span>
              <span className="text-xs text-zinc-400">Dados usados no template DOCX</span>
            </div>
            <div className="panel-body space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="form-label">Tarifa energia (R$/kWh)</label>
                  <input type="number" value={draft.tarifaEnergia}
                    onChange={e => setDraft({ tarifaEnergia: e.target.value === '' ? '' : +e.target.value })}
                    min={0} step={0.01} placeholder="0,85" className="form-input" />
                </div>
                <div>
                  <label className="form-label">Economia esperada (%)</label>
                  <input type="number" value={draft.economiaMensalP}
                    onChange={e => setDraft({ economiaMensalP: e.target.value === '' ? '' : +e.target.value })}
                    min={0} max={100} step={1} placeholder="95" className="form-input" />
                </div>
                <div>
                  <label className="form-label">Inflação energética (% a.a.)</label>
                  <input type="number" value={draft.inflacaoEnergetica}
                    onChange={e => setDraft({ inflacaoEnergetica: e.target.value === '' ? '' : +e.target.value })}
                    min={0} step={0.1} placeholder="8" className="form-input" />
                </div>
                <div>
                  <label className="form-label">Perda eficiência (% a.a.)</label>
                  <input type="number" value={draft.perdaEficienciaAnual}
                    onChange={e => setDraft({ perdaEficienciaAnual: e.target.value === '' ? '' : +e.target.value })}
                    min={0} max={5} step={0.1} placeholder="0,7" className="form-input" />
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="form-label">Eficiência do módulo (%)</label>
                  <input type="number" value={draft.moduloEficiencia}
                    onChange={e => setDraft({ moduloEficiencia: e.target.value === '' ? '' : +e.target.value })}
                    min={0} max={30} step={0.1} placeholder="21" className="form-input" />
                </div>
                <div>
                  <label className="form-label">Área útil (m²)</label>
                  <input type="number" value={draft.areaUtil || areaUtilCalc}
                    onChange={e => setDraft({ areaUtil: e.target.value === '' ? '' : +e.target.value })}
                    min={0} step={0.1} placeholder={areaUtilCalc || 'Auto'} className="form-input" />
                  {areaUtilCalc && !draft.areaUtil && (
                    <p className="text-xs text-zinc-400 mt-0.5">Calculado: {areaUtilCalc} m²</p>
                  )}
                </div>
                <div>
                  <label className="form-label">End. de Instalação</label>
                  <input type="text" value={draft.clienteComplemento}
                    onChange={e => setDraft({ clienteComplemento: e.target.value })}
                    placeholder="Ex: Rua das Flores, 123" className="form-input" />
                </div>
                {economiaMensal > 0 && (
                  <div className="bg-green-50 rounded-lg p-3 border border-green-100 flex flex-col justify-center">
                    <p className="text-xs text-green-600 font-semibold">Economia mensal</p>
                    <p className="text-lg font-bold text-green-800">
                      {economiaMensal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                    <p className="text-xs text-green-500">{draft.economiaMensalP}% de {draft.consumoMensal || 0} kWh × R$ {draft.tarifaEnergia}/kWh</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Vendedor e comissão */}
          {draft.vendedorId && (() => {
            const v = vendedores.find((x: any) => x.id === draft.vendedorId)
            if (!v) return null
            return (
              <div className="flex items-center gap-3 p-4 rounded-xl border border-emerald-200 bg-emerald-50">
                <UserCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <div className="text-sm text-emerald-800">
                  <span className="font-semibold">{v.nome}</span>
                  {v.comissao_percentual > 0
                    ? <span className="ml-2 text-emerald-600">— comissão de {v.comissao_percentual}% sobre o valor de venda (aplicada na aprovação)</span>
                    : <span className="ml-2 text-zinc-500">— sem comissão configurada</span>
                  }
                </div>
              </div>
            )
          })()}

          {/* Custo base */}
          <div className="panel">
            <div className="panel-body">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Custo Base (R$) *</label>
                  <input type="number" value={draft.custoBase}
                    onChange={e => setDraft({ custoBase: e.target.value === '' ? '' : +e.target.value })}
                    min={0} step={0.01} placeholder="0,00" className="form-input" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="form-label mb-0">
                      Valor de Venda (R$)
                      <span className={`ml-2 text-xs px-1.5 py-0.5 rounded font-normal ${
                        draft.valorVendaManual ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                      }`}>{draft.valorVendaManual ? 'manual' : 'auto'}</span>
                    </label>
                  </div>
                  <input type="number" value={draft.valorVendaManual}
                    onChange={e => setDraft({ valorVendaManual: e.target.value === '' ? '' : +e.target.value })}
                    min={0} step={0.01}
                    placeholder={pvFormula ? fmt(pvFormula) : 'Calculado'}
                    className={`form-input ${draft.valorVendaManual ? 'border-yellow-300' : ''}`} />
                </div>
              </div>
            </div>
          </div>

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
                    <button className="btn-secondary text-xs"><Plus className="w-3 h-3" /> Da lista <ChevronDown className="w-3 h-3" /></button>
                    <div className="absolute right-0 top-full mt-1 w-52 bg-white border border-zinc-200 rounded-lg shadow-lg z-10 hidden group-hover:block">
                      {templates.map(t => {
                        const usado = premissasIdsUsados.has(t.id)
                        return (
                          <button key={t.id} onClick={() => adicionarPremissa(t)} disabled={usado}
                            className={`w-full text-left px-3 py-2 text-xs flex justify-between items-center ${usado ? 'opacity-40 cursor-not-allowed' : 'hover:bg-zinc-50'}`}>
                            <span className="text-zinc-800 flex items-center gap-1">
                              {t.obrigatoria && <Lock className="w-2.5 h-2.5 text-amber-500" />}
                              {t.nome}
                            </span>
                            <span className="text-zinc-500 inline-flex items-center">{usado ? <Check className="w-3 h-3 text-green-600" /> : `${t.valor}${t.tipo === 'percentual' ? '%' : ' R$'}`}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
                <button onClick={() => adicionarPremissa(undefined)} className="btn-secondary text-xs"><Plus className="w-3 h-3" /> Personalizada</button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="gov-table">
                <thead><tr><th>Premissa</th><th style={{ width: 120 }}>Tipo</th><th style={{ width: 100 }}>Valor</th><th style={{ width: 110 }} className="text-right">Calculado</th><th style={{ width: 40 }}></th></tr></thead>
                <tbody>
                  {premissas.length === 0 && (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhuma premissa adicionada</td></tr>
                  )}
                  {premissas.map((p, idx) => {
                    const calc = calculado?.premissas?.[idx]
                    const locked = p.obrigatoria
                    return (
                      <tr key={p._key} className={locked ? 'bg-amber-50/50' : ''}>
                        <td>
                          <div className="flex items-center gap-1.5">
                            {locked && <span title="Definida pelo administrador"><Lock className="w-3 h-3 text-amber-500 shrink-0" /></span>}
                            <input value={p.nome}
                              onChange={e => !locked && atualizarPremissa(p._key, { nome: e.target.value })}
                              disabled={locked}
                              className="form-input h-8 text-xs" placeholder="Nome" />
                          </div>
                        </td>
                        <td>
                          <select value={p.tipo}
                            onChange={e => !locked && atualizarPremissa(p._key, { tipo: e.target.value as 'percentual' | 'fixo' })}
                            disabled={locked} className="form-input h-8 text-xs">
                            <option value="percentual">% do PV</option>
                            <option value="fixo">Fixo (R$)</option>
                          </select>
                        </td>
                        <td>
                          <div className="flex items-center gap-1.5">
                            <input type="number" value={p.valor}
                              onChange={e => !locked && atualizarPremissa(p._key, { valor: +e.target.value })}
                              disabled={locked} min={0} step={0.01} className="form-input h-8 text-xs flex-1" />
                            <span className="text-xs text-gray-400 w-5 shrink-0">{p.tipo === 'percentual' ? '%' : 'R$'}</span>
                          </div>
                        </td>
                        <td className="text-right font-semibold text-gray-800" style={{ fontVariantNumeric: 'tabular-nums' }}>
                          {calc ? fmt(calc.valor_calculado) : '—'}
                        </td>
                        <td>
                          {locked ? (
                            <span className="text-xs text-amber-500" title="Obrigatória"><Lock className="w-3 h-3" /></span>
                          ) : (
                            <button onClick={() => removerPremissa(p._key)}
                              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
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
                ...premissas.map((p, idx) => ({
                  nome: p.nome,
                  qtd: null,
                  valor: calculado.premissas[idx]?.valor_calculado ?? 0,
                  secao: 'premissa' as const,
                  obrigatoria: p.obrigatoria,
                })),
                { nome: 'Valor de Venda', qtd: 1, valor: calculado.valor_venda, secao: 'total' as const },
              ]}
            />
          )}

          {/* Itens */}
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Itens Adicionais</span>
              <div className="flex gap-2 ml-auto">
                <button onClick={() => adicionarItem('manual')} className="btn-secondary text-xs"><Plus className="w-3 h-3" /> Manual</button>
                <button onClick={() => adicionarItem('produto')} className="btn-secondary text-xs"><Plus className="w-3 h-3" /> Produto</button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="gov-table">
                <thead><tr><th style={{ width: 70 }}>Tipo</th><th>Descrição</th><th style={{ width: 70 }}>Qtd</th><th style={{ width: 100 }}>Val. Unit.</th><th style={{ width: 100 }} className="text-right">Total</th><th style={{ width: 36 }}></th></tr></thead>
                <tbody>
                  {itens.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhum item</td></tr>}
                  {itens.map((item, idx) => {
                    const calc = calculado?.itens?.[idx]
                    return (
                      <tr key={item._key}>
                        <td><span className={item.tipo === 'manual' ? 'badge-yellow' : 'badge-green'}>{item.tipo === 'manual' ? 'M' : 'P'}</span></td>
                        <td><input value={item.descricao} onChange={e => atualizarItem(item._key, { descricao: e.target.value })} className="form-input h-8 text-xs" /></td>
                        <td>{item.tipo === 'produto' ? <input type="number" value={item.quantidade ?? 1} onChange={e => atualizarItem(item._key, { quantidade: +e.target.value })} min={1} className="form-input h-8 text-xs" /> : <span className="text-gray-400 text-xs">—</span>}</td>
                        <td><input type="number" value={item.valor_unitario ?? 0} onChange={e => atualizarItem(item._key, { valor_unitario: +e.target.value })} min={0} step={0.01} className="form-input h-8 text-xs" /></td>
                        <td className="text-right font-semibold text-gray-800" style={{ fontVariantNumeric: 'tabular-nums' }}>{calc ? fmt(calc.valor_calculado) : '—'}</td>
                        <td><button onClick={() => removerItem(item._key)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"><Trash2 className="w-3.5 h-3.5" /></button></td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div>
          <div className="bg-white rounded-xl border border-zinc-200 shadow-sm sticky top-6 overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100 flex items-center gap-2">
              <Calculator className="w-3.5 h-3.5 text-blue-600" />
              <span className="text-sm font-semibold text-zinc-800">Resumo</span>
            </div>
            <div className="p-5 space-y-1.5 text-sm">
              <div className="flex justify-between py-1.5 border-b border-zinc-100">
                <span className="text-gray-500">Custo base</span>
                <span className="font-medium text-gray-900" style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(base)}</span>
              </div>
              {calculado?.premissas?.map((p, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <span className="text-gray-500 truncate mr-2">{p.nome}</span>
                  <span className="text-blue-600 shrink-0" style={{ fontVariantNumeric: 'tabular-nums' }}>+{fmt(p.valor_calculado)}</span>
                </div>
              ))}
              <div className="mt-3 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                <div className="flex justify-between font-bold text-blue-700">
                  <span>Valor de Venda</span>
                  <span style={{ fontVariantNumeric: 'tabular-nums' }}>{fmt(calculado?.valor_venda ?? base)}</span>
                </div>
                {calculado && calculado.valor_venda > 0 && base > 0 && (
                  <div className="text-xs text-blue-400 mt-1 text-right" style={{ fontVariantNumeric: 'tabular-nums' }}>
                    Margem: {(((calculado.valor_venda - base) / calculado.valor_venda) * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>
            <div className="px-5 pb-5 space-y-3">
              {saveError && (
                <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{saveError}</p>
              )}
              <button
                onClick={handleSalvar}
                disabled={loading}
                className="btn-primary w-full justify-center"
              >
                {loading ? 'Salvando...' : !id ? 'Criar Orçamento' : 'Salvar Alterações'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </WizardLayout>
  )
}
