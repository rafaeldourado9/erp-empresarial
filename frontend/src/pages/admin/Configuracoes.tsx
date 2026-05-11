import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Save } from 'lucide-react'
import { premissasApi, configEmpresaApi } from '../../api/settings'

export function Configuracoes() {
  const [aba, setAba] = useState<'premissas' | 'empresa'>('premissas')
  const [premissas, setPremissas] = useState<any[]>([])
  const [modalPremissa, setModalPremissa] = useState<any>(null)
  const [loadingPremissas, setLoadingPremissas] = useState(true)
  const [config, setConfig] = useState<any>({})
  const [savingConfig, setSavingConfig] = useState(false)

  const carregarPremissas = () => {
    setLoadingPremissas(true)
    premissasApi.listar().then(setPremissas).finally(() => setLoadingPremissas(false))
  }

  const carregarConfig = () => {
    configEmpresaApi.obter().then(setConfig).catch(() => setConfig({}))
  }

  useEffect(() => {
    carregarPremissas()
    carregarConfig()
  }, [])

  const salvarPremissa = async () => {
    if (modalPremissa.id) {
      await premissasApi.atualizar(modalPremissa.id, modalPremissa)
    } else {
      await premissasApi.criar(modalPremissa)
    }
    setModalPremissa(null)
    carregarPremissas()
  }

  const deletarPremissa = async (id: string) => {
    if (!confirm('Remover premissa? Orçamentos que a usam não serão afetados.')) return
    await premissasApi.deletar(id)
    carregarPremissas()
  }

  const salvarConfig = async () => {
    setSavingConfig(true)
    try {
      await configEmpresaApi.atualizar(config)
    } finally {
      setSavingConfig(false)
    }
  }

  const emptyPremissa = { nome: '', descricao: '', valor: 0, tipo: 'percentual' }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Configurações</h1>

      <div className="flex gap-2 mb-6">
        {[
          { v: 'premissas', label: 'Premissas de Custo' },
          { v: 'empresa', label: 'Dados da Empresa' },
        ].map(t => (
          <button key={t.v} onClick={() => setAba(t.v as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${aba === t.v ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {aba === 'premissas' && (
        <>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-semibold text-gray-800">Premissas de Custo</h2>
              <p className="text-sm text-gray-500 mt-0.5">Percentuais fixos usados nos orçamentos (impostos, margem, etc.)</p>
            </div>
            <button onClick={() => setModalPremissa(emptyPremissa)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              <Plus className="w-4 h-4" /> Nova Premissa
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Valor</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {loadingPremissas && <tr><td colSpan={4} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
                {!loadingPremissas && premissas.length === 0 && <tr><td colSpan={4} className="text-center py-8 text-gray-400">Nenhuma premissa cadastrada</td></tr>}
                {premissas.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-800">{p.nome}</td>
                    <td className="px-4 py-3 text-gray-600">{p.descricao || '—'}</td>
                    <td className="px-4 py-3 text-gray-700 font-medium">{p.valor}%</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => setModalPremissa({ ...p })} className="p-1 text-gray-400 hover:text-blue-600">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={() => deletarPremissa(p.id)} className="p-1 text-gray-400 hover:text-red-600">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {aba === 'empresa' && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 max-w-lg">
          <h2 className="font-semibold text-gray-800 mb-4">Dados da Empresa</h2>
          <div className="space-y-3">
            {[
              { k: 'nome_fantasia', label: 'Nome Fantasia' },
              { k: 'razao_social', label: 'Razão Social' },
              { k: 'cnpj', label: 'CNPJ' },
              { k: 'telefone', label: 'Telefone' },
              { k: 'email', label: 'E-mail' },
              { k: 'endereco', label: 'Endereço' },
              { k: 'logo_url', label: 'URL do Logo' },
            ].map(({ k, label }) => (
              <div key={k}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input value={config[k] ?? ''}
                  onChange={e => setConfig((c: any) => ({ ...c, [k]: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            ))}
          </div>
          <button onClick={salvarConfig} disabled={savingConfig}
            className="flex items-center gap-2 mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50">
            <Save className="w-4 h-4" /> {savingConfig ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      )}

      {modalPremissa && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">{modalPremissa.id ? 'Editar' : 'Nova'} Premissa</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modalPremissa.nome}
                  onChange={e => setModalPremissa((m: any) => ({ ...m, nome: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Imposto, Margem, Frete..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                <input value={modalPremissa.descricao ?? ''}
                  onChange={e => setModalPremissa((m: any) => ({ ...m, descricao: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Percentual (%)</label>
                <input type="number" min={0} max={100} step={0.01} value={modalPremissa.valor}
                  onChange={e => setModalPremissa((m: any) => ({ ...m, valor: +e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalPremissa(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvarPremissa} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
