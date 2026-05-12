import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Package, FileText, Users, DollarSign,
  TrendingUp, ShoppingCart, Settings, LogOut, Building2,
  Award, Search, UserCheck,
} from 'lucide-react'
import { useAuthStore } from '../../store/auth.store'

const navGroups = [
  {
    label: 'Operações',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/orcamentos', icon: FileText, label: 'Orçamentos' },
      { to: '/caixa', icon: ShoppingCart, label: 'Caixa' },
      { to: '/estoque', icon: Package, label: 'Estoque' },
    ],
  },
  {
    label: 'Comercial',
    items: [
      { to: '/clientes', icon: Users, label: 'Clientes' },
      { to: '/vendedores', icon: UserCheck, label: 'Vendedores' },
      { to: '/prospeccao', icon: TrendingUp, label: 'Prospecção' },
      { to: '/comissoes', icon: Award, label: 'Comissões' },
    ],
  },
  {
    label: 'Gestão',
    items: [
      { to: '/financeiro', icon: DollarSign, label: 'Financeiro' },
      { to: '/operadores', icon: Users, label: 'Operadores' },
      { to: '/auditoria', icon: Search, label: 'Auditoria' },
      { to: '/configuracoes', icon: Settings, label: 'Configurações' },
    ],
  },
]

export function Sidebar() {
  const { usuario, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen fixed left-0 top-0">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Building2 className="w-6 h-6 text-blue-400" />
          <span className="font-bold text-lg">ERP Empresarial</span>
        </div>
        {usuario && (
          <p className="text-xs text-gray-400 mt-1 truncate">{usuario.nome}</p>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto p-2 no-scrollbar">
        {navGroups.map((group, gi) => (
          <div key={group.label} className={gi > 0 ? 'mt-4' : ''}>
            <p className="sidebar-section-label">{group.label}</p>
            {group.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg mb-0.5 text-sm transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white font-medium'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-700">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-gray-400 hover:text-white text-sm w-full px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sair
        </button>
      </div>
    </aside>
  )
}
