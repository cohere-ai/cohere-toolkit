'use client';

import { useDeferredValue, useMemo, useState } from 'react';

import { AgentPublic, ConversationWithoutMessages } from '@/cohere-client';
import { DiscoverAgentCard } from '@/components/Agents/DiscoverAgentCard';
import { Button, Input, Text } from '@/components/Shared';
import { BASE_AGENT } from '@/constants';
import { useListAgents } from '@/hooks/agents';
import { useConversations } from '@/hooks/conversation';
import { useSession } from '@/hooks/session';
import { cn } from '@/utils';

const GROUPED_ASSISTANTS_LIMIT = 15;

export const DiscoverAgents = () => {
  const { data: agents = [] } = useListAgents();
  const { data: conversations = [] } = useConversations({});

  return (
    <div className="flex h-full w-full flex-grow flex-col overflow-y-auto rounded-lg border border-marble-950 bg-marble-980 md:ml-0 dark:border-volcanic-100 dark:bg-volcanic-100">
      <header
        className={cn(
          'border-b border-marble-950 bg-cover dark:border-volcanic-200',
          'px-4 py-6 md:px-9 md:py-10 lg:px-10',
          'flex items-center justify-between'
        )}
      >
        <div className="flex items-center gap-2">
          <Text styleAs="h4" className="text-volcanic-400 dark:text-mushroom-950">
            All Assistants
          </Text>
        </div>
        <Button kind="secondary" theme="default" icon="add" label="Create Assistant" href="/new" />
      </header>
      <section className="p-8">
        <CompanyAgents agents={agents.concat(BASE_AGENT)} conversations={conversations} />
      </section>
    </div>
  );
};

const GroupAgents: React.FC<{ agents: AgentPublic[]; title: string }> = ({ agents, title }) => {
  const hasShowMore = agents.length > 3;
  const [showMore, setShowMore] = useState(false);
  const handleShowMore = () => setShowMore((prev) => !prev);
  const visibleAgents = showMore ? agents : agents.slice(0, 3);

  return (
    <section className="space-y-6">
      <header>
        <Text styleAs="h5" className="dark:text-marble-1000">
          {title}
        </Text>
      </header>
      <div className="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-3 xl:grid-cols-4">
        {visibleAgents.map((agent) => (
          <DiscoverAgentCard key={agent.id} agent={agent} />
        ))}
      </div>
      {hasShowMore && (
        <Button
          kind="secondary"
          label={showMore ? 'Show less' : 'Show more'}
          theme="marble"
          onClick={handleShowMore}
          icon="chevron-down"
          iconPosition="end"
          iconOptions={{
            className: cn('transform duration-300', {
              'rotate-180': showMore,
            }),
          }}
        />
      )}
    </section>
  );
};

const CompanyAgents: React.FC<{
  agents: AgentPublic[];
  conversations: ConversationWithoutMessages[];
}> = ({ agents, conversations }) => {
  const [query, setQuery] = useState('');
  const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value);
  const deferredQuery = useDeferredValue(query);
  const session = useSession();

  const filteredAgents = useMemo(
    () =>
      agents
        .filter((agent) => agent.name.toLowerCase().includes(deferredQuery.toLowerCase()))
        .sort((a, b) => b.name.toLowerCase().localeCompare(a.name.toLowerCase())),
    [agents, deferredQuery]
  );

  const createdByMeAgents = useMemo(
    () => filteredAgents.filter((agent) => agent.user_id === session.userId),
    [filteredAgents, session.userId]
  );

  const recentlyUsedAgents = useMemo(
    () =>
      conversations
        .sort((a, b) => parseInt(b.updated_at) - parseInt(a.updated_at))
        .map((c) => filteredAgents.find((a) => a.id === c.agent_id))
        .filter((agent) => !!agent)
        .filter((agent, index, self) => self.findIndex((a) => a.id === agent.id) === index),
    [conversations, filteredAgents]
  );

  const mostUsedAgents = useMemo(
    () =>
      conversations.reduce((acc, c) => {
        if (!c.agent_id) {
          return acc;
        }
        if (!acc[c.agent_id]) {
          acc[c.agent_id] = 0;
        } else {
          acc[c.agent_id]++;
        }
        return acc;
      }, {} as Record<string, number>),
    [conversations]
  );

  const trendingAgents: AgentPublic[] = useMemo(
    () =>
      Object.keys(mostUsedAgents)
        .sort((a, b) => mostUsedAgents[b] - mostUsedAgents[a])
        .map((id) => filteredAgents.find((a) => a.id === id))
        .filter((agent) => !!agent)
        .filter((agent) => agent.user_id !== session.userId),
    [mostUsedAgents, filteredAgents, session.userId]
  );

  return (
    <div className="max-w-screen-xl flex-grow overflow-y-auto">
      <div className="space-y-10">
        <Input
          placeholder="Search Assistants"
          type="text"
          onChange={handleOnChange}
          value={query}
        />
        <GroupAgents title="Created by me" agents={createdByMeAgents} />
        {agents.length >= GROUPED_ASSISTANTS_LIMIT && (
          <>
            <GroupAgents title="Recently used" agents={recentlyUsedAgents} />
            <GroupAgents title="Trending" agents={trendingAgents} />
          </>
        )}
        <GroupAgents title="All assistants" agents={filteredAgents} />
      </div>
    </div>
  );
};
