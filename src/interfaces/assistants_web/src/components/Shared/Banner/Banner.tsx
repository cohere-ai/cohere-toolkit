'use client';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

export type BannerTheme = 'primary' | 'secondary' | 'success' | 'error' | 'neutral' | 'dark';

type Props = {
  theme?: BannerTheme;
  children?: React.ReactNode;
  className?: string;
};

const THEME_CLASSES: { [key in BannerTheme]: string } = {
  primary: 'border-coral-800 bg-coral-950 text-volcanic-100',
  secondary: 'border-mushroom-800 bg-mushroom-950 text-volcanic-100',
  success: 'border-success-200 bg-success-950 text-success-200',
  error: 'border-danger-350 bg-danger-950 text-danger-350',
  neutral: 'border-marble-950 bg-marble-950 text-volcanic-100',
  dark: 'border-volcanic-300 bg-volcanic-150 text-marble-800',
};

export const Banner: React.FC<Props> = ({ theme = 'primary', className = '', children }) => {
  return (
    <Text as="div" className={cn('rounded-lg border p-4', THEME_CLASSES[theme], className)}>
      {children}
    </Text>
  );
};
