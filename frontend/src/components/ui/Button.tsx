import { cn } from '../../lib/utils'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  children: ReactNode
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  className,
  disabled,
  children,
  ...props
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed'

  const variants = {
    primary:
      'bg-brand text-white hover:bg-brand-dark focus:ring-brand shadow-sm hover:shadow',
    secondary:
      'bg-zinc-100 text-zinc-700 hover:bg-zinc-200 focus:ring-zinc-300',
    ghost:
      'text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 focus:ring-zinc-200',
    danger:
      'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm',
    outline:
      'border border-zinc-300 text-zinc-700 hover:bg-zinc-50 focus:ring-zinc-200 bg-white',
  }

  const sizes = {
    sm: 'text-xs px-2.5 py-1.5 h-7',
    md: 'text-sm px-3.5 py-2 h-9',
    lg: 'text-sm px-5 py-2.5 h-11',
  }

  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}
