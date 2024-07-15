import { cn } from '@/utils';

export const CoralLogo: React.FC<{
  isDarkModeEnabled?: boolean;
  style?: 'grayscale' | 'primary' | 'secondary';
  className?: string;
}> = ({ className, style = 'primary', isDarkModeEnabled }) => (
  <svg
    viewBox="0 0 22 23"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn(
      'h-5 w-5',
      {
        'fill-coral-200': style === 'primary',
        'dark:fill-blue-900': style === 'primary' && isDarkModeEnabled,
        'fill-marble-950': style === 'grayscale',
        'fill-mushroom-800': style === 'secondary',
      },
      className
    )}
  >
    <path d="M10.0641 4.03514L10.0709 12.8718C10.0709 15.381 7.03945 16.6424 5.25585 14.8656L1.77682 11.3933C0.644266 10.2608 0.00678112 8.72132 0.00678112 7.12083L0 4.02836C0 1.80394 1.80394 0 4.02836 0H6.03575C8.26017 0.00678175 10.0641 1.81073 10.0641 4.03514Z" />
    <path d="M14.3434 0.888489H17.7207C19.1042 0.888489 19.7959 2.5568 18.8261 3.54015L16.1134 6.27998C14.5536 7.86012 11.8613 6.7547 11.8613 4.53029V3.37739C11.8545 2.00069 12.9667 0.888489 14.3434 0.888489Z" />
    <path d="M18.3107 22.0271H15.5438C13.5024 22.0271 11.8409 20.352 11.8545 18.3107L11.8748 15.442C11.8884 13.7737 12.553 12.18 13.7262 11L17.2731 7.44636C19.016 5.69667 22 6.93095 22 9.3995V18.3311C22.0068 20.3791 20.352 22.0271 18.3107 22.0271Z" />
    <path d="M0.874847 19.3822V17.0222C0.874847 15.3878 2.84834 14.574 4.00123 15.7269L6.88347 18.6023C7.85326 19.5653 7.16831 21.2201 5.7984 21.2201H2.70592C1.69544 21.2133 0.874847 20.3927 0.874847 19.3822Z" />
  </svg>
);
