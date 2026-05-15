import { useEffect, useRef, useState } from 'react'
import { Lock, Pencil, Plus, Save, Trash2, Upload, Download } from 'lucide-react'
import { premissasApi, configEmpresaApi, variaveisApi } from '../../api/settings'
import { orcamentosApi } from '../../api/quotes'

type Aba = 'premissas' | 'empresa' | 'templates'

const GRUPOS_ORDEM = [
  'Identificação', 'Empresa', 'Cliente', 'Vendedor', 'Financeiro',
  'Dimensionamento Solar', 'Módulo Solar', 'Inversor', 'Análise Financeira', 'Personalizado',
]

export function Configuracoes() {
  const [aba, setAba] = useState<Aba>('premissas')

  // ── Premissas ────────────────────────────────────────────────────────────────
  const [premissas, setPremissas] = useState<any[]>([])
  const [modalPremissa, setModalPremissa] = useState<any>(null)
  const [loadingPremissas, setLoadingPremissas] = useState(true)

  // ── Empresa ──────────────────────────────────────────────────────────────────
  const [config, setConfig] = useState<any>({})
  const [savingConfig, setSavingConfig] = useState(false)

  // ── Templates & Variáveis ────────────────────────────────────────────────────
  const [varSistema, setVarSistema] = useState<{ chave: string; label: string; grupo: string }[]>([])
  const [varCustom, setVarCustom] = useState<{ id: string; chave: string; label: string; grupo: string }[]>([])
  const [loadingVars, setLoadingVars] = useState(false)
  const [modalVar, setModalVar] = useState<any>(null)
  const [uploadingTemplate, setUploadingTemplate] = useState(false)
  const [templateOk, setTemplateOk] = useState<boolean | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const carregarPremissas = () => {
    setLoadingPremissas(true)
    premissasApi.listar().then(setPremissas).finally(() => setLoadingPremissas(false))
  }

  const carregarConfig = () => {
    configEmpresaApi.obter().then(setConfig).catch(() => setConfig({}))
  }

  const carregarVarveis = () => {
    setLoadingVars(true)
    variaveisApi.listar()
      .then(d => { setVarSistema(d.sistema); setVarCustom(d.personalizadas) })
      .finally(() => setLoadingVars(false))
  }

  useEffect(() => {
    carregarPremissas()
    carregarConfig()
  }, [])

  useEffect(() => {
    if (aba === 'templates') carregarVarveis()
  }, [aba])

  // ── Premissas handlers ────────────────────────────────────────────────────────
  const salvarPremissa = async () => {
    try {
      if (modalPremissa.id) {
        await premissasApi.atualizar(modalPremissa.id, modalPremissa)
      } else {
        await premissasApi.criar(modalPremissa)
      }
      setModalPremissa(null)
      carregarPremissas()
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar premissa')
    }
  }

  const deletarPremissa = async (id: string) => {
    if (!confirm('Remover premissa? Orçamentos que a usam não serão afetados.')) return
    try {
      await premissasApi.deletar(id)
      carregarPremissas()
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao remover premissa')
    }
  }

  const salvarConfig = async () => {
    setSavingConfig(true)
    try { await configEmpresaApi.atualizar(config) } finally { setSavingConfig(false) }
  }

  // ── Template handlers ─────────────────────────────────────────────────────────
  const handleUploadTemplate = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadingTemplate(true)
    try {
      await orcamentosApi.uploadTemplate(file)
      setTemplateOk(true)
      alert('Template enviado com sucesso!')
    } catch {
      alert('Erro ao enviar template.')
    } finally {
      setUploadingTemplate(false)
      e.target.value = ''
    }
  }

  const handleBaixarModelo = async () => {
    try {
      const blob = await orcamentosApi.baixarTemplateExemplo()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'modelo-proposta-comercial.docx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch {
      alert('Erro ao baixar modelo')
    }
  }

  // ── Variáveis handlers ────────────────────────────────────────────────────────
  const salvarVar = async () => {
    try {
      if (modalVar.id) {
        await variaveisApi.atualizar(modalVar.id, modalVar)
      } else {
        await variaveisApi.criar(modalVar)
      }
      setModalVar(null)
      carregarVarveis()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar variável')
    }
  }

  const deletarVar = async (id: string) => {
    if (!confirm('Remover variável personalizada?')) return
    await variaveisApi.deletar(id)
    carregarVarveis()
  }

  // Agrupa variáveis por grupo
  const gruposCustom = varCustom.reduce<Record<string, typeof varCustom>>((acc, v) => {
    ;(acc[v.grupo] ||= []).push(v)
    return acc
  }, {})

  const gruposSistema = varSistema.reduce<Record<string, typeof varSistema>>((acc, v) => {
    ;(acc[v.grupo] ||= []).push(v)
    return acc
  }, {})

  const emptyPremissa = { nome: '', descricao: '', valor: 0, tipo: 'percentual' }
  const emptyVar = { chave: '', label: '', grupo: 'Personalizado' }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Configurações</h1>

      <div className="flex gap-2 mb-6">
        {([
          { v: 'premissas', label: 'Premissas de Custo' },
          { v: 'empresa', label: 'Dados da Empresa' },
          { v: 'templates', label: 'Templates & Variáveis' },
        ] as { v: Aba; label: string }[]).map(t => (
          <button key={t.v} onClick={() => setAba(t.v)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${aba === t.v ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Premissas ── */}
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
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Obrigatória</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {loadingPremissas && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
                {!loadingPremissas && premissas.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhuma premissa cadastrada</td></tr>}
                {premissas.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-800">{p.nome}</td>
                    <td className="px-4 py-3 text-gray-600">{p.descricao || '—'}</td>
                    <td className="px-4 py-3 text-gray-700 font-medium">{p.valor}%</td>
                    <td className="px-4 py-3">
                      {p.obrigatoria
                        ? <span className="badge-amber"><Lock className="w-3 h-3" /> Obrigatória</span>
                        : <span className="text-xs text-gray-400">—</span>}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => setModalPremissa({ ...p })} className="p-1 text-gray-400 hover:text-blue-600"><Pencil className="w-4 h-4" /></button>
                        <button onClick={() => deletarPremissa(p.id)} className="p-1 text-gray-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* ── Empresa ── */}
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

      {/* ── Templates & Variáveis ── */}
      {aba === 'templates' && (
        <div className="space-y-6">

          {/* Upload de template */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="font-semibold text-gray-800 mb-1">Template de Proposta (.docx)</h2>
            <p className="text-sm text-gray-500 mb-4">
              Faça upload do seu arquivo Word com as variáveis no formato <code className="bg-gray-100 px-1 rounded text-xs">{`{{VARIAVEL}}`}</code> ou <code className="bg-gray-100 px-1 rounded text-xs">[variavel]</code>. O template configurado será usado ao gerar propostas em todos os orçamentos.
            </p>
            <div className="flex gap-3 flex-wrap">
              <input ref={fileInputRef} type="file" accept=".docx" className="hidden" onChange={handleUploadTemplate} />
              <button onClick={() => fileInputRef.current?.click()} disabled={uploadingTemplate}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50">
                <Upload className="w-4 h-4" />
                {uploadingTemplate ? 'Enviando...' : 'Enviar Template (.docx)'}
              </button>
              <button onClick={handleBaixarModelo}
                className="flex items-center gap-2 border text-gray-600 hover:bg-gray-50 px-4 py-2 rounded-lg text-sm font-medium">
                <Download className="w-4 h-4" /> Baixar Modelo de Exemplo
              </button>
            </div>
            {templateOk && (
              <p className="mt-3 text-sm text-green-600 font-medium">Template enviado com sucesso.</p>
            )}
          </div>

          {/* Variáveis personalizadas */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-1">
              <div>
                <h2 className="font-semibold text-gray-800">Variáveis Personalizadas</h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  Crie variáveis extras que aparecerão nos orçamentos e no template.
                  Use <code className="bg-gray-100 px-1 rounded text-xs">{`{{CHAVE}}`}</code> no Word.
                </p>
              </div>
              <button onClick={() => setModalVar({ ...emptyVar })}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
                <Plus className="w-4 h-4" /> Nova Variável
              </button>
            </div>

            {loadingVars ? (
              <p className="text-center py-8 text-gray-400 text-sm">Carregando...</p>
            ) : (
              <>
                {varCustom.length === 0 && (
                  <p className="text-center py-6 text-gray-400 text-sm">Nenhuma variável personalizada criada ainda.</p>
                )}
                {Object.entries(gruposCustom).map(([grupo, vars]) => (
                  <div key={grupo} className="mt-4">
                    <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-2">{grupo}</p>
                    <table className="w-full text-sm">
                      <tbody className="divide-y divide-gray-100">
                        {vars.map(v => (
                          <tr key={v.id} className="hover:bg-gray-50">
                            <td className="py-2 pr-4 w-48">
                              <code className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">{`{{${v.chave.toUpperCase()}}}`}</code>
                            </td>
                            <td className="py-2 text-gray-700">{v.label}</td>
                            <td className="py-2 w-20">
                              <div className="flex gap-1 justify-end">
                                <button onClick={() => setModalVar({ ...v })} className="p-1 text-gray-400 hover:text-blue-600"><Pencil className="w-3.5 h-3.5" /></button>
                                <button onClick={() => deletarVar(v.id)} className="p-1 text-gray-400 hover:text-red-600"><Trash2 className="w-3.5 h-3.5" /></button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </>
            )}
          </div>

          {/* Referência: variáveis do sistema */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="font-semibold text-gray-800 mb-1">Variáveis do Sistema</h2>
            <p className="text-sm text-gray-500 mb-4">
              Preenchidas automaticamente. Use <code className="bg-gray-100 px-1 rounded text-xs">{`{{CHAVE}}`}</code> ou <code className="bg-gray-100 px-1 rounded text-xs">[chave_minuscula]</code> no template.
            </p>
            <div className="space-y-4">
              {GRUPOS_ORDEM.filter(g => gruposSistema[g]).map(grupo => (
                <div key={grupo}>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1">
                    <Lock className="w-3 h-3" /> {grupo}
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                    {gruposSistema[grupo].map(v => (
                      <div key={v.chave} className="flex items-center gap-2 py-1">
                        <code className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded shrink-0">{`{{${v.chave}}}`}</code>
                        <span className="text-xs text-gray-500 truncate">{v.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Premissa ── */}
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
              <label className="flex items-start gap-2 cursor-pointer p-3 rounded-lg border border-amber-200 bg-amber-50 hover:bg-amber-100 transition-colors">
                <input
                  type="checkbox"
                  checked={!!modalPremissa.obrigatoria}
                  onChange={e => setModalPremissa((m: any) => ({ ...m, obrigatoria: e.target.checked }))}
                  className="mt-0.5 w-4 h-4 accent-amber-500"
                />
                <div className="text-xs">
                  <p className="font-semibold text-amber-800">Marcar como obrigatória</p>
                  <p className="text-amber-700 mt-0.5">
                    Será aplicada automaticamente em todos os orçamentos novos e o operador não poderá removê-la. Somente admins podem alterar essa flag.
                  </p>
                </div>
              </label>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalPremissa(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvarPremissa} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Variável ── */}
      {modalVar && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-4">{modalVar.id ? 'Editar' : 'Nova'} Variável</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Chave *</label>
                <input value={modalVar.chave} disabled={!!modalVar.id}
                  onChange={e => setModalVar((m: any) => ({ ...m, chave: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_') }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400 font-mono"
                  placeholder="ex: campo_bancario" />
                {!modalVar.id && (
                  <p className="text-xs text-gray-400 mt-1">
                    No template use: <code className="bg-gray-100 px-1 rounded">{`{{${(modalVar.chave || 'CHAVE').toUpperCase()}}}`}</code>
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome / Descrição *</label>
                <input value={modalVar.label}
                  onChange={e => setModalVar((m: any) => ({ ...m, label: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Campo Bancário, Garantia..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Grupo</label>
                <input value={modalVar.grupo}
                  onChange={e => setModalVar((m: any) => ({ ...m, grupo: e.target.value }))}
                  list="grupos-list"
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Personalizado" />
                <datalist id="grupos-list">
                  {['Personalizado', 'Financeiro', 'Dimensionamento Solar', 'Módulo Solar', 'Inversor', 'Análise Financeira', 'Cliente'].map(g => (
                    <option key={g} value={g} />
                  ))}
                </datalist>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalVar(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvarVar} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
