import Link from 'next/link';
import { useMemo } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ASSISTANT_SETTINGS_FORM } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { Icon, IconName, Switch, Text } from '@/components/Shared';
import { DATA_SOURCE_TOOLS, TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';

type Props = {
  pythonTool?: ManagedTool;
  webSearchTool?: ManagedTool;
  activeTools?: string[];
  setActiveTools: (tools?: string[]) => void;
};

export const ToolsStep: React.FC<Props> = ({
  pythonTool,
  webSearchTool,
  activeTools = [],
  setActiveTools,
}) => {
  const handleUpdateActiveTools = (checked: boolean, name?: string | null) => {
    if (!name) return;
    if (checked) {
      setActiveTools([...(activeTools ?? []), name]);
    } else {
      setActiveTools(activeTools.filter((t) => t !== name));
    }
  };

  return (
    <div className="flex flex-col space-y-3">
      {pythonTool && (
        <ToolRow
          name={pythonTool.name ?? 'Python Interpreter'}
          description={pythonTool.description ?? ''}
          icon="code-simple"
          checked={!!(pythonTool.name && activeTools.includes(pythonTool.name))}
          handleSwitch={(checked: boolean) => handleUpdateActiveTools(checked, pythonTool.name)}
        />
      )}
      {webSearchTool && (
        <ToolRow
          name={webSearchTool.name ?? 'Web Search'}
          description={webSearchTool.description ?? ''}
          icon="web"
          checked={!!(webSearchTool.name && activeTools.includes(webSearchTool.name))}
          handleSwitch={(checked: boolean) => handleUpdateActiveTools(checked, webSearchTool.name)}
        />
      )}
      <Text styleAs="caption" className="dark:text-marble-800">
        Don't see the tool you need?{' '}
        <Link className="underline" href="">
          Make a request
        </Link>
      </Text>
    </div>
  );
};

const ToolRow: React.FC<{
  name: string;
  description: string;
  icon: IconName;
  checked: boolean;
  handleSwitch: (checked: boolean) => void;
}> = ({ name, description, icon, checked, handleSwitch }) => {
  return (
    <div className="flex flex-col space-y-4 rounded-md border p-4 dark:border-volcanic-300 dark:bg-volcanic-100">
      <div className="flex justify-between">
        <div className="flex space-x-2">
          <Icon name={icon} kind="outline" className="dark:bg-volcanic-20 h-5 w-5 rounded-sm" />
          <Text styleAs="label" className="font-medium">
            {name}
          </Text>
        </div>
        <Switch
          checked={checked}
          onChange={(checked: boolean) => !!name && handleSwitch(checked)}
        />
      </div>
      <Text>{description}</Text>
    </div>
  );
};
