import { createContext, useContext, useCallback, useEffect, useState, type ReactNode } from 'react'

/* ── Types ──────────────────────────────────────────────────────────────── */

export interface PremissaAplicada {
  _key: string; premissa_id?: string; nome: string; descricao?: string
  tipo: 'percentual' | 'fixo'; valor: number; ordem: number
  obrigatoria?: boolean
}

export interface ItemOrcamento {
  _key: string; tipo: 'manual' | 'produto'; descricao: string
  item_estoque_id?: string; quantidade?: number; valor_unitario?: number; ordem: number
}

export interface ComponenteSelecionado {
  id: string; categoria: string; marca: string; modelo: string
  quantidade: number; preco_referencia: number
}

export interface DraftState {
  step: number
  // Step 1 — Cliente
  titulo: string
  clienteId: string
  vendedorId: string
  uf: string
  cidade: string
  validadeDias: number
  observacoes: string
  clienteComplemento: string   // endereço da instalação
  // Step 2 — Dimensionamento
  consumoMensal: number | ''
  potenciaPlaca: number | ''
  fatorRegional: number
  qtdPlacas: number | null
  kwpSistema: number | null
  areaUtil: number | ''        // m² calculado ou manual
  // Step 3 — Módulo
  moduloId: string
  moduloMarca: string
  moduloModelo: string
  moduloPotencia: number | null
  moduloEficiencia: number | '' // % eficiência do módulo
  qtdModulos: number | ''
  // Step 4 — Inversor
  tipoInversor: string
  inversorId: string
  inversorMarca: string
  inversorModelo: string
  inversorPotencia: number | null
  qtdInversores: number | ''
  fatorOverload: number
  // Step 5 — Componentes
  componentesSelecionados: ComponenteSelecionado[]
  // Step 6 — Resumo + Análise Econômica
  custoBase: number | ''
  valorVendaManual: number | ''
  premissasAplicadas: PremissaAplicada[]
  itens: ItemOrcamento[]
  camposExtras: Record<string, string>
  // Análise econômica
  tarifaEnergia: number | ''     // R$/kWh
  economiaMensalP: number | ''   // % economia esperada
  inflacaoEnergetica: number | '' // % a.a.
  perdaEficienciaAnual: number | '' // % por ano
}

const INITIAL_DRAFT: DraftState = {
  step: 1,
  titulo: '', clienteId: '', vendedorId: '', uf: 'SP', cidade: '',
  validadeDias: 30, observacoes: '', clienteComplemento: '',
  consumoMensal: '', potenciaPlaca: 540, fatorRegional: 126,
  qtdPlacas: null, kwpSistema: null, areaUtil: '',
  moduloId: '', moduloMarca: '', moduloModelo: '', moduloPotencia: null,
  moduloEficiencia: '', qtdModulos: '',
  tipoInversor: 'string', inversorId: '', inversorMarca: '', inversorModelo: '',
  inversorPotencia: null, qtdInversores: 1, fatorOverload: 1.3,
  componentesSelecionados: [],
  custoBase: '', valorVendaManual: '',
  premissasAplicadas: [], itens: [], camposExtras: {},
  tarifaEnergia: 0.85, economiaMensalP: 95, inflacaoEnergetica: 8, perdaEficienciaAnual: 0.7,
}

/* ── Context ────────────────────────────────────────────────────────────── */

interface DraftCtx {
  draft: DraftState
  setDraft: (updates: Partial<DraftState>) => void
  resetDraft: () => void
  setStep: (step: number) => void
  loadFromOrcamento: (orc: any) => void
}

const DraftContext = createContext<DraftCtx | null>(null)

function getDraftKey(userId?: string) {
  return `orcamento-draft-${userId ?? 'anon'}`
}

export function OrcamentoDraftProvider({ userId, children }: { userId?: string; children: ReactNode }) {
  const key = getDraftKey(userId)

  const [draft, _setDraft] = useState<DraftState>(() => {
    try {
      const saved = localStorage.getItem(key)
      if (saved) {
        const parsed = JSON.parse(saved)
        return { ...INITIAL_DRAFT, ...parsed }
      }
    } catch { /* ignore */ }
    return { ...INITIAL_DRAFT }
  })

  // Persist to localStorage on changes (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem(key, JSON.stringify(draft))
    }, 300)
    return () => clearTimeout(timer)
  }, [draft, key])

  const setDraft = useCallback((updates: Partial<DraftState>) => {
    _setDraft(prev => ({ ...prev, ...updates }))
  }, [])

  const resetDraft = useCallback(() => {
    localStorage.removeItem(key)
    _setDraft({ ...INITIAL_DRAFT })
  }, [key])

  const setStep = useCallback((step: number) => {
    _setDraft(prev => ({ ...prev, step: Math.max(1, Math.min(6, step)) }))
  }, [])

  const loadFromOrcamento = useCallback((orc: any) => {
    const ex: Record<string, string> = orc.campos_extras || {}
    const n = (k: string) => { const v = ex[k]; return v ? Number(v) : '' }
    _setDraft({
      ...INITIAL_DRAFT,
      step: 6,
      titulo: orc.titulo || '',
      custoBase: orc.custo_base || '',
      clienteId: orc.cliente_id || '',
      vendedorId: orc.vendedor_id || '',
      validadeDias: orc.validade_dias || 30,
      observacoes: orc.observacoes || '',
      clienteComplemento: ex['cliente_complemento'] || '',
      camposExtras: ex,
      // Restore solar dimensioning from campos_extras
      consumoMensal: n('consumo_mensal'),
      kwpSistema: n('potencia_sistema') || null,
      areaUtil: n('area_util'),
      moduloMarca: ex['modulo_fabricante'] || '',
      moduloModelo: ex['modulo_modelo'] || '',
      moduloPotencia: n('modulo_potencia') || null,
      moduloEficiencia: n('vc_modulo_eficiencia'),
      qtdModulos: n('modulo_quantidade'),
      inversorMarca: ex['inversor_fabricante'] || '',
      inversorPotencia: n('inversor_potencia') || null,
      qtdInversores: n('inversores_utilizados'),
      // Restore financial analysis
      tarifaEnergia: n('tarifa_energia') || 0.85,
      economiaMensalP: n('economia_mensal_p') || 95,
      inflacaoEnergetica: n('inflacao_energetica') || 8,
      perdaEficienciaAnual: n('perda_eficiencia_anual') || 0.7,
      premissasAplicadas: (orc.premissas || []).map((p: any) => ({
        _key: crypto.randomUUID(),
        premissa_id: p.premissa_id, nome: p.nome, descricao: p.descricao,
        tipo: p.tipo, valor: p.valor, ordem: p.ordem,
        obrigatoria: p.obrigatoria ?? false,
      })),
      itens: (orc.itens || []).map((i: any) => ({
        _key: crypto.randomUUID(),
        tipo: i.tipo, descricao: i.descricao, item_estoque_id: i.item_estoque_id,
        quantidade: i.quantidade, valor_unitario: i.valor_unitario, ordem: i.ordem,
      })),
    })
  }, [])

  return (
    <DraftContext.Provider value={{ draft, setDraft, resetDraft, setStep, loadFromOrcamento }}>
      {children}
    </DraftContext.Provider>
  )
}

export function useOrcamentoDraft() {
  const ctx = useContext(DraftContext)
  if (!ctx) throw new Error('useOrcamentoDraft must be used inside OrcamentoDraftProvider')
  return ctx
}
