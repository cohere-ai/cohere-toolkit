import Link from 'next/link';
import { useMemo } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ASSISTANT_SETTINGS_FORM } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { Icon, Switch, Text } from '@/components/Shared';
import { DATA_SOURCE_TOOLS, TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';

type Props = {
  fields: ASSISTANT_SETTINGS_FORM;
  tools?: ManagedTool[];
  setTools: (tools: string[]) => void;
};

export const ToolsStep: React.FC<Props> = ({ fields, tools, setTools }) => {
  const availableTools = useMemo(
    () =>
      tools
        ?.filter((t) => t.name && t.is_available && !DATA_SOURCE_TOOLS.includes(t.name))
        .map((tool) => ({
          ...tool,
          icon: tool.name ? TOOL_ID_TO_DISPLAY_INFO[tool.name].icon : TOOL_FALLBACK_ICON,
        })) ?? [],
    [tools]
  );

  const handleToolSwitch = (name: string, enabled: boolean) => {
    if (enabled) {
      setTools([...(fields.tools ?? []), name]);
    } else {
      setTools([...fields.tools.filter((tool) => tool !== name)]);
    }
  };

  return (
    <div className="flex flex-col space-y-3">
      {availableTools?.map((tool, i) => (
        <div
          key={i}
          className="flex flex-col space-y-4 rounded-md border p-4 dark:border-volcanic-300 dark:bg-volcanic-100"
        >
          <div className="flex justify-between">
            <div className="flex space-x-2">
              <Icon
                name={tool.icon}
                kind="outline"
                className="dark:bg-volcanic-20 h-5 w-5 rounded-sm"
              />
              <Text styleAs="label" className="font-medium">
                {tool.name}
              </Text>
            </div>
            <Switch
              checked={false}
              onChange={(checked: boolean) => !!tool.name && handleToolSwitch(tool.name, checked)}
            />
          </div>
          <Text>{tool.description}</Text>
        </div>
      ))}
      <Text className="dark:text-marble-800">
        Don&quot;t see the tool you need? <Link href="">Make a request</Link>
      </Text>
    </div>
  );
};
