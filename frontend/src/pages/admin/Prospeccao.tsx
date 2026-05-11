import { useEffect, useState } from 'react'
import { Plus, ChevronRight, Pencil, Trash2 } from 'lucide-react'
import { prospeccaoApi } from '../../api/prospecting'

const ETAPAS = ['Prospecção', 'Qualificação', 'Proposta', 'Negociação', 'Fechado', 'Perdido']

const etapaColor: Record<string, string> = {
  'Prospecção': 'bg-gray-100 text-gray-700',
  'Qualificação': 'bg-blue-100 text-blue-700',
  'Proposta': 'bg-purple-100 text-purple-700',
  'Negociação': 'bg-orange-100 text-orange-700',
  'Fechado': 'bg-green-100 text-green-700',
  'Perdido': 'bg-red-100 text-red-700',
}

const fmt = (v?: number | null) => v != null ? `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : '—'

export function Prospeccao() {
  const [leads, setLeads] = useState<any[]>([])
  const [etapaFiltro, setEtapaFiltro] = useState('')
  const [modal, setModal] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const carregar = () => {
    setLoading(true)
    const params: any = {}
    if (etapaFiltro) params.etapa = etapaFiltro
    prospeccaoApi.listar(params).then(setLeads).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [etapaFiltro])

  const salvar = async () => {
    if (modal.id) {
      await prospeccaoApi.atualizar(modal.id, modal)
    } else {
      await prospeccaoApi.criar(modal)
    }
    setModal(null)
    carregar()
  }

  const avancar = async (id: string) => {
    await prospeccaoApi.avancarEtapa(id)
    carregar()
  }

  const deletar = async (id: string) => {
    if (!confirm('Remover lead?')) return
    await prospeccaoApi.deletar(id)
    carregar()
  }

  const empty = { nome: '', empresa: '', contato: '', etapa: 'Prospecção', valor_estimado: '', observacoes: '' }

  const totalValor = leads.filter(l => l.etapa !== 'Perdido').reduce((s, l) => s + (l.valor_estimado ?? 0), 0)
  const totalFechado = leads.filter(l => l.etapa === 'Fechado').reduce((s, l) => s + (l.valor_estimado ?? 0), 0)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Prospecção / CRM</h1>
        <button onClick={() => setModal(empty)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> Novo Lead
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-xs text-gray-500">Pipeline total</p>
          <p className="text-xl font-bold text-gray-900">{fmt(totalValor)}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-xs text-gray-500">Fechados</p>
          <p className="text-xl font-bold text-green-600">{fmt(totalFechado)}</p>
        </div>
      </div>

      {/* Filtros por etapa */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button onClick={() => setEtapaFiltro('')}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${!etapaFiltro ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
          Todos
        </button>
        {ETAPAS.map(e => (
          <button key={e} onClick={() => setEtapaFiltro(e)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${etapaFiltro === e ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
            {e}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Lead</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Empresa</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Contato</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Etapa</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Valor Est.</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && leads.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhum lead cadastrado</td></tr>}
            {leads.map(l => (
              <tr key={l.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{l.nome}</td>
                <td className="px-4 py-3 text-gray-600">{l.empresa || '—'}</td>
                <td className="px-4 py-3 text-gray-600">{l.contato || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${etapaColor[l.etapa] ?? 'bg-gray-100 text-gray-600'}`}>
                    {l.etapa}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-700">{fmt(l.valor_estimado)}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    {!['Fechado', 'Perdido'].includes(l.etapa) && (
                      <button onClick={() => avancar(l.id)} title="Avançar etapa"
                        className="p-1 text-gray-400 hover:text-blue-600">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    )}
                    <button onClick={() => setModal({ ...l })} className="p-1 text-gray-400 hover:text-blue-600">
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button onClick={() => deletar(l.id)} className="p-1 text-gray-400 hover:text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">{modal.id ? 'Editar' : 'Novo'} Lead</h2>
            <div className="space-y-3">
              {[
                { k: 'nome', label: 'Nome / Oportunidade', required: true },
                { k: 'empresa', label: 'Empresa' },
                { k: 'contato', label: 'Contato' },
              ].map(({ k, label, required }) => (
                <div key={k}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}{required && ' *'}</label>
                  <input value={modal[k] ?? ''} onChange={e => setModal((m: any) => ({ ...m, [k]: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Etapa</label>
                <select value={modal.etapa} onChange={e => setModal((m: any) => ({ ...m, etapa: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  {ETAPAS.map(e => <option key={e}>{e}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Valor Estimado (R$)</label>
                <input type="number" min={0} step={0.01} value={modal.valor_estimado ?? ''}
                  onChange={e => setModal((m: any) => ({ ...m, valor_estimado: e.target.value ? +e.target.value : null }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
                <textarea value={modal.observacoes ?? ''} rows={2}
                  onChange={e => setModal((m: any) => ({ ...m, observacoes: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModal(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
