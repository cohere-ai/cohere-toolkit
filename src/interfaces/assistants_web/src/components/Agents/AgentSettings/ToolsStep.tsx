import Link from 'next/link';

import { ManagedTool } from '@/cohere-client';
import { Icon, IconName, Switch, Text } from '@/components/Shared';
import { AGENT_SETTINGS_TOOLS, TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';

type Props = {
  tools?: ManagedTool[];
  activeTools?: string[];
  setActiveTools: (tools: string[]) => void;
};

export const ToolsStep: React.FC<Props> = ({ tools, activeTools, setActiveTools }) => {
  const availableTools = tools?.filter(
    (tool) => tool.name && AGENT_SETTINGS_TOOLS.includes(tool.name)
  );

  const handleUpdateActiveTools = (checked: boolean, name: string) => {
    if (checked) {
      setActiveTools([...(activeTools ?? []), name]);
    } else {
      setActiveTools(activeTools?.filter((t) => t !== name) ?? []);
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      {availableTools?.map(
        ({ name, description }) =>
          !!name &&
          description && (
            <ToolRow
              key={name}
              name={name}
              description={description}
              icon={TOOL_ID_TO_DISPLAY_INFO[name].icon ?? TOOL_FALLBACK_ICON}
              checked={!!activeTools?.includes(name)}
              handleSwitch={(checked: boolean) => handleUpdateActiveTools(checked, name)}
            />
          )
      )}
      <Text styleAs="caption" className="dark:text-marble-800">
        Don&lsquo;t see the tool you need? {/* TODO: get tool request link from Elaine */}
        <Link className="underline" onClick={() => alert('Needs to be developed!')} href="">
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
        <div className="flex items-center space-x-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-sm bg-marble-800 dark:bg-volcanic-200">
            <Icon name={icon} kind="outline" size="sm" />
          </div>
          <Text styleAs="label" className="font-medium">
            {name}
          </Text>
        </div>
        <Switch
          checked={checked}
          onChange={(checked: boolean) => !!name && handleSwitch(checked)}
        />
      </div>
      <Text className="dark:text-marble-800">{description}</Text>
    </div>
  );
};
