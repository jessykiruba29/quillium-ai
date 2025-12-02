'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface CyberBorderProps {
  children: ReactNode
  className?: string
  intensity?: 'low' | 'medium' | 'high'
}

export const CyberBorder = ({ 
  children, 
  className,
  intensity = 'medium' 
}: CyberBorderProps) => {
  const intensityMap = {
    low: 'opacity-30',
    medium: 'opacity-50',
    high: 'opacity-70'
  }

  return (
    <div className={cn('relative', className)}>
      {/* Outer glow */}
      <div className={cn(
        'absolute -inset-1 bg-linear-to-r from-cyan-500 via-purple-500 to-pink-500 rounded-xl blur',
        intensityMap[intensity],
        'animate-pulse'
      )} />
      
      {/* Inner border */}
      <div className="relative rounded-xl bg-black/80 backdrop-blur-sm border border-cyan-500/30">
        {children}
      </div>
    </div>
  )
}