import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  usuario: {
    id: string
    nome: string
    email: string
    perfil: string
    empresa_id: string | null
    grupo_id: string
    permissoes: string[]
  } | null
  empresaSelecionada: string | null
  setTokens: (access: string, refresh: string) => void
  setUsuario: (u: AuthState['usuario']) => void
  setEmpresaSelecionada: (id: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      usuario: null,
      empresaSelecionada: null,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setUsuario: (u) => set({ usuario: u, empresaSelecionada: u?.empresa_id ?? null }),
      setEmpresaSelecionada: (id) => set({ empresaSelecionada: id }),
      logout: () => set({ accessToken: null, refreshToken: null, usuario: null, empresaSelecionada: null }),
    }),
    { name: 'erp-auth' }
  )
)
