'use client';

import { useMemo, useState } from 'react';

import { ConversationWithoutMessages as Conversation } from '@/cohere-client';
import { AgentCard } from '@/components/Agents/AgentCard';
import { ConversationListLoading } from '@/components/ConversationList/ConversationListLoading';
import { ConversationListPanelGroup } from '@/components/ConversationList/ConversationListPanelGroup';
import { IconButton } from '@/components/IconButton';
import { Icon, Text } from '@/components/Shared';
import { InputSearch } from '@/components/Shared/InputSearch';
import { useListAgents } from '@/hooks/agents';
import { useConversations } from '@/hooks/conversation';
import { useSearchConversations } from '@/hooks/search';
import { useAgentsStore } from '@/stores';
import { cn } from '@/utils';

const sortByDate = (a: Conversation, b: Conversation) => {
  return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
};

/**
 * @description This component renders a list of agents.
 * It shows the most recent agents and the base agents.
 */
export const AgentsList: React.FC = () => {
  const { data: conversations } = useConversations({});
  const { search, setSearch, searchResults } = useSearchConversations(conversations);
  const { data: agents = [] } = useListAgents();
  const {
    agents: { isAgentsSidePanelOpen },
    setAgentsSidePanelOpen,
  } = useAgentsStore();
  const recentAgents = useMemo(
    () =>
      conversations
        .sort(sortByDate)
        .map((conversation) => agents.find((agent) => agent.id === conversation.agent_id))
        .filter((agent, index, self) => self.indexOf(agent) === index),
    [agents, conversations]
  );

  return (
    <div className="flex flex-col gap-8">
      <section
        className={cn('flex flex-col gap-2', {
          hidden: !isAgentsSidePanelOpen,
        })}
      >
        <Text styleAs="label" className="truncate dark:text-mushroom-800">
          Recent Assistants
        </Text>
        <div className="flex gap-1">
          {recentAgents.slice(0, 5).map((agent) => {
            if (!agent) return <AgentCard key="commandR+" name="Command R+" isBaseAgent />;
            return <AgentCard key={agent.id} name={agent.name} id={agent.id} />;
          })}
        </div>
      </section>
      <section className={cn('flex flex-col gap-4', { 'items-center': !isAgentsSidePanelOpen })}>
        {isAgentsSidePanelOpen ? (
          <InputSearch
            placeholder="Search chat history"
            value={search}
            onChange={setSearch}
            maxLength={40}
          />
        ) : (
          <IconButton
            iconName="search"
            iconClassName="dark:text-mushroom-950"
            onClick={() => setAgentsSidePanelOpen(true)}
            tooltip={{ label: 'Search' }}
          />
        )}
        <Text
          styleAs="label"
          className={cn('truncate dark:text-mushroom-800', {
            hidden: !isAgentsSidePanelOpen,
          })}
        >
          Recent Chats
        </Text>
        <RecentChats search={search} results={searchResults} />
      </section>
    </div>
  );
};

const RecentChats: React.FC<{ search: string; results: Conversation[] }> = ({
  search,
  results,
}) => {
  const { data: conversations, isLoading: isConversationsLoading, isError } = useConversations({});
  const {
    agents: { isAgentsSidePanelOpen },
  } = useAgentsStore();
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

  if (isError) {
    return (
      <span className="my-auto flex flex-col items-center gap-2 text-center">
        <Icon name="warning" />
        <Text>Unable to load conversations.</Text>
      </span>
    );
  }

  if (hasSearchQuery && !hasSearchResults) {
    return (
      <Text as="span" className="line-clamp-3">
        No results found for &quot;{search}&quot;.
      </Text>
    );
  }

  if (!hasConversations) {
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
      className={cn('space-y-1', { 'space-y-2': !isAgentsSidePanelOpen })}
    />
  );
};
