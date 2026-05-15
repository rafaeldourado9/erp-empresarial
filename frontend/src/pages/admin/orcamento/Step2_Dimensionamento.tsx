import { useMemo, useState } from 'react'
import { Calculator, Zap, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { useOrcamentoDraft } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'
import { calcularDimensionamento, recalcularOutraPlaca, verificarOverload } from '../../../lib/solar'

export function Step2_Dimensionamento() {
  const { draft, setDraft } = useOrcamentoDraft()
  const [showRecalc, setShowRecalc] = useState(false)
  const [novaPotencia, setNovaPotencia] = useState<number | ''>(620)
  const [invKw, setInvKw] = useState<number | ''>(draft.inversorPotencia ?? 5)

  const consumo = Number(draft.consumoMensal) || 0
  const potencia = Number(draft.potenciaPlaca) || 540

  const dim = useMemo(() => {
    if (!consumo || !potencia) return null
    return calcularDimensionamento({
      consumo_kwh_mes: consumo,
      potencia_placa_w: potencia,
      fator_regional: draft.fatorRegional,
    })
  }, [consumo, potencia, draft.fatorRegional])

  const recalc = useMemo(() => {
    if (!dim || !novaPotencia) return null
    return recalcularOutraPlaca(dim.kwp_sistema, Number(novaPotencia))
  }, [dim, novaPotencia])

  const overload = useMemo(() => {
    if (!dim || !invKw) return null
    return verificarOverload(Number(invKw), draft.fatorOverload, dim.kwp_sistema)
  }, [dim, invKw, draft.fatorOverload])

  const applyToDraft = () => {
    if (!dim) return
    setDraft({
      qtdPlacas: dim.qtd_placas,
      kwpSistema: dim.kwp_sistema,
      qtdModulos: dim.qtd_placas,
    })
  }

  const canAdvance = !!dim && dim.qtd_placas > 0

  const fmt = (v: number) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <WizardLayout canAdvance={canAdvance} onNext={() => { applyToDraft(); setDraft({ step: 3 }) }}>
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-zinc-900 flex items-center justify-center gap-2">
            <Calculator className="w-6 h-6 text-blue-600" /> Calculadora de Dimensionamento
          </h2>
          <p className="text-sm text-zinc-500 mt-1">Fórmulas conforme manual Nacional Energy</p>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="form-label">Consumo mensal (kWh/mês) *</label>
            <input
              type="number"
              value={draft.consumoMensal}
              onChange={e => setDraft({ consumoMensal: e.target.value === '' ? '' : +e.target.value })}
              min={0}
              placeholder="Ex: 600"
              className="form-input text-lg font-semibold"
            />
          </div>
          <div>
            <label className="form-label">Potência da placa (W) *</label>
            <input
              type="number"
              value={draft.potenciaPlaca}
              onChange={e => setDraft({ potenciaPlaca: e.target.value === '' ? '' : +e.target.value })}
              min={100}
              step={10}
              placeholder="Ex: 540"
              className="form-input text-lg font-semibold"
            />
          </div>
          <div>
            <label className="form-label">
              Fator regional
              <span className="text-zinc-400 ml-1">(UF: {draft.uf})</span>
            </label>
            <input
              type="number"
              value={draft.fatorRegional}
              onChange={e => setDraft({ fatorRegional: +e.target.value })}
              min={80}
              max={180}
              step={1}
              className="form-input"
            />
          </div>
        </div>

        {/* Result Cards */}
        {dim && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
              <p className="text-xs text-blue-600 font-semibold uppercase tracking-wide mb-1">Geração por placa</p>
              <p className="text-2xl font-bold text-blue-800">{fmt(dim.geracao_por_placa_kwh)} <span className="text-sm font-normal">kWh/mês</span></p>
              <p className="text-xs text-blue-500 mt-1">{potencia/1000} kW × {draft.fatorRegional}</p>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-5 border border-emerald-100">
              <p className="text-xs text-emerald-600 font-semibold uppercase tracking-wide mb-1">Quantidade de placas</p>
              <p className="text-2xl font-bold text-emerald-800">{dim.qtd_placas} <span className="text-sm font-normal">unidades</span></p>
              <p className="text-xs text-emerald-500 mt-1">⌈{consumo} ÷ {fmt(dim.geracao_por_placa_kwh)}⌉</p>
            </div>
            <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-100">
              <p className="text-xs text-violet-600 font-semibold uppercase tracking-wide mb-1">Potência do sistema</p>
              <p className="text-2xl font-bold text-violet-800">{fmt(dim.kwp_sistema)} <span className="text-sm font-normal">kWp</span></p>
              <p className="text-xs text-violet-500 mt-1">{dim.qtd_placas} × {potencia/1000} kW</p>
            </div>
          </div>
        )}

        {/* Recalcular com outra placa */}
        {dim && (
          <div className="bg-white rounded-xl border border-zinc-200 p-5">
            <button
              onClick={() => setShowRecalc(!showRecalc)}
              className="flex items-center gap-2 text-sm font-medium text-zinc-700 hover:text-blue-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Recalcular com outra placa
            </button>

            {showRecalc && (
              <div className="mt-4 flex items-end gap-4">
                <div className="flex-1">
                  <label className="form-label">Nova potência (W)</label>
                  <input
                    type="number"
                    value={novaPotencia}
                    onChange={e => setNovaPotencia(e.target.value === '' ? '' : +e.target.value)}
                    min={100}
                    step={10}
                    className="form-input"
                  />
                </div>
                {recalc && (
                  <div className="flex-1 bg-amber-50 rounded-lg p-3 border border-amber-100">
                    <p className="text-xs text-amber-700 font-medium">
                      Com {recalc.nova_potencia_w}W → <strong>{recalc.qtd_placas} placas</strong> ({fmt(recalc.kwp_sistema)} kWp)
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Overload check */}
        {dim && (
          <div className="bg-white rounded-xl border border-zinc-200 p-5">
            <h3 className="text-sm font-semibold text-zinc-700 mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" /> Verificação de Overload
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
              <div>
                <label className="form-label">Potência do inversor (kW)</label>
                <input
                  type="number"
                  value={invKw}
                  onChange={e => setInvKw(e.target.value === '' ? '' : +e.target.value)}
                  min={0}
                  step={0.5}
                  className="form-input"
                />
              </div>
              <div>
                <label className="form-label">Fator de overload</label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={1.0}
                    max={1.7}
                    step={0.05}
                    value={draft.fatorOverload}
                    onChange={e => setDraft({ fatorOverload: +e.target.value })}
                    className="flex-1 accent-blue-600"
                  />
                  <span className="text-sm font-mono font-semibold text-zinc-700 w-12 text-right">
                    {draft.fatorOverload.toFixed(2)}×
                  </span>
                </div>
              </div>
              {overload && (
                <div className={`rounded-lg p-3 text-sm font-medium flex items-start gap-2 ${
                  overload.status === 'ok'
                    ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
                    : 'bg-red-50 border border-red-200 text-red-700'
                }`}>
                  {overload.status === 'ok'
                    ? <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
                    : <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                  }
                  <div>
                    <p className="text-xs">{overload.mensagem}</p>
                    <p className="text-xs mt-0.5 opacity-70">Máx: {fmt(overload.overload_maximo_kwp)} kWp</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </WizardLayout>
  )
}
