import { cn } from '../../lib/utils'
import type { InputHTMLAttributes, ReactNode } from 'react'
import { forwardRef, useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  prefix?: ReactNode
  suffix?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, prefix, suffix, className, id, type, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s/g, '-')
    const isPassword = type === 'password'
    const [showPassword, setShowPassword] = useState(false)
    const resolvedType = isPassword ? (showPassword ? 'text' : 'password') : type
    const hasAddon = Boolean(prefix || suffix || isPassword)

    const eyeButton = isPassword && (
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setShowPassword((v) => !v)}
        className="flex items-center px-3 text-zinc-400 hover:text-zinc-600 transition-colors shrink-0 select-none"
        aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
      >
        {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
      </button>
    )

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-zinc-700">
            {label}
          </label>
        )}

        {hasAddon ? (
          <div
            className={cn(
              'flex items-stretch rounded-lg border overflow-hidden transition-all duration-150',
              'focus-within:ring-2 focus-within:ring-brand focus-within:border-transparent',
              'hover:border-zinc-400',
              error ? 'border-red-400 focus-within:ring-red-400' : 'border-zinc-300',
            )}
          >
            {prefix && (
              <span className="flex items-center px-3 bg-zinc-50 border-r border-zinc-200 text-zinc-500 text-xs whitespace-nowrap shrink-0 select-none">
                {prefix}
              </span>
            )}
            <input
              ref={ref}
              id={inputId}
              type={resolvedType}
              className={cn(
                'flex-1 min-w-0 h-9 bg-white text-sm text-zinc-900',
                'px-3 py-2 placeholder:text-zinc-400',
                'focus:outline-none',
                'disabled:bg-zinc-50 disabled:text-zinc-400 disabled:cursor-not-allowed',
                className,
              )}
              {...props}
            />
            {suffix && (
              <span className="flex items-center px-3 bg-zinc-50 border-l border-zinc-200 text-zinc-500 text-xs whitespace-nowrap shrink-0 select-none">
                {suffix}
              </span>
            )}
            {eyeButton}
          </div>
        ) : (
          <input
            ref={ref}
            id={inputId}
            type={resolvedType}
            className={cn(
              'w-full h-9 rounded-lg border border-zinc-300 bg-white text-sm text-zinc-900',
              'px-3 py-2 placeholder:text-zinc-400',
              'focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent',
              'hover:border-zinc-400',
              'disabled:bg-zinc-50 disabled:text-zinc-400 disabled:cursor-not-allowed',
              'transition-all duration-150',
              error && 'border-red-400 focus:ring-red-400',
              className,
            )}
            {...props}
          />
        )}

        {error && <p className="text-xs text-red-600">{error}</p>}
        {hint && !error && <p className="text-xs text-zinc-500">{hint}</p>}
      </div>
    )
  },
)

Input.displayName = 'Input'
