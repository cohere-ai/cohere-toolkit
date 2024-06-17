import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { useState } from 'react';
import { usePopper } from 'react-popper';

import { Icon, IconName, Text } from '@/components/Shared';
import { cn } from '@/utils';

export type KebabMenuItem = {
  label: string;
  onClick: VoidFunction;
  iconName?: IconName;
  icon?: React.ReactNode;
  className?: string;
  visible?: boolean;
};
type Props = {
  items: KebabMenuItem[];
  className?: string;
};

/**
 * Menu with a kebab button which opens up a list of items.
 * It uses react-popper to position the menu.
 */
export const KebabMenu: React.FC<Props> = ({ items, className = '' }) => {
  const [referenceElement, setReferenceElement] = useState<Element | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    modifiers: [
      {
        // Positions the menu relative to the kebab button
        name: 'offset',
        options: {
          offset: [0, 4],
        },
      },
      {
        // Offsets the menu if it overflows and will be cutoff
        name: 'preventOverflow',
        options: {
          padding: 16,
        },
      },
    ],
  });

  return (
    <Menu as="div" className={cn('flex flex-col')}>
      {({ open }) => (
        <>
          <MenuButton
            className={cn('flex cursor-pointer p-0 text-secondary-800', className, {
              // Always override styles and show the kebab button if the menu is open
              'md:flex': open,
            })}
            onClick={(e) => e.stopPropagation()}
            ref={setReferenceElement}
          >
            <Icon name="kebab" />
          </MenuButton>

          <Transition
            as={MenuItems}
            appear
            enterFrom="opacity-0"
            enterTo="opacity-100"
            className={cn(
              'z-menu divide-y divide-marble-400 rounded-md bg-marble-100 p-2',
              'min-w-menu shadow-menu',
              'transition-opacity ease-in-out',
              { hidden: !open }
            )}
            ref={setPopperElement}
            style={styles.popper}
            {...attributes.popper}
          >
            {items.map(
              ({ label, iconName, icon, onClick, className, visible = true }, index) =>
                visible && (
                  <MenuItem
                    key={label}
                    as="li"
                    className={cn(
                      'group/menu-item flex items-center gap-x-2 px-4 py-3 transition-colors ease-in-out hover:bg-secondary-100/80',
                      'cursor-pointer',
                      className,
                      {
                        'rounded-tl rounded-tr': index === 0,
                        'rounded-bl rounded-br': index === items.length - 1,
                      }
                    )}
                    onClick={onClick}
                  >
                    {!!iconName && (
                      <Icon
                        name={iconName}
                        className={cn(
                          'text-secondary-700 group-hover/menu-item:!font-iconDefault',
                          className
                        )}
                        kind="outline"
                      />
                    )}
                    {!!icon && icon}
                    <Text>{label}</Text>
                  </MenuItem>
                )
            )}
          </Transition>
        </>
      )}
    </Menu>
  );
};
