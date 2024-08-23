'use client';

import ToolCard from '@/components/Tools/ToolCard';
import { Icon, IconButton, Text } from '@/components/UI';
import { useAgent, useAvailableTools, useChatRoutes, useListTools } from '@/hooks';
import { useSettingsStore } from '@/stores';

type Props = {};

export const KnowledgePanel: React.FC<Props> = () => {
  const { setRightPanelOpen } = useSettingsStore();
  const { agentId } = useChatRoutes();
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { knowledgeTools } = useAvailableTools({ agent, managedTools: tools });

  return (
    <aside className="space-y-5 py-4">
      <header className="flex items-center gap-2">
        <IconButton
          onClick={() => setRightPanelOpen(false)}
          iconName="arrow-right"
          className="flex h-auto flex-shrink-0 self-center lg:hidden"
        />
        <Text styleAs="p-sm" className="font-medium uppercase">
          Assistant Knowledge
        </Text>
      </header>
      <Text styleAs="caption" className="my-6 text-volcanic-600">
        This assistant uses data from following apps.
      </Text>
      <div className="flex flex-col gap-y-2">
        {knowledgeTools.map((tool) => (
          <div key={tool.name} className="flex items-center gap-2">
            <ToolCard key={tool.name} tool={tool} />
          </div>
        ))}
      </div>
    </aside>
  );
};
