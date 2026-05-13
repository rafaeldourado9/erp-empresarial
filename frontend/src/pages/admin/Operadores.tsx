import { useEffect, useState } from 'react'
import { Plus, Pencil, KeyRound, ToggleLeft, ToggleRight, Phone, MapPin } from 'lucide-react'
import { operadoresApi } from '../../api/operators'

const PERFIS = ['ADMIN_EMPRESA', 'VENDEDOR', 'OPERADOR', 'CAIXA', 'FINANCEIRO'] as const

const perfilLabel: Record<string, string> = {
  ADMIN_GRUPO: 'Admin Grupo',
  ADMIN_EMPRESA: 'Admin',
  VENDEDOR: 'Vendedor',
  OPERADOR: 'Operador',
  CAIXA: 'Caixa',
  FINANCEIRO: 'Financeiro',
}

const perfilColor: Record<string, string> = {
  ADMIN_EMPRESA: 'bg-purple-100 text-purple-700',
  VENDEDOR: 'bg-green-100 text-green-700',
  OPERADOR: 'bg-blue-100 text-blue-700',
  CAIXA: 'bg-orange-100 text-orange-700',
  FINANCEIRO: 'bg-teal-100 text-teal-700',
  ADMIN_GRUPO: 'bg-red-100 text-red-700',
}

const TODAS_PERMISSOES = [
  { value: 'ver_dashboard', label: 'Ver Dashboard' },
  { value: 'ver_estoque', label: 'Ver Estoque' },
  { value: 'editar_estoque', label: 'Editar Estoque' },
  { value: 'ver_orcamentos', label: 'Ver Orçamentos' },
  { value: 'criar_orcamentos', label: 'Criar Orçamentos' },
  { value: 'aprovar_orcamentos', label: 'Aprovar Orçamentos' },
  { value: 'ver_clientes', label: 'Ver Clientes' },
  { value: 'editar_clientes', label: 'Editar Clientes' },
  { value: 'ver_financeiro', label: 'Ver Financeiro' },
  { value: 'lancar_financeiro', label: 'Lançar Financeiro' },
  { value: 'ver_comissoes', label: 'Ver Comissões' },
  { value: 'ver_auditoria', label: 'Ver Auditoria' },
  { value: 'usar_caixa', label: 'Usar Caixa' },
  { value: 'gerenciar_usuarios', label: 'Gerenciar Usuários' },
  { value: 'gerenciar_premissas', label: 'Gerenciar Premissas' },
  { value: 'configurar_sistema', label: 'Configurar Sistema' },
]

const PERMISSOES_POR_PERFIL: Record<string, string[]> = {
  VENDEDOR: ['ver_dashboard', 'ver_orcamentos', 'criar_orcamentos', 'ver_clientes', 'editar_clientes', 'ver_comissoes'],
  OPERADOR: ['ver_dashboard', 'ver_orcamentos', 'criar_orcamentos', 'ver_clientes', 'ver_estoque'],
  CAIXA: ['ver_dashboard', 'usar_caixa', 'ver_clientes'],
  FINANCEIRO: ['ver_dashboard', 'ver_financeiro', 'lancar_financeiro', 'ver_comissoes'],
  ADMIN_EMPRESA: TODAS_PERMISSOES.map(p => p.value),
}

const empty = {
  nome: '', email: '', perfil: 'OPERADOR', senha: '',
  permissoes: PERMISSOES_POR_PERFIL['OPERADOR'],
  comissao_percentual: 0,
  telefone: '', endereco: '',
}

