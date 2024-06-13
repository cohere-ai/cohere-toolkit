import { Transition } from '@headlessui/react';
import { useRouter } from 'next/router';
import { useMemo } from 'react';

import { ConfigurationDrawerButton } from '@/components/ConfigurationDrawerButton';
import { Dot } from '@/components/Dot';
import IconButton from '@/components/IconButton';
import { KebabMenu, KebabMenuItem } from '@/components/KebabMenu';
import { Text } from '@/components/Shared';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useConversationActions } from '@/hooks/conversation';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { useIsGroundingOn } from '@/hooks/grounding';
import { useCitationsStore, useConversationStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const useMenuItems = ({ conversationId }: { conversationId?: string }) => {
  const { deleteConversation } = useConversationActions();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { settings, setSettings } = useSettingsStore();
  const router = useRouter();
  const { welcomeGuideState, progressWelcomeGuideStep, finishWelcomeGuide } =
    useWelcomeGuideState();
  const isGroundingOn = useIsGroundingOn();

  const menuItems: KebabMenuItem[] = useMemo(() => {
    if (!conversationId) {
      return [];
    }

    return [
      {
        label: 'Tools',
        icon: <Dot on={isGroundingOn} />,
        onClick: () => {
          setSettings({ isConfigDrawerOpen: true });

          if (welcomeGuideState === WelcomeGuideStep.ONE && router.pathname === '/') {
            progressWelcomeGuideStep();
          } else if (welcomeGuideState !== WelcomeGuideStep.DONE) {
            finishWelcomeGuide();
          }
        },
      },
      {
        label: 'Delete chat',
        iconName: 'trash',
        onClick: () => {
          deleteConversation({ id: conversationId });
        },
        className: 'text-danger-500',
      },
      {
        label: 'New chat',
        iconName: 'new-message',
        onClick: () => {
          router.push('/', undefined, { shallow: true });
          resetConversation();
          resetCitations();
        },
      },
    ];
  }, [conversationId, settings, isGroundingOn]);

  return menuItems;
};

type Props = {
  isStreaming?: boolean;
  conversationId?: string;
};

export const Header: React.FC<Props> = ({ conversationId, isStreaming }) => {
  const {
    conversation: { id, name },
  } = useConversationStore();
  const {
    settings: { isConvListPanelOpen },
    setSettings,
    setIsConvListPanelOpen,
  } = useSettingsStore();
  const isDesktop = useIsDesktop();
  const menuItems = useMenuItems({ conversationId: id });

  const { deleteConversation } = useConversationActions();

  const handleDelete = (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
    e.stopPropagation();
    e.preventDefault();
    if (!id) return;
    deleteConversation({ id });
  };

  return (
    <div className={cn('flex h-header w-full min-w-0 items-center border-b', 'border-marble-400')}>
      <div
        className={cn('flex w-full flex-1 items-center justify-between px-5', { truncate: !!id })}
      >
        <span
          className={cn(
            'relative flex min-w-0 flex-grow items-center gap-x-1 overflow-hidden py-4'
          )}
        >
          {(!isDesktop || !isConvListPanelOpen) && (
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
              className={cn({
                'lg:hidden': isConvListPanelOpen,
              })}
            >
              <IconButton
                iconName="side-panel"
                onClick={() => {
                  setSettings({ isConfigDrawerOpen: false });
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
          <KebabMenu className={cn('md:hidden', { hidden: !conversationId })} items={menuItems} />
          <IconButton
            iconName="trash"
            onClick={handleDelete}
            disabled={isStreaming}
            className={cn('hidden', { 'md:flex': !!conversationId })}
          />
          <ConfigurationDrawerButton
            className={cn({ flex: !conversationId, 'hidden md:flex': !!conversationId })}
          />
        </span>
      </div>
    </div>
  );
};
