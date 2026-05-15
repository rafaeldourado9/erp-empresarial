import { useEffect, useState, useMemo } from 'react'
import { Search, Zap, Battery, Sun, Cpu } from 'lucide-react'
import { solarApi } from '../../../api/solar'
import { useOrcamentoDraft } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'

const TIPOS = [
  { value: 'string', label: 'On-Grid', icon: Sun, color: 'bg-amber-100 text-amber-700 border-amber-200' },
  { value: 'hibrido', label: 'Híbrido', icon: Battery, color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  { value: 'off_grid', label: 'Off-Grid', icon: Zap, color: 'bg-blue-100 text-blue-700 border-blue-200' },
  { value: 'micro', label: 'Micro', icon: Cpu, color: 'bg-violet-100 text-violet-700 border-violet-200' },
]

export function Step4_Inversor() {
  const { draft, setDraft } = useOrcamentoDraft()
  const [inversores, setInversores] = useState<any[]>([])
  const [marcaFiltro, setMarcaFiltro] = useState('')
  const [busca, setBusca] = useState('')
  const [fasesFiltro, setFasesFiltro] = useState<number | ''>('')
  const [tensaoFiltro, setTensaoFiltro] = useState<number | ''>('')
  const [potMinFiltro, setPotMinFiltro] = useState<number | ''>(2)
  const [potMaxFiltro, setPotMaxFiltro] = useState<number | ''>(200)

  useEffect(() => { solarApi.inversores().then(setInversores).catch(() => {}) }, [])

  const marcas = useMemo(() => {
    let filtered = inversores
    if (draft.tipoInversor) filtered = filtered.filter(i => i.tipo === draft.tipoInversor)
    return [...new Set(filtered.map(i => i.marca))].sort()
  }, [inversores, draft.tipoInversor])

  const filtrados = useMemo(() => {
    let r = inversores
    if (draft.tipoInversor) r = r.filter(i => i.tipo === draft.tipoInversor)
    if (marcaFiltro) r = r.filter(i => i.marca === marcaFiltro)
    if (fasesFiltro) r = r.filter(i => i.fases === Number(fasesFiltro))
    if (tensaoFiltro) r = r.filter(i => i.tensao_saida_v === Number(tensaoFiltro))
    if (potMinFiltro) r = r.filter(i => i.potencia_kw >= Number(potMinFiltro))
    if (potMaxFiltro) r = r.filter(i => i.potencia_kw <= Number(potMaxFiltro))
    if (busca) { const t = busca.toLowerCase(); r = r.filter(i => i.marca.toLowerCase().includes(t) || i.modelo.toLowerCase().includes(t)) }
    return r
  }, [inversores, draft.tipoInversor, marcaFiltro, fasesFiltro, tensaoFiltro, potMinFiltro, potMaxFiltro, busca])

  const selectInversor = (inv: any) => {
    setDraft({
      inversorId: inv.id,
      inversorMarca: inv.marca,
      inversorModelo: inv.modelo,
      inversorPotencia: inv.potencia_kw,
    })
  }

  const canAdvance = !!draft.inversorId
  const fmt = (v: number) => v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

  return (
    <WizardLayout canAdvance={canAdvance}>
      <div className="space-y-5">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-zinc-900">Selecione o Inversor</h2>
          <p className="text-sm text-zinc-500 mt-1">Escolha o tipo, marca e modelo do inversor solar</p>
        </div>

        {/* Type cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {TIPOS.map(t => {
            const Icon = t.icon
            const active = draft.tipoInversor === t.value
            return (
              <button
                key={t.value}
                onClick={() => { setDraft({ tipoInversor: t.value }); setMarcaFiltro('') }}
                className={`p-4 rounded-xl border-2 text-center transition-all ${
                  active ? `${t.color} border-current shadow-md` : 'border-zinc-200 bg-white hover:border-zinc-300'
                }`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${active ? '' : 'text-zinc-400'}`} />
                <span className={`text-sm font-semibold ${active ? '' : 'text-zinc-600'}`}>{t.label}</span>
              </button>
            )
          })}
        </div>

        {/* Brand chips */}
        {marcas.length > 0 && (
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
        )}

        {/* Filters row */}
        <div className="flex gap-3 items-end flex-wrap">
          <div className="flex-1 min-w-[200px] relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={busca} onChange={e => setBusca(e.target.value)}
              className="form-input pl-9" placeholder="Buscar marca ou modelo..." />
          </div>
          <div className="w-20">
            <label className="form-label text-[10px]">Fases</label>
            <select value={fasesFiltro} onChange={e => setFasesFiltro(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs">
              <option value="">Todas</option>
              <option value="1">1ø</option>
              <option value="3">3ø</option>
            </select>
          </div>
          <div className="w-20">
            <label className="form-label text-[10px]">Tensão</label>
            <select value={tensaoFiltro} onChange={e => setTensaoFiltro(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs">
              <option value="">Todas</option>
              <option value="220">220V</option>
              <option value="380">380V</option>
            </select>
          </div>
          <div className="w-20">
            <label className="form-label text-[10px]">kW mín</label>
            <input type="number" value={potMinFiltro} onChange={e => setPotMinFiltro(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs" />
          </div>
          <div className="w-20">
            <label className="form-label text-[10px]">kW máx</label>
            <input type="number" value={potMaxFiltro} onChange={e => setPotMaxFiltro(e.target.value === '' ? '' : +e.target.value)} className="form-input h-9 text-xs" />
          </div>
        </div>

        {/* Results table */}
        <div className="text-xs text-zinc-400 mb-1">{filtrados.length} inversores encontrados</div>
        <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden max-h-[40vh] overflow-y-auto">
          <table className="gov-table text-xs">
            <thead className="sticky top-0 bg-zinc-50 z-10">
              <tr>
                <th className="w-6"></th>
                <th>Marca</th>
                <th>Modelo</th>
                <th className="text-right">kW</th>
                <th className="text-center">Fases</th>
                <th className="text-center">Tensão</th>
                <th className="text-center">MPPT</th>
                <th className="text-right">η%</th>
                <th className="text-center">Garantia</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map(inv => {
                const selected = draft.inversorId === inv.id
                return (
                  <tr
                    key={inv.id}
                    onClick={() => selectInversor(inv)}
                    className={`cursor-pointer transition-colors ${
                      selected ? 'bg-blue-50 border-l-2 border-blue-500' : 'hover:bg-zinc-50'
                    }`}
                  >
                    <td className="text-center">
                      <div className={`w-3.5 h-3.5 rounded-full border-2 ${
                        selected ? 'bg-blue-600 border-blue-600' : 'border-zinc-300'
                      }`} />
                    </td>
                    <td className="font-semibold text-zinc-800">{inv.marca}</td>
                    <td className="text-zinc-600">{inv.modelo}</td>
                    <td className="text-right font-bold text-zinc-900">{fmt(inv.potencia_kw)}</td>
                    <td className="text-center">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                        inv.fases === 1 ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                      }`}>{inv.fases}ø</span>
                    </td>
                    <td className="text-center text-zinc-500">{inv.tensao_saida_v}V</td>
                    <td className="text-center text-zinc-500">{inv.num_mppt}</td>
                    <td className="text-right text-emerald-600">{inv.eficiencia_max}%</td>
                    <td className="text-center text-zinc-500">{inv.garantia_anos}a</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Quantity */}
        {draft.inversorId && (
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200 flex items-center justify-between">
            <div>
              <p className="text-xs text-blue-600 font-semibold">Inversor selecionado</p>
              <p className="text-sm font-bold text-blue-900">{draft.inversorMarca} — {draft.inversorModelo} ({draft.inversorPotencia} kW)</p>
            </div>
            <div>
              <label className="form-label text-[10px] text-blue-600">Quantidade</label>
              <input
                type="number"
                value={draft.qtdInversores}
                onChange={e => setDraft({ qtdInversores: e.target.value === '' ? '' : +e.target.value })}
                min={1}
                className="form-input w-20 h-8 text-sm text-center"
              />
            </div>
          </div>
        )}
      </div>
    </WizardLayout>
  )
}
