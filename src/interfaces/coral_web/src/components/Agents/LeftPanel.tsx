import { Transition } from '@headlessui/react';
import Link from 'next/link';

import { CoralLogo, Text, Tooltip } from '@/components/Shared';
import { useSettingsStore } from '@/stores';

/**
 * @description
 */
export const LeftPanel: React.FC = () => {
  const {
    settings: { isAgentsSidePanelOpen },
  } = useSettingsStore();

  return (
    <div className="flex flex-col gap-3">
      {isAgentsSidePanelOpen && (
        <Text styleAs="label" className="text-green-800">
          Most recent
        </Text>
      )}
      <BaseAgentCard isExpanded={isAgentsSidePanelOpen} />
    </div>
  );
};

type BaseAgentCardProps = {
  isExpanded: boolean;
};
const BaseAgentCard: React.FC<BaseAgentCardProps> = ({ isExpanded }) => {
  return (
    <Tooltip label="Command R+" placement="right" hover={!isExpanded}>
      <Link href="/agents" className="flex items-center gap-x-2 rounded-lg p-2 hover:bg-marble-300">
        <div className="flex h-8 w-8 items-center justify-center rounded bg-secondary-400 transition-colors duration-300 group-hover:bg-secondary-500">
          <CoralLogo style="secondary" />
        </div>
        <Transition
          as="div"
          show={isExpanded}
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <Text>Command R+</Text>
        </Transition>
      </Link>
    </Tooltip>
  );
};
