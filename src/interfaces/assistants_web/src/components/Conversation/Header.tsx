'use client';

import { Transition } from '@headlessui/react';
import { usePathname } from 'next/navigation';
import { useContext } from 'react';

import { IconButton } from '@/components/IconButton';
import { KebabMenu, KebabMenuItem } from '@/components/KebabMenu';
import { ShareModal } from '@/components/ShareModal';
import { Text } from '@/components/Shared';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { ModalContext } from '@/context/ModalContext';
import { useAgent } from '@/hooks/agents';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useNavigateToNewChat } from '@/hooks/chatRoutes';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { useSession } from '@/hooks/session';
import { useAgentsStore, useConversationStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const useHeaderMenu = ({ agentId }: { agentId?: string }) => {
  const { open } = useContext(ModalContext);
  const {
    conversation: { id: conversationId },
  } = useConversationStore();

  const { userId } = useSession();
  const { data: agent } = useAgent({ agentId });
  const isAgentCreator = userId === agent?.user_id;

  const {
    setSettings,
    settings: { isConfigDrawerOpen },
  } = useSettingsStore();
  const {
    agents: { isEditAgentPanelOpen },
    setEditAgentPanelOpen,
  } = useAgentsStore();

  const pathname = usePathname();
  const { welcomeGuideState, progressWelcomeGuideStep, finishWelcomeGuide } =
    useWelcomeGuideState();

  const navigateToNewChat = useNavigateToNewChat();
  const handleNewChat = () => {
    navigateToNewChat(agentId);
  };

  const handleOpenShareModal = () => {
    if (!conversationId) return;
    open({
      title: 'Share link to conversation',
      content: <ShareModal conversationId={conversationId} />,
    });
  };

  const handleToggleConfigSettings = () => {
    setSettings({ isConfigDrawerOpen: !isConfigDrawerOpen });

    if (welcomeGuideState === WelcomeGuideStep.ONE && pathname === '/') {
      progressWelcomeGuideStep();
    } else if (welcomeGuideState !== WelcomeGuideStep.DONE) {
      finishWelcomeGuide();
    }
  };

  const handleOpenAgentDrawer = () => {
    setEditAgentPanelOpen(!isEditAgentPanelOpen);
    setSettings({ isConvListPanelOpen: false });
  };

  const menuItems: KebabMenuItem[] = [
    ...(!!agent
      ? [
          {
            label: isAgentCreator ? 'Edit assistant' : 'About assistant',
            iconName: isAgentCreator ? 'edit' : 'information',
            onClick: handleOpenAgentDrawer,
          } as KebabMenuItem,
        ]
      : []),
    {
      label: 'Settings',
      iconName: 'settings',
      onClick: handleToggleConfigSettings,
    },
    {
      label: 'Share',
      iconName: 'share',
      onClick: handleOpenShareModal,
    },
    {
      label: 'New chat',
      iconName: 'new-message',
      onClick: handleNewChat,
    },
  ];

  return {
    menuItems,
    isAgentCreator,
    handleNewChat,
    handleOpenShareModal,
    handleToggleConfigSettings,
    handleOpenAgentDrawer,
  };
};

type Props = {
  isStreaming?: boolean;
  conversationId?: string;
  agentId?: string;
};

export const Header: React.FC<Props> = ({ isStreaming, agentId }) => {
  const {
    conversation: { id, name },
  } = useConversationStore();
  const {
    settings: { isConvListPanelOpen, isConfigDrawerOpen },
    setSettings,
    setIsConvListPanelOpen,
  } = useSettingsStore();
  const {
    setAgentsSidePanelOpen,
    agents: { isEditAgentPanelOpen },
  } = useAgentsStore();

  const { welcomeGuideState } = useWelcomeGuideState();

  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;
  const {
    menuItems,
    isAgentCreator,
    handleNewChat,
    handleOpenShareModal,
    handleToggleConfigSettings,
    handleOpenAgentDrawer,
  } = useHeaderMenu({
    agentId,
  });

  return (
    <div className={cn('flex h-header w-full min-w-0 items-center border-b', 'border-marble-950')}>
      <div
        className={cn('flex w-full flex-1 items-center justify-between px-5', { truncate: !!id })}
      >
        <span
          className={cn(
            'relative flex min-w-0 flex-grow items-center gap-x-1 overflow-hidden py-4'
          )}
        >
          {(isMobile || !isConvListPanelOpen) && (
            <Transition
              show={true}
              appear
              enter="delay-300 transition ease-in-out duration-300"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="delay-300 transition ease-in-out duration-300"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
              as="div"
            >
              <IconButton
                iconName="side-panel"
                tooltip={{ label: 'Toggle chat list', placement: 'bottom-start', size: 'md' }}
                onClick={() => {
                  setSettings({ isConfigDrawerOpen: false });
                  setAgentsSidePanelOpen(false);
                  setIsConvListPanelOpen(true);
                }}
              />
            </Transition>
          )}

          <Text className="truncate" styleAs="p-lg" as="span">
            {name}
          </Text>
        </span>
        <span className="flex items-center gap-x-2 py-4 pl-4 md:pl-0">
          <KebabMenu className="md:hidden" items={menuItems} anchor="left start" />
          <IconButton
            tooltip={{ label: 'New chat', placement: 'bottom-end', size: 'md' }}
            className="hidden md:flex"
            iconName="new-message"
            onClick={handleNewChat}
          />
          {id && (
            <IconButton
              tooltip={{ label: 'Share', placement: 'bottom-end', size: 'md' }}
              className="hidden md:flex"
              iconName="share"
              onClick={handleOpenShareModal}
            />
          )}
          <div className="relative">
            <IconButton
              tooltip={{ label: 'Settings', placement: 'bottom-end', size: 'md' }}
              className={cn('hidden md:flex', { 'bg-mushroom-900': isConfigDrawerOpen })}
              onClick={handleToggleConfigSettings}
              iconName="settings"
              disabled={isStreaming}
            />
            <WelcomeGuideTooltip
              step={1}
              className={cn('right-0 top-full mt-9', {
                'delay-1000': !welcomeGuideState || welcomeGuideState === WelcomeGuideStep.ONE,
              })}
            />
          </div>
          <IconButton
            tooltip={{
              label: isAgentCreator ? 'Edit assistant' : 'About assistant',
              placement: 'bottom-end',
              size: 'md',
            }}
            iconName={isAgentCreator ? 'edit' : 'information'}
            onClick={handleOpenAgentDrawer}
            className={cn('hidden', {
              'md:flex': !!agentId,
              'bg-mushroom-900': isEditAgentPanelOpen,
            })}
          />
        </span>
      </div>
    </div>
  );
};
