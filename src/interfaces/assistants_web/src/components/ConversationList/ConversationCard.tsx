'use client';

import Link from 'next/link';

import { AgentPublic } from '@/cohere-client';
import { KebabMenu, KebabMenuItem } from '@/components/KebabMenu';
import { ShareModal } from '@/components/ShareModal';
import { CoralLogo, Text, Tooltip } from '@/components/Shared';
import { useContextStore } from '@/context';
import { useBrandedColors } from '@/hooks/brandedColors';
import { getIsTouchDevice, useIsDesktop } from '@/hooks/breakpoint';
import { useConversationActions } from '@/hooks/conversation';
import { useFileActions } from '@/hooks/files';
import { useConversationStore, useSettingsStore } from '@/stores';
import { cn, formatDateToShortDate } from '@/utils';

export type ConversationListItem = {
  conversationId: string;
  updatedAt: string;
  title: string;
  description: string | null;
  weekHeading?: string;
  agent?: AgentPublic;
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

const useMenuItems = ({ conversationId }: { conversationId: string }) => {
  const { deleteConversation } = useConversationActions();
  const { open } = useContextStore();

  const handleOpenShareModal = () => {
    if (!conversationId) return;
    open({
      title: 'Share link to conversation',
      content: <ShareModal conversationId={conversationId} />,
    });
  };

  const menuItems: KebabMenuItem[] = [
    {
      label: 'Share Chat',
      iconName: 'share',
      onClick: handleOpenShareModal,
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

export const ConversationCard: React.FC<Props> = ({ isActive, conversation, flippedProps }) => {
  const { title, conversationId } = conversation;
  const {
    conversation: { id: selectedConversationId, name: conversationName },
    setConversation,
  } = useConversationStore();
  const { isAgentsLeftPanelOpen, setAgentsLeftSidePanelOpen } = useSettingsStore();
  const isDesktop = useIsDesktop();
  const isTouchDevice = getIsTouchDevice();
  const { clearComposerFiles } = useFileActions();
  const { bg, contrastText, contrastFill } = useBrandedColors(conversation.agent?.id);

  // if the conversation card is for the selected conversation we use the `conversationName`
  // from the context store, otherwise we use the name from the conversation object
  // this is to ensure that we use the typed animation
  // @see "handleUpdateConversationTitle" in hooks/chat.ts
  const name = conversationId === selectedConversationId ? conversationName : title;

  const menuItems = useMenuItems({ conversationId });

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
          className={cn(
            'flex size-4 flex-shrink-0 items-center justify-center rounded',
            bg,
            contrastText
          )}
        >
          {conversation.agent ? (
            <Text className={contrastText} styleAs="p-xs">
              {conversation.agent.name[0]}
            </Text>
          ) : (
            <CoralLogo className={cn('scale-50', contrastFill)} />
          )}
        </div>
        <Text styleAs="p-sm" className="truncate text-volcanic-500 dark:text-mushroom-800">
          {conversation.agent?.name ?? 'Cohere AI'}
        </Text>
        <Text styleAs="code-sm" className="ml-auto mt-0.5 uppercase dark:text-mushroom-800">
          {formatDateToShortDate(conversation.updatedAt)}
        </Text>
      </div>
    </div>
  );

  const conversationUrl = conversation.agent
    ? `/a/${conversation.agent.id}/c/${conversationId}`
    : `/c/${conversationId}`;

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
          setAgentsLeftSidePanelOpen(false);
          clearComposerFiles();
        }}
        className={wrapperClassName}
      >
        {info}
      </Link>
    );

  if (!isAgentsLeftPanelOpen) {
    const content = (
      <div
        className={cn(
          'flex size-8 flex-shrink-0 items-center justify-center rounded',
          bg,
          contrastText
        )}
      >
        {conversation.agent ? (
          <Text>{conversation.agent.name[0]}</Text>
        ) : (
          <CoralLogo className={contrastFill} />
        )}
      </div>
    );
    return (
      <div {...flippedProps}>
        <Tooltip label={conversation.title} placement={'bottom-end'} hover size="sm">
          {isActive && isDesktop ? (
            <div className="select-none">{content}</div>
          ) : (
            <Link
              href={conversationUrl}
              key={conversationId}
              shallow
              onClick={() => {
                setConversation({ id: conversationId, name });
                setAgentsLeftSidePanelOpen(false);
              }}
            >
              {content}
            </Link>
          )}
        </Tooltip>
      </div>
    );
  }

  return (
    <div
      {...flippedProps}
      className={cn('group relative flex w-full rounded-lg', 'flex items-start gap-x-1', {
        'transition-colors ease-in-out hover:bg-white dark:hover:bg-volcanic-200': !isActive,
        'bg-white dark:bg-volcanic-200': isActive,
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
