'use client';

import { PropsWithChildren, useState } from 'react';

import { StatusConnection } from '@/components/AgentSettingsForm/StatusConnection';
import { MobileHeader } from '@/components/Global';
import { Button, DarkModeToggle, Icon, ShowStepsToggle, Tabs, Text } from '@/components/UI';
import { TOOL_SLACK_ID } from '@/constants';
import { useDeleteAuthTool, useListTools, useNotify } from '@/hooks';
import { cn, getToolAuthUrl } from '@/utils';

const tabs = [
  <div className="flex items-center gap-2" key="company">
    <Icon name="users-three" kind="outline" />
    <Text>Connections</Text>
  </div>,
  <div className="flex items-center gap-2" key="company">
    <Icon name="sun" kind="outline" />
    <Text>Appearance</Text>
  </div>,
  <div className="flex items-center gap-2" key="company">
    <Icon name="settings" kind="outline" />
    <Text>Advanced</Text>
  </div>,
  <div className="flex items-center gap-2" key="private">
    <Icon name="profile" kind="outline" />
    <Text>Profile</Text>
  </div>,
];

export const Settings = () => {
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);

  return (
    <div className="flex h-full w-full flex-grow flex-col overflow-y-auto rounded-lg border border-marble-950 bg-marble-980 dark:border-volcanic-100 dark:bg-volcanic-100 md:ml-0">
      <header
        className={cn(
          'border-b border-marble-950 bg-cover dark:border-volcanic-200',
          'px-4 py-6 lg:px-10 lg:py-10',
          'flex flex-col gap-y-3'
        )}
      >
        <MobileHeader />
        <div className="flex items-center gap-2">
          <Text styleAs="h4" className="text-volcanic-400 dark:text-mushroom-950">
            Settings
          </Text>
        </div>
      </header>
      <section className="p-8">
        <Tabs
          tabs={tabs}
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
    <Text styleAs="h5" className="mb-6">
      Connections your assistants can access
    </Text>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <GoogleDriveConnection />
      <SlackConnection />
    </div>
  </Wrapper>
);

const Appearance = () => {
  return (
    <Wrapper>
      <Text styleAs="h5" className="mb-6">
        Mode
      </Text>
      <DarkModeToggle />
    </Wrapper>
  );
};

const Advanced = () => {
  return (
    <Wrapper>
      <Text styleAs="h5" className="mb-6">
        Advanced
      </Text>
      <ShowStepsToggle />
    </Wrapper>
  );
};

const Profile = () => {
  return (
    <Wrapper>
      <Text styleAs="h5" className="mb-6">
        User Profile
      </Text>
      <Button label="Log out" href="/logout" kind="secondary" icon="sign-out" theme="default" />
    </Wrapper>
  );
};

const GoogleDriveConnection = () => {
  const { data } = useListTools();
  const { mutateAsync: deleteAuthTool } = useDeleteAuthTool();
  const notify = useNotify();
  const googleDriveTool = data?.find((tool) => tool.name === 'google_drive');

  if (!googleDriveTool) {
    return null;
  }

  const handleDeleteAuthTool = async () => {
    try {
      await deleteAuthTool(googleDriveTool.name!);
    } catch (e) {
      notify.error('Failed to delete Google Drive connection');
    }
  };

  const isGoogleDriveConnected = !(googleDriveTool.is_auth_required ?? false);
  const authUrl = getToolAuthUrl(googleDriveTool.auth_url);

  return (
    <article className="rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name="google-drive" size="xl" />
          <Text className="text-volcanic-400 dark:text-mushroom-950">Google Drive</Text>
        </div>
        <StatusConnection connected={isGoogleDriveConnected} />
      </header>
      <Text className="mb-6 text-volcanic-400 dark:text-mushroom-800">
        Connect to Google Drive and add files to the assistant
      </Text>
      <section>
        {isGoogleDriveConnected ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <Text styleAs="p-sm" className="uppercase text-volcanic-400 dark:text-mushroom-950">
                Last Sync
              </Text>
              <Text styleAs="p-sm" className="uppercase text-volcanic-400 dark:text-mushroom-950">
                Aug 15, 2024 11:20 AM
              </Text>
            </div>
            <div className="flex items-center justify-between">
              <Button
                label="Sync now"
                kind="secondary"
                icon="arrow-clockwise"
                href={authUrl ?? ''}
              />
              <Button
                label="Delete connection"
                kind="secondary"
                icon="trash"
                theme="danger"
                onClick={handleDeleteAuthTool}
              />
            </div>
          </div>
        ) : (
          <Button
            label="Authenticate"
            href={getToolAuthUrl(googleDriveTool.auth_url)}
            kind="secondary"
            theme="default"
            icon="arrow-up-right"
          />
        )}
      </section>
    </article>
  );
};
const SlackConnection = () => {
  const { data } = useListTools();
  const { mutateAsync: deleteAuthTool } = useDeleteAuthTool();
  const notify = useNotify();
  const slackTool = data?.find((tool) => tool.name === TOOL_SLACK_ID);

  if (!slackTool) {
    return null;
  }

  const handleDeleteAuthTool = async () => {
    try {
      await deleteAuthTool(slackTool.name!);
    } catch (e) {
      notify.error('Failed to delete Slack connection');
    }
  };

  const isSlackConnected = !(slackTool.is_auth_required ?? false);

  return (
    <article className="rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name="slack" size="xl" />
          <Text className="text-volcanic-400 dark:text-mushroom-950">Slack</Text>
        </div>
        <StatusConnection connected={isSlackConnected} />
      </header>
      <Text className="mb-6 text-volcanic-400 dark:text-mushroom-800">Connect to Slack</Text>
      <section>
        {isSlackConnected ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <Button
                label="Delete connection"
                kind="secondary"
                icon="trash"
                theme="danger"
                onClick={handleDeleteAuthTool}
              />
            </div>
          </div>
        ) : (
          <Button
            label="Authenticate"
            href={getToolAuthUrl(slackTool.auth_url)}
            kind="secondary"
            theme="default"
            icon="arrow-up-right"
          />
        )}
      </section>
    </article>
  );
};
