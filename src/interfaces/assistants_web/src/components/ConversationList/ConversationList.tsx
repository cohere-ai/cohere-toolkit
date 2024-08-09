'use client';

import { useMemo, useState } from 'react';

import { ConversationWithoutMessages as Conversation } from '@/cohere-client';
import { AgentCard } from '@/components/Agents/AgentCard';
import { ConversationListLoading } from '@/components/ConversationList/ConversationListLoading';
import { ConversationListPanelGroup } from '@/components/ConversationList/ConversationListPanelGroup';
import { Icon, Text, Tooltip } from '@/components/Shared';
import { InputSearch } from '@/components/Shared/InputSearch';
import { useRecentAgents } from '@/hooks/agents';
import { useConversations } from '@/hooks/conversation';
import { useSearchConversations } from '@/hooks/search';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const sortByDate = (a: Conversation, b: Conversation) => {
  return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
};

/**
 * @description This component renders a list of agents.
 * It shows the most recent agents and the base agents.
 */
export const ConversationList: React.FC = () => {
  const { data: conversations = [] } = useConversations({});
  const { search, setSearch, searchResults } = useSearchConversations(conversations);
  const { isAgentsLeftPanelOpen, setAgentsLeftSidePanelOpen } = useSettingsStore();
  const recentAgents = useRecentAgents();

  return (
    <>
      <div className="flex flex-col gap-8">
        <section
          className={cn('flex flex-col gap-2', {
            hidden: !isAgentsLeftPanelOpen,
          })}
        >
          <Text styleAs="label" className="truncate dark:text-mushroom-800">
            Recent Assistants
          </Text>
          <div className="flex gap-1 overflow-y-auto">
            {recentAgents.map((agent) => (
              <AgentCard
                key={agent.id || agent.name}
                name={agent.name}
                id={agent.id}
                isBaseAgent={!agent.id}
              />
            ))}
          </div>
        </section>
        <section className={cn('flex flex-col gap-4', { 'items-center': !isAgentsLeftPanelOpen })}>
          {isAgentsLeftPanelOpen ? (
            <InputSearch
              placeholder="Search chat history"
              value={search}
              onChange={setSearch}
              maxLength={40}
            />
          ) : (
            <Tooltip label="Search" hover size="sm">
              <button onClick={() => setAgentsLeftSidePanelOpen(true)}>
                <Icon name="search" kind="outline" className="dark:fill-marble-950" />
              </button>
            </Tooltip>
          )}
        </section>
      </div>
      <div
        className={cn('flex-grow', {
          'space-y-4 overflow-y-auto': conversations.length > 0,
        })}
      >
        <Text
          styleAs="label"
          className={cn('truncate dark:text-mushroom-800', {
            hidden: !isAgentsLeftPanelOpen,
          })}
        >
          Recent Chats
        </Text>
        <RecentChats search={search} results={searchResults} />
      </div>
    </>
  );
};

const RecentChats: React.FC<{ search: string; results: Conversation[] }> = ({
  search,
  results,
}) => {
  const {
    data: conversations = [],
    isLoading: isConversationsLoading,
    isError,
  } = useConversations({});
  const { isAgentsLeftPanelOpen } = useSettingsStore();
  const [checkedConversations, setCheckedConversations] = useState<Set<string>>(new Set());
  const hasSearchQuery = search.length > 0;
  const hasSearchResults = results.length > 0;
  const hasConversations = conversations.length > 0;
  const displayedConversations = useMemo<Conversation[]>(() => {
    return search ? results : conversations.sort(sortByDate);
  }, [results, conversations, search]);

  const handleCheckConversationToggle = (id: string) => {
    const newCheckedConversations = new Set(checkedConversations);
    if (!newCheckedConversations.delete(id)) {
      newCheckedConversations.add(id);
    }
    setCheckedConversations(newCheckedConversations);
  };

  if (isConversationsLoading) {
    return <ConversationListLoading />;
  }

  if (isError && isAgentsLeftPanelOpen) {
    return (
      <span className="my-auto flex flex-col items-center gap-2 text-center">
        <Icon name="warning" />
        <Text>Unable to load conversations.</Text>
      </span>
    );
  }

  if (hasSearchQuery && !hasSearchResults && isAgentsLeftPanelOpen) {
    return (
      <Text as="span" className="line-clamp-3">
        No results found for &quot;{search}&quot;.
      </Text>
    );
  }

  if (!hasConversations && isAgentsLeftPanelOpen) {
    return (
      <span className="flex h-full w-full items-center justify-center text-volcanic-500">
        <Text>It&apos;s quiet here... for now</Text>
      </span>
    );
  }

  return (
    <ConversationListPanelGroup
      conversations={displayedConversations}
      showWeekHeadings={!hasSearchQuery}
      checkedConversations={checkedConversations}
      onCheckConversation={handleCheckConversationToggle}
      className={cn('flex flex-col items-center space-y-1', {
        'space-y-2': !isAgentsLeftPanelOpen,
      })}
    />
  );
};
