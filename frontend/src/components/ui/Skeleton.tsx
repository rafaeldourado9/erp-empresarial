import { type CSSProperties, type HTMLAttributes } from 'react'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  width?: number | string
  height?: number | string
  rounded?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

export function Skeleton({
  width,
  height,
  rounded = 'md',
  style,
  className = '',
  ...rest
}: SkeletonProps) {
  const radius = {
    sm: 'rounded',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full',
  }[rounded]

  const combined: CSSProperties = {
    width: width ?? '100%',
    height: height ?? 14,
    ...style,
  }

  return <div className={`skeleton ${radius} ${className}`} style={combined} {...rest} />
}

export function SkeletonText({
  lines = 3,
  className = '',
}: {
  lines?: number
  className?: string
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height={12}
          width={i === lines - 1 ? '70%' : '100%'}
        />
      ))}
    </div>
  )
}

export function TableSkeleton({
  rows = 5,
  cols = 5,
  showHeader = true,
}: {
  rows?: number
  cols?: number
  showHeader?: boolean
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-zinc-100 overflow-hidden">
      {showHeader && (
        <div className="bg-zinc-50 border-b border-zinc-200 px-4 py-3 flex gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <Skeleton key={i} height={10} width={`${100 / cols - 4}%`} />
          ))}
        </div>
      )}
      <div className="divide-y divide-zinc-100">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="px-4 py-3.5 flex gap-4 items-center">
            {Array.from({ length: cols }).map((_, c) => (
              <Skeleton
                key={c}
                height={12}
                width={`${100 / cols - 4}%`}
                style={{ opacity: 1 - r * 0.08 }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export function MetricSkeleton() {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-zinc-100">
      <div className="flex items-center justify-between">
        <div className="space-y-2 flex-1">
          <Skeleton height={10} width="60%" />
          <Skeleton height={22} width="80%" />
        </div>
        <Skeleton height={48} width={48} rounded="xl" />
      </div>
    </div>
  )
}

export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-zinc-100 space-y-3">
      <Skeleton height={14} width="40%" />
      <SkeletonText lines={lines} />
    </div>
  )
}

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center justify-between text-sm">
          <div className="flex-1 space-y-1.5">
            <Skeleton height={12} width="50%" />
            <Skeleton height={10} width="30%" />
          </div>
          <Skeleton height={20} width={70} rounded="full" />
        </div>
      ))}
    </div>
  )
}

/**
 * Linhas skeleton para inserir DENTRO de uma <tbody> existente.
 * Preserva o layout/colunas da tabela.
 */
export function TableRowsSkeleton({
  rows = 5,
  cols,
}: {
  rows?: number
  cols: number
}) {
  return (
    <>
      {Array.from({ length: rows }).map((_, r) => (
        <tr key={`sk-${r}`}>
          {Array.from({ length: cols }).map((_, c) => (
            <td key={c} className="px-4 py-3.5">
              <Skeleton
                height={12}
                width={c === 0 ? '65%' : c === cols - 1 ? '40%' : '80%'}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}
