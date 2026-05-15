import { Fragment } from 'react'
import { Lock } from 'lucide-react'

const fmt = (v: number) =>
  `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

export interface LinhaComposicao {
  nome: string
  qtd: number | null
  valor: number
  secao: 'base' | 'item' | 'premissa' | 'total'
  badge?: 'manual' | 'produto' | null
  obrigatoria?: boolean
}

export function TabelaComposicao({
  linhas, valorVenda,
}: { linhas: LinhaComposicao[]; valorVenda: number }) {
  const pct = (v: number) =>
    valorVenda > 0 ? `${((v / valorVenda) * 100).toFixed(2)}%` : '—'

  return (
    <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
      <div className="px-5 py-3 border-b border-zinc-100 flex items-center justify-between">
        <span className="text-sm font-semibold text-zinc-800">Composição do Preço</span>
        <span className="text-xs text-zinc-400">% sobre o valor de venda</span>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #E4E4E7', background: '#FAFAFA' }}>
            <th style={{ padding: '8px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em' }}>ITEM</th>
            <th style={{ padding: '8px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 60 }}>QTD</th>
            <th style={{ padding: '8px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 150 }}>VALORES</th>
            <th style={{ padding: '8px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#71717A', letterSpacing: '0.05em', width: 90 }}>% DO TOTAL</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((row, i) => {
            const isTotal = row.secao === 'total'
            const isDivider = row.secao === 'premissa' && linhas[i - 1]?.secao !== 'premissa'
            return (
              <Fragment key={i}>
                {isDivider && (
                  <tr style={{ borderTop: '1px solid #E4E4E7', borderBottom: '1px solid #E4E4E7', background: '#FAFAFA' }}>
                    <td colSpan={4} style={{ padding: '3px 16px', fontSize: '10px', fontWeight: 700, color: '#A1A1AA', letterSpacing: '0.08em' }}>
                      PREMISSAS
                    </td>
                  </tr>
                )}
                <tr style={{
                  borderBottom: isTotal ? 'none' : '1px solid #F4F4F5',
                  borderTop: isTotal ? '2px solid #E4E4E7' : 'none',
                  background: isTotal ? '#FAFAFA' : (row.obrigatoria ? '#FFFBEB' : 'white'),
                }}>
                  <td style={{ padding: '9px 16px', fontSize: '13px', color: isTotal ? '#18181B' : '#3F3F46', fontWeight: isTotal ? 700 : 400 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {row.obrigatoria && (
                        <Lock className="w-3 h-3 text-amber-500 shrink-0" />
                      )}
                      {row.badge && (
                        <span style={{
                          fontSize: 10, fontWeight: 600, padding: '1px 5px', borderRadius: 3,
                          background: row.badge === 'manual' ? '#FEF3C7' : '#DCFCE7',
                          color: row.badge === 'manual' ? '#D97706' : '#16A34A',
                        }}>
                          {row.badge === 'manual' ? 'M' : 'P'}
                        </span>
                      )}
                      <span style={{ textTransform: row.secao === 'total' ? 'none' : 'uppercase', letterSpacing: row.secao === 'total' ? 'normal' : '0.02em' }}>
                        {row.nome}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'center', fontSize: '13px', color: '#A1A1AA', fontVariantNumeric: 'tabular-nums' }}>
                    {row.qtd ?? '—'}
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'right', fontSize: '13px', color: isTotal ? '#2563EB' : '#18181B', fontWeight: isTotal ? 700 : 400, fontVariantNumeric: 'tabular-nums' }}>
                    {fmt(row.valor)}
                  </td>
                  <td style={{ padding: '9px 16px', textAlign: 'right', fontSize: '13px', color: isTotal ? '#2563EB' : '#71717A', fontWeight: isTotal ? 700 : 400, fontVariantNumeric: 'tabular-nums' }}>
                    {isTotal ? '100,00%' : pct(row.valor)}
                  </td>
                </tr>
              </Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
