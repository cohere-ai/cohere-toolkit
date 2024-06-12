import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react';
import Link from 'next/link';

import { Icon, Text } from '@/components/Shared';

/**
 * @description renders a button to add a new agent.
 */
export const AddAgentButton: React.FC = () => {
  return (
    <Menu>
      <MenuButton className="group h-8 w-8 rounded border border-marble-500 p-px">
        <div className="flex h-full w-full items-center justify-center rounded bg-green-50 transition-colors duration-300 group-hover:bg-green-100/80">
          <Icon name="add" className="text-volcanic-800" />
        </div>
      </MenuButton>
      <MenuItems
        anchor="right start"
        className="z-menu ml-3 rounded bg-white px-2 py-1 shadow-menu"
      >
        <MenuItem
          as={Link}
          href="/agents/new"
          className="flex w-full items-center gap-x-2 rounded bg-white p-2 hover:bg-secondary-50"
        >
          <Icon name="add" className="text-secondary-700" />
          <Text>Create new agent</Text>
        </MenuItem>
        <div className="my-1 h-px w-full border-t border-marble-400" />
        <MenuItem
          as="button"
          className="flex w-full items-center gap-x-2 rounded bg-white p-2 hover:bg-secondary-50"
        >
          <Icon name="circles-four" className="text-secondary-700" />
          <Text>Add an existing agent</Text>
        </MenuItem>
      </MenuItems>
    </Menu>
  );
};
