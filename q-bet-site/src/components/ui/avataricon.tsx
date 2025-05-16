'use client';

import type { LucideIcon } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface IconAvatarProps {
  icon: LucideIcon;
  size?: 'sm' | 'md' | 'lg';
  bgColor?: string;
  iconColor?: string;
}

export function IconAvatar({
  icon: Icon,
  size = 'md',
  bgColor = 'bg-black',
  iconColor = 'text-primary-foreground',
}: IconAvatarProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-16 w-16',
  };

  const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-8 w-8',
  };

  return (
    <Avatar className={sizeClasses[size]}>
      <AvatarFallback className={bgColor}>
        <Icon className={`${iconSizes[size]} ${iconColor}`} />
      </AvatarFallback>
    </Avatar>
  );
}
