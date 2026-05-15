import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AdminLayout } from './components/layout/AdminLayout'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/admin/Dashboard'
import { Estoque } from './pages/admin/Estoque'
import { Orcamentos } from './pages/admin/Orcamentos'
import { OrcamentoEditor } from './pages/admin/OrcamentoEditor'
import { OrcamentoWizard } from './pages/admin/orcamento/OrcamentoWizard'
import { Clientes } from './pages/admin/Clientes'
import { Financeiro } from './pages/admin/Financeiro'
import { Comissoes } from './pages/admin/Comissoes'
import { Prospeccao } from './pages/admin/Prospeccao'
import { Caixa } from './pages/admin/Caixa'
import { Operadores } from './pages/admin/Operadores'
import { Vendedores } from './pages/admin/Vendedores'
import { Auditoria } from './pages/admin/Auditoria'
import { Configuracoes } from './pages/admin/Configuracoes'
import { Templates } from './pages/admin/Templates'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Register />} />
        <Route element={<AdminLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/estoque" element={<Estoque />} />
          <Route path="/orcamentos" element={<Orcamentos />} />
          <Route path="/orcamentos/novo" element={<OrcamentoWizard />} />
          <Route path="/orcamentos/:id" element={<OrcamentoWizard />} />
          <Route path="/orcamentos/:id/classic" element={<OrcamentoEditor />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/vendedores" element={<Vendedores />} />
          <Route path="/financeiro" element={<Financeiro />} />
          <Route path="/comissoes" element={<Comissoes />} />
          <Route path="/prospeccao" element={<Prospeccao />} />
          <Route path="/caixa" element={<Caixa />} />
          <Route path="/operadores" element={<Operadores />} />
          <Route path="/auditoria" element={<Auditoria />} />
          <Route path="/configuracoes" element={<Configuracoes />} />
          <Route path="/templates" element={<Templates />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
