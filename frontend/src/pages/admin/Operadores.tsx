import { useEffect, useState } from 'react'
import { Plus, Pencil, KeyRound, ToggleLeft, ToggleRight } from 'lucide-react'
import { operadoresApi } from '../../api/operators'

const PERFIS = ['ADMIN_EMPRESA', 'VENDEDOR', 'OPERADOR', 'CAIXA', 'FINANCEIRO']

const perfilLabel: Record<string, string> = {
  ADMIN_GRUPO: 'Admin Grupo',
  ADMIN_EMPRESA: 'Admin Empresa',
  VENDEDOR: 'Vendedor',
  OPERADOR: 'Operador',
  CAIXA: 'Caixa',
  FINANCEIRO: 'Financeiro',
}

export function Operadores() {
  const [operadores, setOperadores] = useState<any[]>([])
  const [modal, setModal] = useState<any>(null)
  const [modalSenha, setModalSenha] = useState<any>(null)
  const [novaSenha, setNovaSenha] = useState('')
  const [loading, setLoading] = useState(true)

  const carregar = () => {
    setLoading(true)
    operadoresApi.listar().then(setOperadores).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  const salvar = async () => {
    if (modal.id) {
      await operadoresApi.atualizar(modal.id, { nome: modal.nome, perfil: modal.perfil })
    } else {
      await operadoresApi.criar(modal)
    }
    setModal(null)
    carregar()
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

  const empty = { nome: '', email: '', perfil: 'OPERADOR', senha: '' }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Operadores</h1>
        <button onClick={() => setModal(empty)}
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
              <th className="text-left px-4 py-3 font-medium text-gray-600">Perfil</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && operadores.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhum operador cadastrado</td></tr>}
            {operadores.map(op => (
              <tr key={op.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{op.nome}</td>
                <td className="px-4 py-3 text-gray-600">{op.email}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                    {perfilLabel[op.perfil] ?? op.perfil}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${op.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {op.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => setModal({ ...op })} title="Editar"
                      className="p-1 text-gray-400 hover:text-blue-600">
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

      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="font-semibold text-lg mb-4">{modal.id ? 'Editar' : 'Novo'} Operador</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input value={modal.nome} onChange={e => setModal((m: any) => ({ ...m, nome: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              {!modal.id && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">E-mail *</label>
                    <input type="email" value={modal.email} onChange={e => setModal((m: any) => ({ ...m, email: e.target.value }))}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Senha inicial *</label>
                    <input type="password" value={modal.senha} onChange={e => setModal((m: any) => ({ ...m, senha: e.target.value }))}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                </>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Perfil</label>
                <select value={modal.perfil} onChange={e => setModal((m: any) => ({ ...m, perfil: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  {PERFIS.map(p => <option key={p} value={p}>{perfilLabel[p]}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setModal(null)} className="flex-1 border py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancelar</button>
              <button onClick={salvar} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">Salvar</button>
            </div>
          </div>
        </div>
      )}

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
