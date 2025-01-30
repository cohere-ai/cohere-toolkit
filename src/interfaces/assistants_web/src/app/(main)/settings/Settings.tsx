'use client';

import { PropsWithChildren, useState } from 'react';

import { StatusConnection } from '@/components/AgentSettingsForm/StatusConnection';
import { MobileHeader } from '@/components/Global';
import {
  Button,
  DarkModeToggle,
  Icon,
  IconName,
  ShowCitationsToggle,
  ShowStepsToggle,
  Tabs,
  Text,
} from '@/components/UI';
import { TOOL_GITHUB_ID, TOOL_GMAIL_ID, TOOL_SLACK_ID } from '@/constants';
import { useDeleteAuthTool, useListTools, useNotify } from '@/hooks';
import { cn, getToolAuthUrl } from '@/utils';

const tabs: { key: string; icon: IconName; label: string }[] = [
  { key: 'connections', icon: 'users-three', label: 'Connections' },
  { key: 'appearance', icon: 'sun', label: 'Appearance' },
  { key: 'advanced', icon: 'settings', label: 'Advanced' },
  { key: 'profile', icon: 'profile', label: 'Profile' },
];

const Settings = () => {
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);

  return (
    <div className="flex h-full w-full flex-grow flex-col overflow-y-auto rounded-lg border border-marble-950 bg-marble-980 dark:border-volcanic-100 dark:bg-volcanic-100 md:ml-0">
      <header className={cn('border-b border-marble-950 bg-cover dark:border-volcanic-200', 'px-4 py-6 lg:px-10 lg:py-10', 'flex flex-col gap-y-3')}>
        <MobileHeader />
        <div className="flex items-center gap-2">
          <Text styleAs="h4" className="text-volcanic-400 dark:text-mushroom-950">Settings</Text>
        </div>
      </header>
      <section className="p-8">
        <Tabs
          tabs={tabs.map(tab => (
            <div className="flex items-center gap-2" key={tab.key}>
              <Icon name={tab.icon} kind="outline" />
              <Text>{tab.label}</Text>
            </div>
          ))}
          selectedIndex={selectedTabIndex}
          onChange={setSelectedTabIndex}
          tabGroupClassName="h-full"
          tabClassName="pt-2.5"
          panelsClassName="pt-7 lg:pt-7 px-0 flex flex-col rounded-b-lg md:rounded-b-none"
          fitTabsContent
        >
          <Connections />
          <Appearance />
          <Advanced />
          <Profile />
        </Tabs>
      </section>
    </div>
  );
};

const Wrapper: React.FC<PropsWithChildren> = ({ children }) => (
  <div className="max-w-screen-xl flex-grow overflow-y-auto">{children}</div>
);

const Connections = () => (
  <Wrapper>
    <Text styleAs="h5" className="mb-6">Connections your assistants can access</Text>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <GoogleDriveConnection />
      <SlackConnection />
      <GmailConnection />
      <GithubConnection />
    </div>
  </Wrapper>
);

const Appearance = () => (
  <Wrapper>
    <Text styleAs="h5" className="mb-6">Mode</Text>
    <DarkModeToggle />
  </Wrapper>
);

const Advanced = () => (
  <Wrapper>
    <Text styleAs="h5" className="mb-6">Advanced</Text>
    <ShowStepsToggle />
    <ShowCitationsToggle />
  </Wrapper>
);

const Profile = () => (
  <Wrapper>
    <Text styleAs="h5" className="mb-6">User Profile</Text>
    <Button label="Log out" href="/logout" kind="secondary" icon="sign-out" theme="default" />
  </Wrapper>
);

const ConnectionComponent = ({ toolId, toolName, iconName, description, showSyncButton }: { toolId: string; toolName: string; iconName: IconName; description: string; showSyncButton: boolean }) => {
  const { data } = useListTools();
  const { mutateAsync: deleteAuthTool } = useDeleteAuthTool();
  const notify = useNotify();
  const tool = data?.find(tool => tool.name === toolId);

  if (!tool) return null;

  const handleDeleteAuthTool = async () => {
    try {
      await deleteAuthTool(tool.name!);
    } catch {
      notify.error(`Failed to delete ${toolName} connection`);
    }
  };

  const isConnected = !(tool.is_auth_required ?? false);
  const isAvailable = tool.is_available ?? false;
  const error = tool.error_message ?? '';
  const authUrl = getToolAuthUrl(tool.auth_url);

  return (
    <article className="rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name={iconName} size="xl" />
          <Text className="text-volcanic-400 dark:text-mushroom-950">{toolName}</Text>
        </div>
        <StatusConnection connected={isConnected} />
      </header>
      <Text className="mb-6 text-volcanic-400 dark:text-mushroom-800">{description}</Text>
      <section>
        {!isAvailable ? (
          <div className="justify-items-start space-y-6">
            <div className="flex items-center justify-between">
              <p className="font-body text-p-sm uppercase text-danger-500">{error || `${toolName} connection is not available.`}</p>
            </div>
          </div>
        ) : isConnected ? (
          <div className="space-y-6">
            {showSyncButton && <Button label="Sync now" kind="secondary" icon="arrow-clockwise" href={authUrl} />}
            <Button label="Delete connection" kind="secondary" icon="trash" theme="danger" onClick={handleDeleteAuthTool} />
          </div>
        ) : (
          <Button label="Authenticate" href={authUrl} kind="secondary" theme="default" icon="arrow-up-right" />
        )}
      </section>
    </article>
  );
};

const GoogleDriveConnection = () => (
  <ConnectionComponent
    toolId="google_drive"
    toolName="Google Drive"
    iconName="google-drive"
    description="Connect to Google Drive and add files to the assistant"
    showSyncButton={true}
  />
);

const SlackConnection = () => (
  <ConnectionComponent
    toolId={TOOL_SLACK_ID}
    toolName="Slack"
    iconName="slack"
    description="Connect to Slack"
    showSyncButton={false}
  />
);

const GmailConnection = () => (
  <ConnectionComponent
    toolId={TOOL_GMAIL_ID}
    toolName="Gmail"
    iconName="gmail"
    description="Connect to Gmail"
    showSyncButton={false}
  />
);

const GithubConnection = () => (
  <ConnectionComponent
    toolId={TOOL_GITHUB_ID}
    toolName="Github"
    iconName="github"
    description="Connect to Github"
    showSyncButton={false}
  />
);

export { Settings };