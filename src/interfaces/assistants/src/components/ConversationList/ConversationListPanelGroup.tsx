'use client';

import { useMemo } from 'react';
import { Flipped, Flipper } from 'react-flip-toolkit';

import { ConversationWithoutMessages as Conversation } from '@/cohere-client';
import {
  ConversationCard,
  ConversationListItem,
} from '@/components/ConversationList/ConversationCard';
import { Text } from '@/components/Shared';
import { useConversationStore } from '@/stores';
import { getWeeksAgo } from '@/utils/format';

type Props = {
  conversations: Conversation[];
  checkedConversations: Set<string>;
  onCheckConversation: (id: string) => void;
  showWeekHeadings?: boolean;
  className?: string;
};

/**
 * Renders a list of conversations that are subgrouped by when it was last
 * updated by weeks ago.
 *
 * @param {Conversation[]} props.conversations list of conversations, **must be sorted by date**
 */
export const ConversationListPanelGroup: React.FC<Props> = ({
  conversations,
  checkedConversations,
  onCheckConversation,
  showWeekHeadings = true,
  className = '',
}) => {
  const {
    conversation: { id: selectedConversationId },
  } = useConversationStore();

  const { items, flipKey } = useMemo(() => {
    let latestWeekHeading = '';
    const itemsWithTitles: ConversationListItem[] = [];

    conversations.forEach((c) => {
      const { weeksAgo, weeksAgoStr } = getWeeksAgo(c.updated_at ?? '');

      if (weeksAgo > 1 && weeksAgoStr !== latestWeekHeading && showWeekHeadings) {
        latestWeekHeading = weeksAgoStr;
        // Insert dummy conversation to show weeks ago title, we keep the same structure
        // because we want to make sure the list is still sorted by date.
        itemsWithTitles.push({
          weekHeading: weeksAgoStr,
          updatedAt: c.updated_at,
          conversationId: weeksAgoStr,
          title: weeksAgoStr,
          description: weeksAgoStr,
        });
      }
      itemsWithTitles.push({
        updatedAt: c.updated_at,
        conversationId: c.id,
        title: c.title,
        description: c.description,
      });
    });

    // Used to determine if the order of the conversations has changed and we should animate
    const flipKey = itemsWithTitles.map((c) => c.weekHeading ?? c.conversationId).join('');

    return { items: itemsWithTitles, flipKey };
  }, [conversations, showWeekHeadings]);

  return (
    <Flipper flipKey={flipKey} className={className}>
      {items.map((c) => {
        const { conversationId: currentId } = c;
        const isConversationActive = currentId === selectedConversationId;

        if (c.weekHeading) {
          if (!showWeekHeadings) return null;
          return (
            <Flipped key={c.weekHeading} flipId={c.weekHeading}>
              {(flippedProps) => (
                <Text
                  as="div"
                  styleAs="label"
                  className="pb-1 pl-[26px] pr-3 pt-4 text-volcanic-500"
                  {...flippedProps}
                >
                  {c.weekHeading}
                </Text>
              )}
            </Flipped>
          );
        }

        return (
          <Flipped key={currentId} flipId={currentId}>
            {(flippedProps) => (
              <ConversationCard
                flippedProps={flippedProps}
                conversation={c}
                key={currentId}
                showCheckbox={checkedConversations.size > 0}
                isChecked={checkedConversations.has(currentId ?? '')}
                isActive={isConversationActive}
                onCheck={onCheckConversation}
              />
            )}
          </Flipped>
        );
      })}
    </Flipper>
  );
};
