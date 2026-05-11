import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Building2 } from 'lucide-react'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/auth.store'

export function Register() {
  const [form, setForm] = useState({ nome_grupo: '', nome_empresa: '', nome_admin: '', email: '', senha: '' })
  const [erro, setErro] = useState('')
  const [loading, setLoading] = useState(false)
  const { setTokens, setUsuario } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      const data = await authApi.registro(form)
      setTokens(data.access_token, data.refresh_token)
      const me = await authApi.me()
      setUsuario(me)
      navigate('/dashboard')
    } catch (err: any) {
      setErro(err.response?.data?.detail || 'Erro ao criar conta')
    } finally {
      setLoading(false)
    }
  }

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-8">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
        <div className="flex items-center gap-2 mb-6">
          <Building2 className="w-8 h-8 text-blue-600" />
          <span className="font-bold text-xl text-gray-900">ERP Empresarial</span>
        </div>
        <h1 className="text-lg font-semibold text-gray-800 mb-6">Criar conta</h1>
        {erro && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 text-sm mb-4">{erro}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-3">
          {[
            { k: 'nome_grupo', label: 'Nome do Grupo Empresarial' },
            { k: 'nome_empresa', label: 'Nome da Empresa Principal' },
            { k: 'nome_admin', label: 'Seu Nome' },
            { k: 'email', label: 'E-mail', type: 'email' },
            { k: 'senha', label: 'Senha', type: 'password' },
          ].map(({ k, label, type = 'text' }) => (
            <div key={k}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type={type}
                value={form[k as keyof typeof form]}
                onChange={set(k)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          ))}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg text-sm transition-colors disabled:opacity-50 mt-2"
          >
            {loading ? 'Criando...' : 'Criar conta'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Já tem conta?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">Entrar</Link>
        </p>
      </div>
    </div>
  )
}
