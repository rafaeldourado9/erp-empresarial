import { useEffect, useState, useMemo } from 'react'
import { Package, Plus, Minus } from 'lucide-react'
import { solarApi } from '../../../api/solar'
import { useOrcamentoDraft, type ComponenteSelecionado } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'

const CATEGORIAS = [
  { value: '', label: 'Todos' },
  { value: 'transformador', label: 'Transformadores' },
  { value: 'string_box', label: 'String Boxes' },
  { value: 'otimizador', label: 'Otimizadores' },
  { value: 'estrutura', label: 'Estruturas' },
  { value: 'cabo', label: 'Cabos' },
  { value: 'protecao', label: 'Proteção' },
  { value: 'monitoramento', label: 'Monitoramento' },
]

export function Step5_Componentes() {
  const { draft, setDraft } = useOrcamentoDraft()
  const [componentes, setComponentes] = useState<any[]>([])
  const [catFiltro, setCatFiltro] = useState('')

  useEffect(() => { solarApi.componentes().then(setComponentes).catch(() => {}) }, [])

  const filtrados = useMemo(() => {
    if (!catFiltro) return componentes
    return componentes.filter(c => c.categoria === catFiltro)
  }, [componentes, catFiltro])

  const selecionados = draft.componentesSelecionados
  const selecionadoById = new Map(selecionados.map(s => [s.id, s]))

  const toggleComponente = (comp: any) => {
    const exists = selecionadoById.get(comp.id)
    if (exists) {
      setDraft({ componentesSelecionados: selecionados.filter(s => s.id !== comp.id) })
    } else {
      const novo: ComponenteSelecionado = {
        id: comp.id, categoria: comp.categoria, marca: comp.marca,
        modelo: comp.modelo, quantidade: 1, preco_referencia: comp.preco_referencia,
      }
      setDraft({ componentesSelecionados: [...selecionados, novo] })
    }
  }

  const updateQtd = (id: string, qtd: number) => {
    setDraft({
      componentesSelecionados: selecionados.map(s =>
        s.id === id ? { ...s, quantidade: Math.max(1, qtd) } : s
      ),
    })
  }

  const total = selecionados.reduce((acc, s) => acc + s.quantidade * s.preco_referencia, 0)
  const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <WizardLayout canAdvance={true}>
      <div className="space-y-5">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-zinc-900 flex items-center justify-center gap-2">
            <Package className="w-6 h-6 text-amber-500" /> Componentes Opcionais
          </h2>
          <p className="text-sm text-zinc-500 mt-1">Adicione transformadores, string boxes, cabos e outros itens BOS (opcional)</p>
        </div>

        {/* Category tabs */}
        <div className="flex flex-wrap gap-2 justify-center">
          {CATEGORIAS.map(c => (
            <button
              key={c.value}
              onClick={() => setCatFiltro(c.value)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                catFiltro === c.value ? 'bg-amber-500 text-white shadow' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
              }`}
            >{c.label}</button>
          ))}
        </div>

        {/* Component grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtrados.map(comp => {
            const sel = selecionadoById.get(comp.id)
            return (
              <div
                key={comp.id}
                className={`p-4 rounded-xl border-2 transition-all ${
                  sel
                    ? 'border-amber-400 bg-amber-50 shadow-sm'
                    : 'border-zinc-200 bg-white hover:border-zinc-300'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-zinc-400">{comp.categoria.replace('_', ' ')}</span>
                  <span className="text-xs font-semibold text-emerald-600">{fmt(comp.preco_referencia)}</span>
                </div>
                <p className="text-xs font-semibold text-zinc-500 mb-0.5">{comp.marca}</p>
                <p className="text-sm font-semibold text-zinc-800 mb-1">{comp.modelo}</p>
                <p className="text-xs text-zinc-500 mb-3">{comp.descricao}</p>

                {sel ? (
                  <div className="flex items-center gap-2">
                    <button onClick={() => updateQtd(comp.id, sel.quantidade - 1)} className="p-1 rounded bg-zinc-100 hover:bg-zinc-200">
                      <Minus className="w-3 h-3" />
                    </button>
                    <span className="text-sm font-bold w-8 text-center">{sel.quantidade}</span>
                    <button onClick={() => updateQtd(comp.id, sel.quantidade + 1)} className="p-1 rounded bg-zinc-100 hover:bg-zinc-200">
                      <Plus className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => toggleComponente(comp)}
                      className="ml-auto text-xs text-red-500 hover:text-red-700 font-medium"
                    >Remover</button>
                  </div>
                ) : (
                  <button
                    onClick={() => toggleComponente(comp)}
                    className="w-full py-1.5 rounded-lg bg-zinc-100 text-zinc-600 text-xs font-medium hover:bg-amber-100 hover:text-amber-700 transition-colors"
                  >
                    <Plus className="w-3 h-3 inline mr-1" /> Adicionar
                  </button>
                )}
              </div>
            )
          })}
        </div>

        {/* Total footer */}
        {selecionados.length > 0 && (
          <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-amber-600 font-semibold">{selecionados.length} componente(s) selecionado(s)</p>
                {selecionados.map(s => (
                  <p key={s.id} className="text-xs text-amber-800">{s.quantidade}× {s.modelo} = {fmt(s.quantidade * s.preco_referencia)}</p>
                ))}
              </div>
              <p className="text-lg font-bold text-amber-800">{fmt(total)}</p>
            </div>
          </div>
        )}
      </div>
    </WizardLayout>
  )
}
