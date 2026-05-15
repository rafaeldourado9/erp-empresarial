import { ChevronLeft, ChevronRight, Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useOrcamentoDraft } from './hooks/useOrcamentoDraft'

const STEPS = [
  { n: 1, label: 'Cliente' },
  { n: 2, label: 'Dimensionamento' },
  { n: 3, label: 'Módulo' },
  { n: 4, label: 'Inversor' },
  { n: 5, label: 'Componentes' },
  { n: 6, label: 'Resumo' },
] as const

interface Props {
  children: React.ReactNode
  canAdvance?: boolean
  onNext?: () => void
  onBack?: () => void
}

export function WizardLayout({ children, canAdvance = true, onNext, onBack }: Props) {
  const { draft, setStep } = useOrcamentoDraft()
  const current = draft.step

  const goBack = () => {
    if (onBack) { onBack(); return }
    if (current > 1) setStep(current - 1)
  }

  const goNext = () => {
    if (onNext) { onNext(); return }
    if (current < 6 && canAdvance) setStep(current + 1)
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Stepper */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {STEPS.map((s, i) => {
            const done = current > s.n
            const active = current === s.n
            return (
              <div key={s.n} className="flex items-center flex-1 last:flex-none">
                {/* Node */}
                <button
                  onClick={() => s.n <= current && setStep(s.n)}
                  disabled={s.n > current}
                  className={`flex items-center justify-center w-9 h-9 rounded-full text-sm font-semibold shrink-0 transition-all duration-200 ${
                    done
                      ? 'bg-emerald-500 text-white shadow-md shadow-emerald-200'
                      : active
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 ring-4 ring-blue-100'
                        : 'bg-zinc-100 text-zinc-400 border border-zinc-200'
                  }`}
                >
                  {done ? <Check className="w-4 h-4" /> : s.n}
                </button>
                {/* Label under node */}
                <span className={`hidden sm:block ml-2 text-xs font-medium whitespace-nowrap ${
                  active ? 'text-blue-700' : done ? 'text-emerald-600' : 'text-zinc-400'
                }`}>
                  {s.label}
                </span>
                {/* Connector line */}
                {i < STEPS.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-3 rounded-full transition-colors ${
                    done ? 'bg-emerald-300' : 'bg-zinc-200'
                  }`} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Step content */}
      <div className="min-h-[60vh]">
        {children}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-8 pt-5 border-t border-zinc-200">
        <button
          onClick={goBack}
          disabled={current <= 1}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
            current <= 1
              ? 'text-zinc-300 cursor-not-allowed'
              : 'text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900'
          }`}
        >
          <ChevronLeft className="w-4 h-4" /> Voltar
        </button>

        {current < 6 ? (
          <button
            onClick={goNext}
            disabled={!canAdvance}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              canAdvance
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md shadow-blue-200'
                : 'bg-zinc-100 text-zinc-400 cursor-not-allowed'
            }`}
          >
            Avançar <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <div /> /* Step 6 has its own save button */
        )}
      </div>
    </div>
  )
}
