'use client';

import Link from 'next/link';

import { KebabMenu, KebabMenuItem } from '@/components/KebabMenu';
import { Text } from '@/components/Shared';
import { getIsTouchDevice, useIsDesktop } from '@/hooks/breakpoint';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useConversationActions } from '@/hooks/conversation';
import { useFileActions } from '@/hooks/files';
import { useConversationStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

export type ConversationListItem = {
  conversationId: string;
  updatedAt: string;
  title: string;
  description: string | null;
  weekHeading?: string;
};

type Props = {
  isChecked: boolean;
  isActive: boolean;
  showCheckbox: boolean;
  conversation: ConversationListItem;
  /* Config values necessary for react-flipped-toolkit */
  flippedProps: Object;
  onCheck: (id: string) => void;
};

const useMenuItems = ({ conversationId, name }: { conversationId: string; name: string }) => {
  const { deleteConversation, editConversationTitle } = useConversationActions();

  const menuItems: KebabMenuItem[] = [
    {
      label: 'Edit title',
      iconName: 'edit',
      onClick: () => {
        editConversationTitle({ id: conversationId, title: name });
      },
    },
    {
      label: 'Delete chat',
      iconName: 'trash',
      onClick: () => {
        deleteConversation({ id: conversationId });
      },
    },
  ];

  return menuItems;
};

export const ConversationCard: React.FC<Props> = ({ isActive, conversation, flippedProps }) => {
  const { title, conversationId, description } = conversation;
  const { agentId } = useChatRoutes();
  const { setSettings } = useSettingsStore();
  const {
    conversation: { id: selectedConversationId, name: conversationName },
    setConversation,
  } = useConversationStore();
  const isDesktop = useIsDesktop();
  const isTouchDevice = getIsTouchDevice();
  const { clearComposerFiles } = useFileActions();

  // if the conversation card is for the selected conversation we use the `conversationName`
  // from the context store, otherwise we use the name from the conversation object
  // this is to ensure that we use the typed animation
  // @see "handleUpdateConversationTitle" in hooks/chat.ts
  const name = conversationId === selectedConversationId ? conversationName : title;

  const menuItems = useMenuItems({ conversationId, name: name! });

  const info = (
    <div className="flex flex-col gap-y-1 pl-3">
      <div className="flex w-full items-center justify-between gap-x-0.5">
        <span className="flex items-center gap-x-1 truncate">
          <Text
            as="span"
            className={cn('h-[21px] truncate text-volcanic-300', {
              'font-medium': isActive,
            })}
          >
            {name}
          </Text>
        </span>

        {/* Placeholder for the kebab menu */}
        <div className="flex h-4 w-4 flex-shrink-0" />
      </div>
      <Text styleAs="p-sm" className={cn('h-[18px] w-full truncate text-volcanic-500')}>
        {description}
      </Text>
    </div>
  );

  const conversationUrl = agentId ? `/a/${agentId}/c/${conversationId}` : `/c/${conversationId}`;

  const wrapperClassName = cn('flex w-full flex-col gap-y-1 pr-2 py-3 truncate');
  const conversationLink =
    isActive && isDesktop ? (
      <div className={cn('select-none', wrapperClassName)}>{info}</div>
    ) : (
      <Link
        href={conversationUrl}
        key={conversationId}
        shallow
        onClick={() => {
          setConversation({ id: conversationId, name });
          setSettings({ isMobileConvListPanelOpen: false });
          clearComposerFiles();
        }}
        className={wrapperClassName}
      >
        {info}
      </Link>
    );

  return (
    <div
      {...flippedProps}
      className={cn('group relative flex w-full rounded-lg', 'flex items-start gap-x-1', {
        'bg-marble-1000 transition-colors ease-in-out hover:bg-mushroom-900/20': !isActive,
        'bg-mushroom-900/40': isActive,
      })}
    >
      {conversationLink}
      <div className="absolute right-3 top-3.5 flex">
        <KebabMenu
          anchor="left start"
          items={menuItems}
          className={cn('flex', {
            'hidden group-hover:flex': !isTouchDevice,
          })}
        />
      </div>
    </div>
  );
};
