'use client';

import Link from 'next/link';

import { KebabMenu, KebabMenuItem } from '@/components/KebabMenu';
import { CoralLogo, Text } from '@/components/Shared';
import { useListAgents } from '@/hooks/agents';
import { getIsTouchDevice, useIsDesktop } from '@/hooks/breakpoint';
import { useConversationActions } from '@/hooks/conversation';
import { useConversationStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

export type ConversationListItem = {
  conversationId: string;
  updatedAt: string;
  title: string;
  agentId: string | null;
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
      label: 'Share Chat',
      iconName: 'share',
      onClick: () => {
        // editConversationTitle({ id: conversationId, title: name });
        alert('TODO: Share Chat');
      },
    },
    {
      label: 'Delete chat',
      iconName: 'trash',
      iconClassName: 'dark:text-danger-500',
      onClick: () => {
        deleteConversation({ id: conversationId });
      },
    },
  ];

  return menuItems;
};

const formateDate = (date: string) =>
  new Intl.DateTimeFormat('en-US', {
    month: 'short',
    year: '2-digit',
  }).format(new Date(date));

export const ConversationCard: React.FC<Props> = ({ isActive, conversation, flippedProps }) => {
  const { title, conversationId } = conversation;
  const { data: agents = [] } = useListAgents();
  const agent = agents.find((a) => a.id === conversation.agentId);
  const agentColor = getCohereColor(agent?.id);
  const { setSettings } = useSettingsStore();
  const {
    conversation: { id: selectedConversationId, name: conversationName },
    setConversation,
  } = useConversationStore();
  const isDesktop = useIsDesktop();
  const isTouchDevice = getIsTouchDevice();

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
            className={cn('h-[21px] truncate text-volcanic-300 dark:text-mushroom-950', {
              'font-medium': isActive,
            })}
          >
            {name}
          </Text>
        </span>

        {/* Placeholder for the kebab menu */}
        <div className="flex h-4 w-4 flex-shrink-0" />
      </div>
      <div className="flex h-[18px] w-full items-center gap-2">
        <div
          className={cn('flex size-4 flex-shrink-0 items-center justify-center rounded', {
            'bg-mushroom-700': !agent,
            [agentColor]: agent,
          })}
        >
          {agent ? (
            <Text className="text-white" styleAs="p-xs">
              {agent.name[0]}
            </Text>
          ) : (
            <CoralLogo style="secondary" className="scale-50" />
          )}
        </div>
        <Text styleAs="p-sm" className="truncate text-volcanic-500 dark:text-mushroom-800">
          {agent?.name ?? 'Cohere AI'}
        </Text>
        <Text styleAs="code-sm" className="ml-auto mt-0.5 uppercase dark:text-mushroom-800">
          {formateDate(conversation.updatedAt)}
        </Text>
      </div>
    </div>
  );

  const conversationUrl = agent ? `/a/${agent.id}/c/${conversationId}` : `/c/${conversationId}`;

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
        'bg-marble-1000 transition-colors ease-in-out hover:bg-mushroom-900/20 dark:bg-transparent':
          !isActive,
        'bg-mushroom-900/40 dark:bg-volcanic-200': isActive,
      })}
    >
      {conversationLink}
      <div className="absolute right-3 top-3.5 flex">
        <KebabMenu
          anchor="right start"
          items={menuItems}
          className={cn('flex', {
            'hidden group-hover:flex': !isTouchDevice,
          })}
        />
      </div>
    </div>
  );
};
