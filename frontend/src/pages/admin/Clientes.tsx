import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Search, Phone, Mail } from 'lucide-react'
import { clientesApi } from '../../api/clients'

export function Clientes() {
  const [clientes, setClientes] = useState<any[]>([])
  const [busca, setBusca] = useState('')
  const [modal, setModal] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const carregar = () => {
    setLoading(true)
    clientesApi.listar(busca || undefined).then(setClientes).finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [busca])

  const salvar = async () => {
    if (modal.id) {
      await clientesApi.atualizar(modal.id, modal)
    } else {
      await clientesApi.criar(modal)
    }
    setModal(null)
    carregar()
  }

  const deletar = async (id: string) => {
    if (!confirm('Remover cliente?')) return
    await clientesApi.deletar(id)
    carregar()
  }

  const empty = { nome: '', email: '', telefone: '', cpf_cnpj: '', endereco: '' }

  const campos = [
    { k: 'nome', label: 'Nome', required: true },
    { k: 'email', label: 'E-mail', type: 'email' },
    { k: 'telefone', label: 'Telefone' },
    { k: 'cpf_cnpj', label: 'CPF / CNPJ' },
    { k: 'endereco', label: 'Endereço' },
  ]

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
        <button onClick={() => setModal(empty)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> Novo Cliente
        </button>
      </div>

      <div className="relative mb-4">
        <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
        <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Buscar por nome..."
          className="pl-9 w-full max-w-xs border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Contato</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">CPF / CNPJ</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Endereço</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Carregando...</td></tr>}
            {!loading && clientes.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gray-400">Nenhum cliente cadastrado</td></tr>}
            {clientes.map(c => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{c.nome}</td>
                <td className="px-4 py-3 text-gray-600">
                  <div className="flex flex-col gap-0.5">
                    {c.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" />{c.email}</span>}
                    {c.telefone && <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{c.telefone}</span>}
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">{c.cpf_cnpj || '—'}</td>
                <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{c.endereco || '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => setModal({ ...c })} className="p-1 text-gray-400 hover:text-blue-600">
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button onClick={() => deletar(c.id)} className="p-1 text-gray-400 hover:text-red-600">
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
            <h2 className="font-semibold text-lg mb-4">{modal.id ? 'Editar' : 'Novo'} Cliente</h2>
            <div className="space-y-3">
              {campos.map(({ k, label, type = 'text', required }) => (
                <div key={k}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}{required && ' *'}</label>
                  <input type={type} value={modal[k] ?? ''} required={required}
                    onChange={e => setModal((m: any) => ({ ...m, [k]: e.target.value }))}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              ))}
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
