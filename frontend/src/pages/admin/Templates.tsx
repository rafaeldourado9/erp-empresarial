import { useEffect, useRef, useState } from 'react'
import {
  FileText, Upload, Download, Trash2, Star, StarOff, Plus, AlertCircle, CheckCircle2, X,
} from 'lucide-react'
import { templatesApi, type TemplateItem } from '../../api/quotes'

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function Templates() {
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [nome, setNome] = useState('')
  const [descricao, setDescricao] = useState('')
  const [tornarPadrao, setTornarPadrao] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const carregar = () => {
    setLoading(true)
    templatesApi.listar()
      .then(setTemplates)
      .catch(() => setError('Erro ao carregar templates'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  const handleUpload = async () => {
    if (!nome.trim()) { setError('Informe um nome para o template'); return }
    if (!file) { setError('Selecione um arquivo .docx'); return }
    setError(null)
    setUploading(true)
    try {
      await templatesApi.criar(nome.trim(), file, descricao.trim() || undefined, tornarPadrao)
      setSuccess('Template cadastrado com sucesso!')
      setShowUpload(false)
      setNome('')
      setDescricao('')
      setFile(null)
      setTornarPadrao(false)
      carregar()
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Erro ao enviar template')
    } finally {
      setUploading(false)
    }
  }

  const handleDefinirPadrao = async (id: string) => {
    try {
      await templatesApi.definirPadrao(id)
      setSuccess('Template padrão definido!')
      carregar()
    } catch {
      setError('Erro ao definir template padrão')
    }
  }

  const handleDeletar = async (id: string, nome: string) => {
    if (!confirm(`Remover o template "${nome}"?`)) return
    try {
      await templatesApi.deletar(id)
      setSuccess('Template removido')
      carregar()
    } catch {
      setError('Erro ao remover template')
    }
  }

  const handleBaixar = async (id: string, nomeArq: string) => {
    try {
      const blob = await templatesApi.baixarOriginal(id)
      downloadBlob(blob, `${nomeArq.toLowerCase().replace(/\s+/g, '_')}.docx`)
    } catch {
      setError('Erro ao baixar template')
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Templates de Proposta</h1>
          <p className="text-sm text-gray-500 mt-1">
            Gerencie seus modelos .docx. As variáveis <code className="text-xs bg-gray-100 px-1 rounded">[cliente_nome]</code> serão preenchidas automaticamente.
          </p>
        </div>
        <button
          onClick={() => { setShowUpload(true); setError(null) }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Novo Template
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="flex items-center gap-2 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span className="flex-1">{error}</span>
          <button onClick={() => setError(null)}><X className="w-4 h-4" /></button>
        </div>
      )}
      {success && (
        <div className="flex items-center gap-2 mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span className="flex-1">{success}</span>
          <button onClick={() => setSuccess(null)}><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Upload modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="text-lg font-bold text-gray-900">Cadastrar Template</h2>
              <button onClick={() => setShowUpload(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="form-label">Nome do template *</label>
                <input
                  value={nome}
                  onChange={e => setNome(e.target.value)}
                  placeholder="Ex: Proposta Residencial"
                  className="form-input"
                />
              </div>
              <div>
                <label className="form-label">Descrição</label>
                <input
                  value={descricao}
                  onChange={e => setDescricao(e.target.value)}
                  placeholder="Descrição opcional"
                  className="form-input"
                />
              </div>

              {/* File drop zone */}
              <div>
                <label className="form-label">Arquivo .docx *</label>
                <div
                  onClick={() => fileRef.current?.click()}
                  onDragOver={e => e.preventDefault()}
                  onDrop={e => {
                    e.preventDefault()
                    const f = e.dataTransfer.files[0]
                    if (f?.name.endsWith('.docx')) setFile(f)
                    else setError('Apenas arquivos .docx são aceitos')
                  }}
                  className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-2 text-blue-700">
                      <FileText className="w-5 h-5" />
                      <span className="font-medium text-sm">{file.name}</span>
                      <button
                        onClick={e => { e.stopPropagation(); setFile(null) }}
                        className="text-gray-400 hover:text-red-500 ml-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="text-gray-500">
                      <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm font-medium">Clique ou arraste o arquivo aqui</p>
                      <p className="text-xs text-gray-400 mt-1">Apenas .docx com variáveis [entre_colchetes]</p>
                    </div>
                  )}
                </div>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".docx"
                  className="hidden"
                  onChange={e => setFile(e.target.files?.[0] ?? null)}
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={tornarPadrao}
                  onChange={e => setTornarPadrao(e.target.checked)}
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm text-gray-700">Definir como template padrão</span>
              </label>

              {error && <p className="text-sm text-red-600">{error}</p>}
            </div>
            <div className="flex gap-3 p-5 border-t">
              <button onClick={() => setShowUpload(false)} className="btn-secondary flex-1">Cancelar</button>
              <button onClick={handleUpload} disabled={uploading} className="btn-primary flex-1 flex items-center justify-center gap-2">
                {uploading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <Upload className="w-4 h-4" />}
                {uploading ? 'Enviando...' : 'Cadastrar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Template list */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <span className="animate-spin w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full mr-3" />
          Carregando templates...
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-200">
          <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <h3 className="font-semibold text-gray-700 mb-1">Nenhum template cadastrado</h3>
          <p className="text-sm text-gray-500 mb-4">
            Faça upload do seu arquivo .docx com as variáveis <code className="bg-gray-100 px-1 rounded">[cliente_nome]</code>
          </p>
          <button onClick={() => setShowUpload(true)} className="btn-primary inline-flex items-center gap-2">
            <Plus className="w-4 h-4" /> Cadastrar primeiro template
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {templates.map(tpl => (
            <div
              key={tpl.id}
              className={`bg-white rounded-xl border-2 p-5 flex items-center gap-4 transition-colors ${
                tpl.padrao ? 'border-blue-200 bg-blue-50/20' : 'border-gray-100 hover:border-gray-200'
              }`}
            >
              {/* Icon */}
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                tpl.padrao ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <FileText className={`w-6 h-6 ${tpl.padrao ? 'text-blue-600' : 'text-gray-400'}`} />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-semibold text-gray-900 truncate">{tpl.nome}</h3>
                  {tpl.padrao && (
                    <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                      <Star className="w-3 h-3" /> Padrão
                    </span>
                  )}
                </div>
                {tpl.descricao && (
                  <p className="text-sm text-gray-500 mt-0.5 truncate">{tpl.descricao}</p>
                )}
                <p className="text-xs text-gray-400 mt-1">Cadastrado em {formatDate(tpl.criado_em)}</p>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                {!tpl.padrao && (
                  <button
                    onClick={() => handleDefinirPadrao(tpl.id)}
                    title="Definir como padrão"
                    className="p-2 text-gray-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                  >
                    <StarOff className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleBaixar(tpl.id, tpl.nome)}
                  title="Baixar arquivo original"
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                </button>
                {!tpl.padrao && (
                  <button
                    onClick={() => handleDeletar(tpl.id, tpl.nome)}
                    title="Remover template"
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Variables reference */}
      <div className="mt-8 bg-gray-50 rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-gray-400" /> Variáveis disponíveis no template
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
          {[
            ['[proposta_identificador]', 'Número da proposta'],
            ['[cliente_nome]', 'Nome do cliente'],
            ['[cliente_cnpj_cpf]', 'CPF/CNPJ do cliente'],
            ['[cliente_endereco]', 'Endereço'],
            ['[cliente_bairro]', 'Bairro'],
            ['[cliente_cidade]', 'Cidade'],
            ['[cliente_estado]', 'Estado'],
            ['[cliente_complemento]', 'End. de instalação'],
            ['[consumo_mensal]', 'Consumo médio (kWh)'],
            ['[geracao_mensal]', 'Geração mensal (kWh)'],
            ['[potencia_sistema]', 'Potência do sistema (kWp)'],
            ['[area_util]', 'Área necessária (m²)'],
            ['[modulo_fabricante]', 'Fabricante do módulo'],
            ['[modulo_modelo]', 'Modelo do módulo'],
            ['[modulo_potencia]', 'Potência do módulo (W)'],
            ['[modulo_quantidade]', 'Quantidade de módulos'],
            ['[vc_modulo_eficiencia]', 'Eficiência do módulo (%)'],
            ['[inversor_fabricante]', 'Fabricante do inversor'],
            ['[inversor_potencia_nominal]', 'Potência do inversor (W)'],
            ['[inversores_utilizados]', 'Qtd. de inversores'],
            ['[cap_vendedorresp]', 'Consultor responsável'],
            ['[preco]', 'Valor da proposta'],
            ['[economia_mensal]', 'Economia mensal (R$)'],
            ['[economia_mensal_p]', 'Economia esperada (%)'],
            ['[inflacao_energetica]', 'Inflação energética (% a.a.)'],
            ['[perda_eficiencia_anual]', 'Perda de eficiência (% a.a.)'],
          ].map(([varName, label]) => (
            <div key={varName} className="flex items-start gap-2">
              <code className="text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded shrink-0">{varName}</code>
              <span className="text-gray-500">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
