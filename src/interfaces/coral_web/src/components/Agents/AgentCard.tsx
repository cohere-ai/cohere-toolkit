import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import Link from 'next/link';

import { CoralLogo, Icon, Text, Tooltip } from '@/components/Shared';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  isExpanded: boolean;
  name: string;
  isBaseAgent?: boolean;
  id?: string;
};

/**
 * @description This component renders an agent card.
 * It shows the agent's name and a colored icon with the first letter of the agent's name.
 * If the agent is a base agent, it shows the Coral logo instead.
 */
export const AgentCard: React.FC<Props> = ({ name, id, isBaseAgent, isExpanded }) => {
  return (
    <Tooltip label={name} placement="right" hover={!isExpanded}>
      <Link
        href={isBaseAgent ? '/agents' : `/agents?id=${id}`}
        className="flex w-full items-center justify-between gap-x-2 rounded-lg p-2 transition-colors hover:bg-marble-300"
        shallow
      >
        <div
          className={cn(
            'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded duration-300',
            id && getCohereColor(id),
            {
              'bg-secondary-400': isBaseAgent,
            }
          )}
        >
          {isBaseAgent && <CoralLogo style="secondary" />}
          {!isBaseAgent && (
            <Text className="uppercase text-white" styleAs="p-lg">
              {name[0]}
            </Text>
          )}
        </div>
        <Transition
          as="div"
          show={isExpanded}
          className="flex-grow overflow-x-hidden"
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <Text className="truncate">{name}</Text>
        </Transition>
        <Transition
          as="div"
          show={isExpanded && !isBaseAgent}
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <Menu>
            <MenuButton className="rounded p-px hover:bg-marble-400">
              <Icon name="kebab" className="text-volcanic-700" />
            </MenuButton>
            <MenuItems
              anchor="right start"
              className="z-menu ml-3 rounded bg-white px-2 py-1 shadow-menu"
            >
              <MenuItem
                as={Link}
                href={`/agents?id=${id}`}
                onClick={(e) => e.stopPropagation()}
                className="flex w-full items-center gap-x-2 rounded bg-white p-2 hover:bg-secondary-50"
              >
                <Icon name="new-message" kind="outline" className="text-secondary-700" />
                <Text>New chat</Text>
              </MenuItem>
              <div className="my-1 h-px w-full border-t border-marble-400" />
              <MenuItem
                as="button"
                onClick={(e) => e.stopPropagation()}
                className="flex w-full items-center gap-x-2 rounded bg-white p-2 hover:bg-secondary-50"
              >
                <Icon name="hide" kind="outline" className="text-secondary-700" />
                <Text>Hide assistant</Text>
              </MenuItem>
            </MenuItems>
          </Menu>
        </Transition>
      </Link>
    </Tooltip>
  );
};
