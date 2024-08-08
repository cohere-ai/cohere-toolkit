'use client';

import { PropsWithChildren, useState } from 'react';

import { DarkModeToggle } from '@/components/DarkModeToggle';
import { Button, Icon, Tabs, Text, Tooltip } from '@/components/Shared';
import { useListTools } from '@/hooks/tools';
import { cn } from '@/utils';

const tabs = [
  <div className="flex items-center gap-2" key="company">
    <Icon name="users-three" kind="outline" />
    <Text>Connections</Text>
  </div>,
  <div className="flex items-center gap-2" key="company">
    <Icon name="sun" kind="outline" />
    <Text>appearance</Text>
  </div>,
  <div className="flex items-center gap-2" key="private">
    <Icon name="profile" kind="outline" />
    <Text>Profile</Text>
  </div>,
];

export const Settings = () => {
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
            Settings
          </Text>
          <Tooltip label="tbd" hover size="sm">
            <Icon
              name="information"
              kind="outline"
              className="fill-volcanic-300 dark:fill-mushroom-700"
            />
          </Tooltip>
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
    <Text className="mb-10 dark:text-mushroom-950">
      A list of connections that your assistants can access
    </Text>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <GoogleDriveConnection />
    </div>
  </Wrapper>
);

const Profile = () => {
  return (
    <Wrapper>
      <Button label="Sign out" href="/logout" kind="secondary" icon="sign-out" theme="default" />
    </Wrapper>
  );
};

const Appearance = () => {
  return (
    <Wrapper>
      <Text styleAs="h5" className="mb-6">
        Appearance
      </Text>
      <DarkModeToggle />
    </Wrapper>
  );
};

const GoogleDriveConnection = () => {
  const { data } = useListTools();
  const googleDriveTool = data?.find((tool) => tool.name === 'google_drive');

  if (!googleDriveTool) {
    return null;
  }

  const isGoogleDriveConnected = !googleDriveTool.is_auth_required ?? false;
  const authUrl = googleDriveTool.auth_url;

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
                onClick={() => alert('not implemented')}
              />
            </div>
          </div>
        ) : (
          <Button
            label="Authenticate"
            href={googleDriveTool.auth_url ?? ''}
            kind="secondary"
            theme="evolved-green"
            icon="arrow-up-right"
          />
        )}
      </section>
    </article>
  );
};

const StatusConnection: React.FC<{ connected: boolean }> = ({ connected }) => {
  const label = connected ? 'Connected' : 'Disconnected';
  return (
    <Text styleAs="p-sm" className="flex items-center gap-2 uppercase dark:text-mushroom-950">
      <span
        className={cn('size-[10px] rounded-full', {
          'bg-evolved-green-700': connected,
          'bg-danger-500': !connected,
        })}
      />
      {label}
    </Text>
  );
};
