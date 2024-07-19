'use client';

import {
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  MenuItemsProps,
  Transition,
} from '@headlessui/react';
import Link from 'next/link';

import { Icon, IconName, Text } from '@/components/Shared';
import { cn } from '@/utils';

export type KebabMenuItem = {
  label: string;
  onClick?: VoidFunction;
  href?: string;
  iconName?: IconName;
  icon?: React.ReactNode;
  className?: string;
  visible?: boolean;
};
type Props = {
  items: KebabMenuItem[];
  anchor: MenuItemsProps['anchor'];
  className?: string;
};

/**
 * Menu with a kebab button which opens up a list of items.
 */
export const KebabMenu: React.FC<Props> = ({ items, anchor, className = '' }) => {
  return (
    <Menu as="div" className={cn('flex flex-col')}>
      {({ open }) => (
        <>
          <MenuButton
            className={cn('flex cursor-pointer p-0 text-mushroom-300', className, {
              // Always override styles and show the kebab button if the menu is open
              flex: open,
            })}
            onClick={(e) => e.stopPropagation()}
          >
            <Icon name="kebab" />
          </MenuButton>
          <Transition
            as={MenuItems}
            appear
            anchor={anchor}
            enterFrom="opacity-0"
            enterTo="opacity-100"
            className={cn(
              'z-menu divide-y divide-marble-950 rounded-md bg-marble-1000 p-2',
              'min-w-menu shadow-menu',
              'transition-opacity ease-in-out',
              { hidden: !open }
            )}
          >
            {items.map(
              ({ label, iconName, icon, onClick, href, className, visible = true }, index) => {
                return (
                  visible && (
                    <MenuItem
                      key={label}
                      as={href ? Link : 'button'}
                      className={cn(
                        'group/menu-item flex w-full items-center gap-x-2 px-4 py-3 transition-colors ease-in-out hover:bg-mushroom-900/80',
                        'cursor-pointer',
                        className,
                        {
                          'rounded-tl rounded-tr': index === 0,
                          'rounded-bl rounded-br': index === items.length - 1,
                        }
                      )}
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation();
                        onClick?.();
                      }}
                      {...(href ? { href, shallow: true } : {})}
                    >
                      {!!iconName && (
                        <Icon
                          name={iconName}
                          className={cn(
                            'text-mushroom-400 group-hover/menu-item:!font-iconDefault',
                            className
                          )}
                          kind="outline"
                        />
                      )}
                      {!!icon && icon}
                      <Text>{label}</Text>
                    </MenuItem>
                  )
                );
              }
            )}
          </Transition>
        </>
      )}
    </Menu>
  );
};
