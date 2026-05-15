import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { OrcamentoDraftProvider, useOrcamentoDraft } from './hooks/useOrcamentoDraft'
import { Step1_Cliente } from './Step1_Cliente'
import { Step2_Dimensionamento } from './Step2_Dimensionamento'
import { Step3_Modulo } from './Step3_Modulo'
import { Step4_Inversor } from './Step4_Inversor'
import { Step5_Componentes } from './Step5_Componentes'
import { Step6_Resumo } from './Step6_Resumo'
import { orcamentosApi } from '../../../api/quotes'

function WizardRouter() {
  const { id } = useParams()
  const { draft, loadFromOrcamento, resetDraft } = useOrcamentoDraft()

  // Reset draft when starting a new orcamento; load existing when editing.
  useEffect(() => {
    if (id) {
      orcamentosApi.obter(id).then(loadFromOrcamento).catch(() => {})
    } else {
      resetDraft()
    }
  }, [id, loadFromOrcamento, resetDraft])

  switch (draft.step) {
    case 1: return <Step1_Cliente />
    case 2: return <Step2_Dimensionamento />
    case 3: return <Step3_Modulo />
    case 4: return <Step4_Inversor />
    case 5: return <Step5_Componentes />
    case 6: return <Step6_Resumo />
    default: return <Step1_Cliente />
  }
}

/**
 * Get current userId from localStorage JWT token (matching existing auth pattern).
 */
function getUserIdFromToken(): string | undefined {
  try {
    const token = localStorage.getItem('token')
    if (!token) return undefined
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || payload.user_id || undefined
  } catch {
    return undefined
  }
}

export function OrcamentoWizard() {
  const userId = getUserIdFromToken()

  return (
    <OrcamentoDraftProvider userId={userId}>
      <WizardRouter />
    </OrcamentoDraftProvider>
  )
}
