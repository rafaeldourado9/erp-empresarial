import { cn } from '../../lib/utils'
import { ORDER_STATUS_CONFIG, ESTOQUE_STATUS_CONFIG, ENTREGADOR_STATUS_CONFIG } from '../../lib/constants'
import type { PedidoStatus, StatusEstoque, StatusEntregador } from '../../types'

export function OrderStatusBadge({ status }: { status: PedidoStatus }) {
  const cfg = ORDER_STATUS_CONFIG[status]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        cfg.bg,
        cfg.text,
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', cfg.dot)} />
      {cfg.label}
    </span>
  )
}

export function EstoqueStatusBadge({ status }: { status: StatusEstoque }) {
  const cfg = ESTOQUE_STATUS_CONFIG[status]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        cfg.bg,
        cfg.text,
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', cfg.dot)} />
      {cfg.label}
    </span>
  )
}

export function EntregadorStatusBadge({ status }: { status: StatusEntregador }) {
  const cfg = ENTREGADOR_STATUS_CONFIG[status]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        cfg.bg,
        cfg.text,
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', cfg.dot)} />
      {cfg.label}
    </span>
  )
}
