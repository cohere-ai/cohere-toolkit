import { BasicButton } from '@/components/Shared/BasicButton';
import { Icon, IconName } from '@/components/Shared/Icon';
import { cn } from '@/utils';

type Props = {
  iconName: IconName;
  href?: string;
  shallow?: boolean;
  isDefaultOnHover?: boolean;
  iconKind?: 'default' | 'outline';
  iconClassName?: string;
  disabled?: boolean;
  className?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
};

/**
 * Convenience component for rendering an icon button that follows Coral UI's design patterns.
 */
const IconButton: React.FC<Props> = ({
  iconName,
  iconKind = 'outline',
  iconClassName,
  isDefaultOnHover = true,
  className,
  disabled,
  href,
  shallow,
  onClick,
}) => {
  return (
    <BasicButton
      className={cn('group h-8 w-8 p-0', className)}
      startIcon={
        <Icon
          name={iconName}
          className={cn(
            'text-secondary-700 group-hover:text-secondary-800',
            'transition-colors ease-in-out',
            {
              'group-hover:!font-iconDefault': isDefaultOnHover,
            },
            iconClassName
          )}
          kind={iconKind}
        />
      }
      size="lg"
      kind="minimal"
      disabled={disabled}
      href={href}
      shallow={shallow}
      onClick={onClick}
    />
  );
};
export default IconButton;
