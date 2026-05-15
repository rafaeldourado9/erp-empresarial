import { useEffect, useState } from 'react'
import { User, MapPin } from 'lucide-react'
import { clientesApi } from '../../../api/clients'
import { operadoresApi } from '../../../api/operators'
import { solarApi } from '../../../api/solar'
import { useOrcamentoDraft } from './hooks/useOrcamentoDraft'
import { WizardLayout } from './WizardLayout'

export function Step1_Cliente() {
  const { draft, setDraft } = useOrcamentoDraft()
  const [clientes, setClientes] = useState<any[]>([])
  const [vendedores, setVendedores] = useState<any[]>([])
  const [estados, setEstados] = useState<any[]>([])

  useEffect(() => {
    clientesApi.listar().then(setClientes).catch(() => {})
    operadoresApi.listar().then((ops: any[]) =>
      setVendedores(ops.filter(o => o.perfil?.toLowerCase() === 'vendedor' && o.ativo))
    ).catch(() => {})
    solarApi.estados().then(setEstados).catch(() => {})
  }, [])

  const canAdvance = !!draft.titulo.trim()

  return (
    <WizardLayout canAdvance={canAdvance}>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-zinc-900">Dados do Orçamento</h2>
          <p className="text-sm text-zinc-500 mt-1">Identifique o cliente, vendedor e localização do projeto</p>
        </div>

        {/* Título */}
        <div>
          <label className="form-label">Título do Orçamento *</label>
          <input
            value={draft.titulo}
            onChange={e => setDraft({ titulo: e.target.value })}
            className="form-input text-lg"
            placeholder="Ex: Sistema Solar 5.4 kWp – João Silva"
          />
        </div>

        {/* Cliente + Vendedor */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="form-label flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-zinc-400" /> Cliente
            </label>
            <select
              value={draft.clienteId}
              onChange={e => setDraft({ clienteId: e.target.value })}
              className="form-input"
            >
              <option value="">Sem cliente vinculado</option>
              {clientes.map((c: any) => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          </div>
          <div>
            <label className="form-label">Vendedor</label>
            <select
              value={draft.vendedorId}
              onChange={e => setDraft({ vendedorId: e.target.value })}
              className="form-input"
            >
              <option value="">Sem vendedor</option>
              {vendedores.map((v: any) => <option key={v.id} value={v.id}>{v.nome}</option>)}
            </select>
          </div>
        </div>

        {/* Localização */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="form-label flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-zinc-400" /> Estado (UF)
            </label>
            <select
              value={draft.uf}
              onChange={e => {
                const est = estados.find((s: any) => s.uf === e.target.value)
                setDraft({
                  uf: e.target.value,
                  fatorRegional: est ? Math.round(est.fator_geracao * 30 * 0.75 * (1000/540) * (540/1000)) : 126,
                })
              }}
              className="form-input"
            >
              {estados.length > 0
                ? estados.map((s: any) => <option key={s.uf} value={s.uf}>{s.uf} — {s.nome}</option>)
                : <option value="SP">SP — São Paulo</option>
              }
            </select>
          </div>
          <div>
            <label className="form-label">Cidade</label>
            <input
              value={draft.cidade}
              onChange={e => setDraft({ cidade: e.target.value })}
              className="form-input"
              placeholder="Ex: Campinas"
            />
          </div>
        </div>

        {/* Validade + Obs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="form-label">Validade (dias)</label>
            <input
              type="number"
              value={draft.validadeDias}
              onChange={e => setDraft({ validadeDias: +e.target.value })}
              min={1}
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">Observações</label>
            <input
              value={draft.observacoes}
              onChange={e => setDraft({ observacoes: e.target.value })}
              className="form-input"
              placeholder="Notas internas"
            />
          </div>
        </div>
      </div>
    </WizardLayout>
  )
}
