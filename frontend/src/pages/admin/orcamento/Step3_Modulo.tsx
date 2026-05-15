import { useEffect, useState, useMemo } from 'react'
import { Search } from 'lucide-react'
import { solarApi } from '../../../api/solar'
import { useOrcamentoDraft } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'

const TIPOS = [
  { value: 'half_cell', label: 'Half-Cell' },
  { value: 'monocristalino', label: 'Mono PERC' },
  { value: 'topcon', label: 'TOPCon' },
  { value: 'bifacial', label: 'Bifacial' },
  { value: 'hjt', label: 'HJT' },
]

export function Step3_Modulo() {
  const { draft, setDraft } = useOrcamentoDraft()
  const [modulos, setModulos] = useState<any[]>([])
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [marcaFiltro, setMarcaFiltro] = useState('')
  const [busca, setBusca] = useState('')
  const [potMin, setPotMin] = useState<number | ''>(300)
  const [potMax, setPotMax] = useState<number | ''>(700)

  useEffect(() => { solarApi.modulos().then(setModulos).catch(() => {}) }, [])

  const marcas = useMemo(() => {
    let filtered = modulos
    if (tipoFiltro) filtered = filtered.filter(m => m.tipo === tipoFiltro)
    return [...new Set(filtered.map(m => m.marca))].sort()
  }, [modulos, tipoFiltro])

  const filtrados = useMemo(() => {
    let r = modulos
    if (tipoFiltro) r = r.filter(m => m.tipo === tipoFiltro)
    if (marcaFiltro) r = r.filter(m => m.marca === marcaFiltro)
    if (busca) { const t = busca.toLowerCase(); r = r.filter(m => m.marca.toLowerCase().includes(t) || m.modelo.toLowerCase().includes(t)) }
    if (potMin) r = r.filter(m => m.potencia_wp >= Number(potMin))
    if (potMax) r = r.filter(m => m.potencia_wp <= Number(potMax))
    return r
  }, [modulos, tipoFiltro, marcaFiltro, busca, potMin, potMax])

  const selectModulo = (m: any) => {
    setDraft({
      moduloId: m.id,
      moduloMarca: m.marca,
      moduloModelo: m.modelo,
      moduloPotencia: m.potencia_wp,
      moduloEficiencia: m.eficiencia || '',
      potenciaPlaca: m.potencia_wp,
      qtdModulos: draft.qtdPlacas ?? draft.qtdModulos,
    })
  }

  const canAdvance = !!draft.moduloId

  return (
    <WizardLayout canAdvance={canAdvance}>
      <div className="space-y-5">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-zinc-900">Selecione o Módulo Solar</h2>
          <p className="text-sm text-zinc-500 mt-1">Escolha o tipo, marca e modelo do painel fotovoltaico</p>
        </div>

        {/* Type chips */}
        <div className="flex flex-wrap gap-2 justify-center">
          <button
            onClick={() => { setTipoFiltro(''); setMarcaFiltro('') }}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              !tipoFiltro ? 'bg-blue-600 text-white shadow' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
            }`}
          >Todos</button>
          {TIPOS.map(t => (
            <button
              key={t.value}
              onClick={() => { setTipoFiltro(t.value); setMarcaFiltro('') }}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                tipoFiltro === t.value ? 'bg-blue-600 text-white shadow' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
              }`}
            >{t.label}</button>
          ))}
        </div>

        {/* Brand chips */}
        <div className="flex flex-wrap gap-1.5 justify-center">
          {marcas.map(marca => (
            <button
              key={marca}
              onClick={() => setMarcaFiltro(marcaFiltro === marca ? '' : marca)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                marcaFiltro === marca ? 'bg-emerald-600 text-white' : 'bg-zinc-50 text-zinc-600 hover:bg-zinc-100 border border-zinc-200'
              }`}
            >{marca}</button>
          ))}
        </div>

        {/* Filters row */}
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={busca} onChange={e => setBusca(e.target.value)}
              className="form-input pl-9" placeholder="Buscar por marca ou modelo..." />
          </div>
          <div className="w-24">
            <label className="form-label text-[10px]">Pot. mín (W)</label>
            <input type="number" value={potMin} onChange={e => setPotMin(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs" />
          </div>
          <div className="w-24">
            <label className="form-label text-[10px]">Pot. máx (W)</label>
            <input type="number" value={potMax} onChange={e => setPotMax(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs" />
          </div>
        </div>

        {/* Results */}
        <div className="text-xs text-zinc-400 mb-1">{filtrados.length} módulos encontrados</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[50vh] overflow-y-auto pr-1">
          {filtrados.map(m => {
            const selected = draft.moduloId === m.id
            return (
              <button
                key={m.id}
                onClick={() => selectModulo(m)}
                className={`text-left p-4 rounded-xl border-2 transition-all ${
                  selected
                    ? 'border-blue-500 bg-blue-50 shadow-md shadow-blue-100'
                    : 'border-zinc-200 bg-white hover:border-zinc-300 hover:shadow-sm'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold text-zinc-500">{m.marca}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    m.tipo === 'topcon' ? 'bg-violet-100 text-violet-700'
                    : m.tipo === 'bifacial' ? 'bg-blue-100 text-blue-700'
                    : m.tipo === 'hjt' ? 'bg-amber-100 text-amber-700'
                    : 'bg-zinc-100 text-zinc-600'
                  }`}>{m.tipo}</span>
                </div>
                <p className="text-sm font-semibold text-zinc-800 truncate">{m.modelo}</p>
                <div className="flex gap-3 mt-2 text-xs text-zinc-500">
                  <span className="font-bold text-zinc-800">{m.potencia_wp}W</span>
                  <span>{m.eficiencia}%</span>
                  <span>{m.garantia_produto_anos}a</span>
                </div>
              </button>
            )
          })}
        </div>

        {/* Selected module summary */}
        {draft.moduloId && (
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-blue-600 font-semibold">Módulo selecionado</p>
                <p className="text-sm font-bold text-blue-900">{draft.moduloMarca} — {draft.moduloModelo} ({draft.moduloPotencia}W)</p>
              </div>
              <div>
                <label className="form-label text-[10px] text-blue-600">Quantidade</label>
                <input
                  type="number"
                  value={draft.qtdModulos}
                  onChange={e => setDraft({ qtdModulos: e.target.value === '' ? '' : +e.target.value })}
                  min={1}
                  className="form-input w-20 h-8 text-sm text-center"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </WizardLayout>
  )
}
