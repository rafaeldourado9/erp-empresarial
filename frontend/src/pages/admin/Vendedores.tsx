import { useEffect, useState } from 'react'
import { Plus, Pencil, KeyRound, ToggleLeft, ToggleRight, X, Award } from 'lucide-react'
import { operadoresApi } from '../../api/operators'
import { comissoesApi } from '../../api/commissions'

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`

export function Vendedores() {
  const [vendedores, setVendedores] = useState<any[]>([])
  const [comissoes, setComissoes] = useState<any[]>([])
  const [modal, setModal] = useState<any>(null)
  const [modalSenha, setModalSenha] = useState<any>(null)
  const [novaSenha, setNovaSenha] = useState('')
  const [loading, setLoading] = useState(true)

  const carregar = () => {
    setLoading(true)
    Promise.all([
      operadoresApi.listar(),
      comissoesApi.listar({ status: 'pendente' }),
    ]).then(([ops, cms]) => {
      setVendedores(ops.filter((o: any) => o.perfil?.toUpperCase() === 'VENDEDOR'))
      setComissoes(cms)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  const pendentePor = (id: string) =>
    comissoes
      .filter((c: any) => c.vendedor_id === id)
      .reduce((s: number, c: any) => s + c.valor_comissao, 0)

  const salvar = async () => {
    try {
      if (modal.id) {
        await operadoresApi.atualizar(modal.id, {
          nome: modal.nome,
          perfil: 'VENDEDOR',
          permissoes: modal.permissoes ?? [],
          comissao_percentual: modal.comissao_percentual ?? 0,
        })
      } else {
        await operadoresApi.criar({
          nome: modal.nome,
          email: modal.email,
          senha: modal.senha,
          perfil: 'VENDEDOR',
          permissoes: ['ver_dashboard', 'ver_orcamentos', 'criar_orcamentos', 'ver_clientes', 'editar_clientes', 'ver_comissoes'],
          comissao_percentual: modal.comissao_percentual ?? 0,
        })
      }
      setModal(null)
      carregar()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
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

  const emptyVendedor = { nome: '', email: '', senha: '', comissao_percentual: 0, permissoes: [] }
  const totalPendente = comissoes.reduce((s: number, c: any) => s + c.valor_comissao, 0)

  return (
    <div className="p-6">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vendedores</h1>
          <p className="text-sm text-gray-500 mt-1">{vendedores.length} vendedor(es) cadastrado(s)</p>
        </div>
        <button onClick={() => setModal(emptyVendedor)} className="btn-primary">
          <Plus className="w-4 h-4" /> Novo Vendedor
        </button>
      </div>

      {totalPendente > 0 && (
        <div className="flex items-center gap-3 p-4 mb-5 rounded-xl border border-yellow-200 bg-yellow-50">
          <Award className="w-4 h-4 text-yellow-600 shrink-0" />
          <p className="text-sm text-yellow-700 font-medium">
            {fmt(totalPendente)} em comissões pendentes de pagamento
          </p>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-100">
          <span className="text-sm font-semibold text-gray-800">Equipe de Vendas</span>
        </div>
        <div className="overflow-x-auto">
          <table className="gov-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>% Comissão</th>
                <th>Comissão Pendente</th>
                <th>Status</th>
                <th style={{ width: 100 }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={6} className="text-center py-10 text-gray-400">Carregando...</td></tr>
              )}
              {!loading && vendedores.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-gray-400">
                    Nenhum vendedor cadastrado
                    <p className="text-xs mt-1 text-gray-300">Clique em "Novo Vendedor" para adicionar</p>
                  </td>
                </tr>
              )}
              {vendedores.map(v => (
                <tr key={v.id}>
                  <td className="font-medium">{v.nome}</td>
                  <td className="text-gray-500">{v.email}</td>
                  <td>
                    <span className="badge-blue" style={{ fontVariantNumeric: 'tabular-nums' }}>
                      {v.comissao_percentual ?? 0}%
                    </span>
                  </td>
                  <td style={{ fontVariantNumeric: 'tabular-nums' }}>
                    {pendentePor(v.id) > 0
                      ? <span className="text-yellow-600 font-medium">{fmt(pendentePor(v.id))}</span>
                      : <span className="text-gray-400">—</span>
                    }
                  </td>
                  <td>
                    <span className={v.ativo ? 'badge-green' : 'badge-gray'}>
                      {v.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-1">
                      <button onClick={() => setModal({ ...v, senha: '' })} title="Editar"
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => { setModalSenha(v); setNovaSenha('') }} title="Redefinir senha"
                        className="p-1.5 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded transition-colors">
                        <KeyRound className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => toggleAtivo(v.id)} title={v.ativo ? 'Desativar' : 'Ativar'}
                        className={`p-1.5 rounded transition-colors ${v.ativo ? 'text-green-600 hover:bg-green-50' : 'text-gray-400 hover:text-green-600 hover:bg-green-50'}`}>
                        {v.ativo ? <ToggleRight className="w-3.5 h-3.5" /> : <ToggleLeft className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Vendedor */}
      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-sm mx-4 rounded-xl border border-gray-200 shadow-xl">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <h2 className="text-base font-semibold text-gray-900">
                {modal.id ? 'Editar Vendedor' : 'Novo Vendedor'}
              </h2>
              <button onClick={() => setModal(null)} className="p-1 text-gray-400 hover:text-gray-700 rounded">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="px-5 py-4 space-y-3">
              <div>
                <label className="form-label">Nome *</label>
                <input value={modal.nome}
                  onChange={e => setModal((m: any) => ({ ...m, nome: e.target.value }))}
                  className="form-input" placeholder="Nome completo" />
              </div>
              {!modal.id && (
                <>
                  <div>
                    <label className="form-label">E-mail *</label>
                    <input type="email" value={modal.email}
                      onChange={e => setModal((m: any) => ({ ...m, email: e.target.value }))}
                      className="form-input" />
                  </div>
                  <div>
                    <label className="form-label">Senha inicial *</label>
                    <input type="password" value={modal.senha}
                      onChange={e => setModal((m: any) => ({ ...m, senha: e.target.value }))}
                      className="form-input" />
                  </div>
                </>
              )}
              <div>
                <label className="form-label">% de Comissão sobre Venda Aprovada</label>
                <div className="flex items-center gap-2">
                  <input type="number" min={0} max={100} step={0.1}
                    value={modal.comissao_percentual ?? 0}
                    onChange={e => setModal((m: any) => ({ ...m, comissao_percentual: +e.target.value }))}
                    className="form-input" />
                  <span className="text-sm text-gray-500 shrink-0">%</span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Calculado sobre o valor de venda ao aprovar a proposta
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-gray-100 bg-gray-50 rounded-b-xl">
              <button onClick={() => setModal(null)} className="btn-secondary">Cancelar</button>
              <button onClick={salvar} className="btn-primary">Salvar</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Senha */}
      {modalSenha && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-sm mx-4 rounded-xl border border-gray-200 shadow-xl">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <h2 className="text-base font-semibold text-gray-900">Redefinir Senha</h2>
              <button onClick={() => setModalSenha(null)} className="p-1 text-gray-400 hover:text-gray-700 rounded">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="px-5 py-4 space-y-3">
              <p className="text-sm text-gray-500">
                Vendedor: <strong className="text-gray-800">{modalSenha.nome}</strong>
              </p>
              <div>
                <label className="form-label">Nova Senha (mín. 6 caracteres)</label>
                <input type="password" value={novaSenha}
                  onChange={e => setNovaSenha(e.target.value)}
                  className="form-input" />
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-gray-100 bg-gray-50 rounded-b-xl">
              <button onClick={() => setModalSenha(null)} className="btn-secondary">Cancelar</button>
              <button onClick={redefinirSenha} className="btn-primary">Redefinir</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
