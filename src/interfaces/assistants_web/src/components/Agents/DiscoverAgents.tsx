'use client';

import { useDebouncedState } from '@react-hookz/web';
import { useEffect, useState } from 'react';

import { DiscoverAgentCard } from '@/components/Agents/DiscoverAgentCard';
import { Input, Text } from '@/components/Shared';
import { useListAgents } from '@/hooks/agents';
import { cn } from '@/utils';

const MAX_DEBOUNCE_TIME = 300;

export const DiscoverAgents = () => {
  const { data: agents = [] } = useListAgents();

  const [filterText, setFilterText] = useState('');
  const [filteredAgents, setFilteredAgents] = useDebouncedState(
    agents,
    MAX_DEBOUNCE_TIME,
    MAX_DEBOUNCE_TIME
  );

  useEffect(() => {
    if (!filterText) {
      setFilteredAgents(agents);
      return;
    }

    setFilteredAgents(
      agents.filter((agent) => agent.name.toLowerCase().includes(filterText.toLowerCase()))
    );
  }, [filterText, agents]);
  return (
    <div className="flex h-full w-full flex-grow flex-col overflow-y-auto rounded-lg border border-marble-950 bg-marble-1000 md:ml-0">
      <div
        className={cn(
          'border-b border-marble-950 bg-cover',
          'flex flex-shrink-0 flex-col gap-y-2',
          'bg-[url(/images/cellBackground.svg)]',
          'px-4 py-6 md:px-9 md:py-10 lg:px-10'
        )}
      >
        <Text styleAs="h4" className="text-volcanic-400">
          Discover Assistants
        </Text>
        <Text>
          Assistants created by your peers to help you solve tasks and increase efficiency
        </Text>
      </div>
      <div className="max-w-screen-xl flex-grow overflow-y-auto px-4 py-10 md:px-9 lg:px-10">
        <div className="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-2 xl:grid-cols-3">
          {agents.length >= 1 && (
            <>
              <Input
                size="sm"
                kind="default"
                actionType="search"
                placeholder="Search"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
              />
              <div className="col-span-2 hidden md:flex" />
            </>
          )}
          {'command r+'.includes(filterText.toLowerCase()) && (
            <DiscoverAgentCard
              isBaseAgent
              name="Command R+"
              description="Review, understand and ask questions about  internal financial documents."
            />
          )}
          {filteredAgents?.map((agent) => (
            <DiscoverAgentCard
              key={agent.name}
              description={agent.description ?? undefined}
              name={agent.name}
              id={agent.id}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
