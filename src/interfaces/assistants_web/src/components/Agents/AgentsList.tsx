'use client';

import { useMemo, useState } from 'react';

import { ConversationWithoutMessages as Conversation } from '@/cohere-client';
import { AgentCard } from '@/components/Agents/AgentCard';
import { ConversationListLoading } from '@/components/ConversationList/ConversationListLoading';
import { ConversationListPanelGroup } from '@/components/ConversationList/ConversationListPanelGroup';
import { Icon, Input, Text } from '@/components/Shared';
import { useRecentAgents } from '@/hooks/agents';
import { useConversations } from '@/hooks/conversation';
import { useSearchConversations } from '@/hooks/search';

const sortByDate = (a: Conversation, b: Conversation) => {
  return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
};

/**
 * @description This component renders a list of agents.
 * It shows the most recent agents and the base agents.
 */
export const AgentsList: React.FC = () => {
  const { recentAgents } = useRecentAgents();
  const { data: conversations } = useConversations({});
  const { search, setSearch, searchResults } = useSearchConversations(conversations);

  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-2">
        <Text styleAs="label" className="truncate text-mushroom-800">
          Recent Assistants
        </Text>
        <div className="flex gap-1">
          <AgentCard name="Command R+" isBaseAgent />
          {recentAgents
            .filter((agent, idx, array) => array.findIndex((a) => a.id === agent.id) === idx)
            .slice(0, 5)
            .map((agent) => (
              <AgentCard key={agent.id} name={agent.name} id={agent.id} />
            ))}
        </div>
      </section>
      <section className="space-y-4">
        <Input
          placeholder="Search chat history"
          theme="secondary"
          actionType="search"
          kind="default"
          size="sm"
          maxLength={40}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onClear={() => setSearch('')}
        />
        <Text styleAs="label" className="truncate text-mushroom-800">
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
      className="space-y-1"
    />
  );
};
