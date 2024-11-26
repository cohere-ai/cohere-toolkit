import Link from 'next/link';

import { ToolDefinition } from '@/cohere-client';
import { StatusConnection } from '@/components/AgentSettingsForm/StatusConnection';
import { Button, Icon, IconName, Switch, Text } from '@/components/UI';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';

type Props = {
  tools?: ToolDefinition[];
  activeTools?: string[];
  setActiveTools: (tools: string[]) => void;
  handleAuthButtonClick: (toolName: string) => void;
};

export const ToolsStep: React.FC<Props> = ({
  tools,
  activeTools,
  setActiveTools,
  handleAuthButtonClick,
}) => {
  const availableTools = tools?.filter((tool) => tool.name && tool.is_available && tool.is_visible);

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
        ({ name, description, is_auth_required, auth_url, is_available, error_message }) =>
          !!name &&
          description && (
            <ToolRow
              key={name}
              name={name}
              description={description}
              icon={TOOL_ID_TO_DISPLAY_INFO[name]?.icon ?? TOOL_FALLBACK_ICON}
              checked={!!activeTools?.includes(name)}
              handleSwitch={(checked: boolean) => handleUpdateActiveTools(checked, name)}
              isAuthRequired={is_auth_required}
              authUrl={auth_url?.toString()}
              isAvailable={is_available}
              errorMessage={error_message}
              handleAuthButtonClick={handleAuthButtonClick}
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
  isAuthRequired?: boolean;
  authUrl?: string;
  isAvailable?: boolean;
  errorMessage?: string | null;
  handleAuthButtonClick?: (toolName: string) => void;
}> = ({
  name,
  description,
  icon,
  checked,
  handleSwitch,
  isAuthRequired,
  authUrl,
  isAvailable,
  errorMessage,
  handleAuthButtonClick,
}) => {
  return (
    <div className="flex flex-col space-y-1 rounded-md border p-4 dark:border-volcanic-300 dark:bg-volcanic-100">
      <div className="flex justify-between">
        <div className="flex items-center space-x-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-sm bg-marble-800 dark:bg-volcanic-200">
            <Icon name={icon} kind="outline" size="sm" />
          </div>
          <Text styleAs="label" className="font-medium">
            {name}
          </Text>
        </div>
        {isAvailable && (
          <div className="flex items-center space-x-2">
            <Switch
              checked={checked}
              onChange={(checked: boolean) => !!name && handleSwitch(checked)}
              showCheckedState
            />
          </div>
        )}
      </div>
      <Text className="dark:text-marble-800">{description}</Text>
      {!isAuthRequired && !!authUrl && <StatusConnection connected={!isAuthRequired} />}
      {!isAvailable && (
        <Text styleAs="caption" className="dark:text-danger-500">
          {errorMessage ||
            'Connection is not available. Please set the required configuration parameters.'}
        </Text>
      )}
      {isAuthRequired && !!authUrl && isAvailable && (
        <Button
          kind="outline"
          theme="mushroom"
          label="Authenticate"
          onClick={() => (handleAuthButtonClick ? handleAuthButtonClick(name) : '')}
        />
      )}
    </div>
  );
};
