'use client';

import { PropsWithChildren, useDeferredValue, useState } from 'react';

import { Agent, Conversation, ConversationWithoutMessages } from '@/cohere-client';
import { DiscoverAgentCard } from '@/components/Agents/DiscoverAgentCard';
import { Button, Icon, Input, Tabs, Text, Tooltip } from '@/components/Shared';
import { useListAgents } from '@/hooks/agents';
import { useConversations } from '@/hooks/conversation';
import { cn } from '@/utils';

const tabs = [
  <div className="flex items-center gap-2" key="company">
    <Icon name="users-three" kind="outline" />
    <Text>Company</Text>
  </div>,
  <div className="flex items-center gap-2" key="private">
    <Icon name="profile" kind="outline" />
    <Text>Private</Text>
  </div>,
];

export const DiscoverAgents = () => {
  const { data: agents = [] } = useListAgents();
  const { data: conversations = [] } = useConversations({});
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);

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
          <Tooltip label="tbd" hover size="sm">
            <Icon
              name="information"
              kind="outline"
              className="fill-volcanic-300 dark:fill-mushroom-700"
            />
          </Tooltip>
        </div>
        <Button kind="secondary" theme="default" icon="add" label="Create Assistant" href="/new" />
      </header>
      <section className="p-8">
        <Tabs
          tabs={tabs}
          selectedIndex={selectedTabIndex}
          onChange={setSelectedTabIndex}
          tabGroupClassName="h-full"
          tabClassName="pt-2.5"
          panelsClassName="pt-7 lg:pt-7 px-0 flex flex-col rounded-b-lg bg-marble-980 dark:bg-volcanic-100 md:rounded-b-none"
          fitTabsContent
        >
          <CompanyAgents agents={agents} conversations={conversations} />
          <PrivateAgents agents={agents} />
        </Tabs>
      </section>
    </div>
  );
};

const Wrapper: React.FC<PropsWithChildren> = ({ children }) => (
  <div className="max-w-screen-xl flex-grow overflow-y-auto py-10">{children}</div>
);

const GroupAgents: React.FC<{ agents: Agent[]; title: string; subTitle: string }> = ({
  agents,
  title,
  subTitle,
}) => {
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
        <Text className="dark:text-marble-800">{subTitle}</Text>
      </header>
      <div className="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-3 xl:grid-cols-4">
        {visibleAgents.map((agent) => (
          <DiscoverAgentCard key={agent.id} {...agent} isBaseAgent={agent.id === 'default'} />
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
  agents: Agent[];
  conversations: ConversationWithoutMessages[];
}> = ({ agents, conversations }) => {
  const [query, setQuery] = useState('');
  const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value);
  const deferredQuery = useDeferredValue(query);

  const filteredAgents = agents
    .filter((agent) => agent.name.toLowerCase().includes(deferredQuery.toLowerCase()))
    .sort((a, b) => b.name.toLowerCase().localeCompare(a.name.toLowerCase()));

  const usedByMeAgents = conversations
    .sort((a, b) => parseInt(b.updated_at) - parseInt(a.updated_at))
    .map((c) => filteredAgents.find((a) => a.id === c.agent_id))
    .filter((agent) => !!agent)
    .filter((agent, index, self) => self.findIndex((a) => a.id === agent.id) === index);

  const mostUsedAgents = conversations.reduce((acc, c) => {
    if (!c.agent_id) {
      return acc;
    }
    if (!acc[c.agent_id]) {
      acc[c.agent_id] = 0;
    } else {
      acc[c.agent_id]++;
    }
    return acc;
  }, {} as Record<string, number>);
  const trendingAgents: Agent[] = Object.keys(mostUsedAgents)
    .sort((a, b) => mostUsedAgents[b] - mostUsedAgents[a])
    .map((id) => filteredAgents.find((a) => a.id === id))
    .filter((agent) => !!agent);

  const featuredAgents = filteredAgents.filter((agent) => agent.id === 'default');

  return (
    <Wrapper>
      <div className="space-y-10">
        <Input
          placeholder="Search Assistants"
          type="text"
          onChange={handleOnChange}
          value={query}
        />
        <GroupAgents
          title="Used by me"
          subTitle="Assistants that you regularly use"
          agents={usedByMeAgents}
        />
        <GroupAgents
          title="Trending"
          subTitle="Most popular assistants from your company"
          agents={trendingAgents}
        />
        <GroupAgents
          title="Featured"
          subTitle="Official recommended assistants"
          agents={featuredAgents}
        />
        <GroupAgents
          title="All assistants"
          subTitle="All available assistants"
          agents={filteredAgents}
        />
      </div>
    </Wrapper>
  );
};

const PrivateAgents: React.FC<{ agents: Agent[] }> = () => {
  return <Wrapper>tbd</Wrapper>;
};
