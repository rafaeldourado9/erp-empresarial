import { useEffect, useState } from 'react'
import { Outlet, Navigate, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useAuthStore } from '../../store/auth.store'

const STORAGE_KEY = 'erp:sidebar:collapsed'

export function AdminLayout() {
  const { accessToken } = useAuthStore()
  const location = useLocation()

  const [collapsed, setCollapsed] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    return window.localStorage.getItem(STORAGE_KEY) === '1'
  })

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0')
  }, [collapsed])

  if (!accessToken) {
    return <Navigate to="/login" replace />
  }

  const sidebarWidth = collapsed ? 72 : 256

  return (
    <div className="flex h-screen bg-zinc-50">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(c => !c)} />
      <main
        className="flex-1 overflow-y-auto"
        style={{
          marginLeft: sidebarWidth,
          transition: 'margin-left 280ms cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        <div key={location.pathname} className="animate-page-enter">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
