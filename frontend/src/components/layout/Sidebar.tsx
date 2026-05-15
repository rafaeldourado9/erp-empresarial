import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Package, FileText, Users, DollarSign,
  TrendingUp, ShoppingCart, Settings, LogOut, Sun,
  Award, Search, UserCheck, PanelLeftClose, PanelLeftOpen, LayoutTemplate,
} from 'lucide-react'
import { useAuthStore } from '../../store/auth.store'

const navGroups = [
  {
    label: 'Operações',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/orcamentos', icon: FileText, label: 'Orçamentos' },
      { to: '/templates', icon: LayoutTemplate, label: 'Templates' },
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

interface Props {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: Props) {
  const { usuario, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside
      className={`sidebar-shell ${collapsed ? 'sidebar-collapsed' : ''}`}
      style={{ width: collapsed ? 72 : 256 }}
    >
      {/* Brand + toggle */}
      <div className="px-3 py-4 border-b border-white/5 flex items-center gap-2.5 min-h-[64px]">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-[0_4px_12px_-2px_rgba(59,130,246,0.6)] shrink-0">
          <Sun className="w-5 h-5 text-white" strokeWidth={2.4} />
        </div>
        <div className="sidebar-brand-label flex-1 min-w-0">
          <p className="font-bold text-sm tracking-tight leading-tight">ERP Solar</p>
          {usuario && (
            <p className="text-[11px] text-zinc-400 truncate leading-tight mt-0.5">
              {usuario.nome}
            </p>
          )}
        </div>
        <button
          onClick={onToggle}
          aria-label={collapsed ? 'Expandir menu' : 'Recolher menu'}
          title={collapsed ? 'Expandir menu' : 'Recolher menu'}
          className="shrink-0 w-8 h-8 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 flex items-center justify-center transition-colors"
        >
          {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto overflow-x-hidden p-2 no-scrollbar">
        {navGroups.map((group, gi) => (
          <div key={group.label} className={gi > 0 ? 'mt-3' : ''}>
            <p className="sidebar-section-label">{group.label}</p>
            {group.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="sidebar-link-label">{label}</span>
                <span className="sidebar-tooltip">{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="p-2 border-t border-white/5">
        <button
          onClick={handleLogout}
          className="sidebar-link w-full text-zinc-400 hover:text-white"
          title="Sair"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <span className="sidebar-link-label">Sair</span>
          <span className="sidebar-tooltip">Sair</span>
        </button>
      </div>
    </aside>
  )
}