export function Operadores() {
  const [operadores, setOperadores] = useState<any[]>([])
  const [modal, setModal] = useState<any>(null)
  const [modalSenha, setModalSenha] = useState<any>(null)
  const [novaSenha, setNovaSenha] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const carregar = () => {
    setLoading(true)
    operadoresApi.listar().then(setOperadores).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  const togglePermissao = (perm: string) => {
    setModal((m: any) => {
      const perms: string[] = m.permissoes ?? []
      return {
        ...m,
        permissoes: perms.includes(perm) ? perms.filter((p: string) => p !== perm) : [...perms, perm],
      }
    })
  }

  const aplicarPerfil = (perfil: string) => {
    setModal((m: any) => ({
      ...m,
      perfil,
      permissoes: PERMISSOES_POR_PERFIL[perfil] ?? [],
    }))
  }

  const salvar = async () => {
    if (saving) return
    setSaving(true)
    try {
      const payload = {
        nome: modal.nome,
        perfil: modal.perfil,
        permissoes: modal.permissoes ?? [],
        comissao_percentual: modal.comissao_percentual ?? 0,
        telefone: modal.telefone || null,
        endereco: modal.endereco || null,
        senha: modal.senha || undefined,
      }
      if (modal.id) {
        await operadoresApi.atualizar(modal.id, payload)
      } else {
        await operadoresApi.criar({ ...payload, email: modal.email, senha: modal.senha })
      }
      setModal(null)
      carregar()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const toggleAtivo = async (id: string) => {
    await operadoresApi.toggleAtivo(id)
    carregar()
  }

  const redefinirSenha = async () => {
    if (!novaSenha || novaSenha.length < 6) return alert('Senha deve ter ao menos 6 caracteres')
    await operadoresApi.redefinirSenha(modalSenha.id, novaSenha)
    setModalSenha(null)
    setNovaSenha('')
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Operadores</h1>
        <button onClick={() => setModal({ ...empty })}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> Novo Operador
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">E-mail</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Telefone</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Perfil</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Comissão</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={7} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && operadores.length === 0 && <tr><td colSpan={7} className="text-center py-8 text-gray-400">Nenhum operador cadastrado</td></tr>}
            {operadores.map(op => (
              <tr key={op.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{op.nome}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">{op.email}</td>
                <td className="px-4 py-3 text-gray-600 text-xs">{op.telefone || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${perfilColor[op.perfil?.toUpperCase()] ?? 'bg-gray-100 text-gray-600'}`}>
                    {perfilLabel[op.perfil?.toUpperCase()] ?? op.perfil}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600 text-sm">
                  {op.comissao_percentual > 0 ? `${op.comissao_percentual}%` : '—'}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${op.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {op.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => setModal({ ...op, permissoes: op.permissoes ?? [], senha: '', telefone: op.telefone ?? '', endereco: op.endereco ?? '' })}
                      title="Editar" className="p-1 text-gray-400 hover:text-blue-600">
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button onClick={() => { setModalSenha(op); setNovaSenha('') }} title="Redefinir senha"
                      className="p-1 text-gray-400 hover:text-orange-500">
                      <KeyRound className="w-4 h-4" />
                    </button>
                    <button onClick={() => toggleAtivo(op.id)} title={op.ativo ? 'Desativar' : 'Ativar'}
                      className={`p-1 ${op.ativo ? 'text-green-500 hover:text-gray-400' : 'text-gray-400 hover:text-green-500'}`}>
                      {op.ativo ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Modal Operador ── */}
      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto py-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl mx-4 my-auto">
            <h2 className="font-semibold text-lg mb-5">{modal.id ? 'Editar' : 'Novo'} Operador</h2>

            {/* Perfil — pill buttons */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Perfil</label>
              <div className="flex flex-wrap gap-2">
                {PERFIS.map(p => (
                  <button key={p} type="button"
                    onClick={() => aplicarPerfil(p)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                      modal.perfil?.toUpperCase() === p
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-600 border-gray-200 hover:border-blue-400 hover:text-blue-600'
                    }`}>
                    {perfilLabel[p]}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              {/* Nome */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modal.nome} onChange={e => setModal((m: any) => ({ ...m, nome: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nome completo" />
              </div>

              {/* E-mail + Senha (só na criação) */}
              {!modal.id ? (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">E-mail *</label>
                    <input type="email" value={modal.email} onChange={e => setModal((m: any) => ({ ...m, email: e.target.value }))}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="email@empresa.com" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Senha inicial *</label>
                    <input type="password" value={modal.senha} onChange={e => setModal((m: any) => ({ ...m, senha: e.target.value }))}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Mínimo 6 caracteres" />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nova senha <span className="text-gray-400 font-normal">(deixe em branco para manter)</span></label>
                  <input type="password" value={modal.senha} onChange={e => setModal((m: any) => ({ ...m, senha: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="••••••" />
                </div>
              )}

              {/* Telefone + Comissão */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Phone className="w-3.5 h-3.5 inline mr-1" />Telefone
                  </label>
                  <input value={modal.telefone ?? ''} onChange={e => setModal((m: any) => ({ ...m, telefone: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="(00) 00000-0000" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">% Comissão</label>
                  <input type="number" min={0} max={100} step={0.01}
                    value={modal.comissao_percentual ?? 0}
                    onChange={e => setModal((m: any) => ({ ...m, comissao_percentual: +e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>

              {/* Endereço */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="w-3.5 h-3.5 inline mr-1" />Endereço
                </label>
                <input value={modal.endereco ?? ''} onChange={e => setModal((m: any) => ({ ...m, endereco: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Rua, nº, bairro, cidade" />
              </div>

              {/* Permissões */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Permissões</label>
                <div className="grid grid-cols-2 gap-1.5 max-h-44 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                  {TODAS_PERMISSOES.map(perm => (
                    <label key={perm.value} className="flex items-center gap-2 cursor-pointer text-sm">
                      <input type="checkbox"
                        checked={(modal.permissoes ?? []).includes(perm.value)}
                        onChange={() => togglePermissao(perm.value)}
                        className="rounded" />
                      <span className="text-gray-700">{perm.label}</span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-1">{(modal.permissoes ?? []).length} permissão(ões) selecionada(s)</p>
              </div>
            </div>

            <div className="flex gap-2 mt-5">
              <button onClick={() => setModal(null)}
                className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} disabled={saving}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed">
                {saving ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Redefinir Senha ── */}
      {modalSenha && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="font-semibold text-lg mb-1">Redefinir Senha</h2>
            <p className="text-sm text-gray-500 mb-4">{modalSenha.nome}</p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nova senha</label>
              <input type="password" value={novaSenha} onChange={e => setNovaSenha(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModalSenha(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={redefinirSenha} className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-lg text-sm font-medium">Redefinir</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
