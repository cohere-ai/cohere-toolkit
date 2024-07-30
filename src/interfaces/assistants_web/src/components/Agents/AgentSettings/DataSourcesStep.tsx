import { useMemo } from 'react';
import { UseFormSetValue } from 'react-hook-form';

import { ManagedTool } from '@/cohere-client';
import { IconButton } from '@/components/IconButton';
import { Button, Icon, IconName, Text } from '@/components/Shared';
import { TOOL_FILE_UPLOAD, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { DataSourceArtifact } from '@/types/tools';

import { ASSISTANT_SETTINGS_FORM } from './AgentSettingsForm';

type Props = {
  fields: ASSISTANT_SETTINGS_FORM;
  tools?: ManagedTool[];
  setValue: UseFormSetValue<ASSISTANT_SETTINGS_FORM>;
  openFilePicker: VoidFunction;
};
export const DataSourcesStep: React.FC<Props> = ({ fields, tools, setValue }) => {
  const googleDriveTool = tools?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID && t.is_available);
  const fileUploadTool = tools?.find((t) => t.name === TOOL_FILE_UPLOAD && t.is_available);

  const handleGoogleDriveEnable = () => {};
  const handleFileUploadEnable = () => {};

  const activeDataSources =
    fields.tools.includes(TOOL_GOOGLE_DRIVE_ID) || fields.tools.includes(TOOL_FILE_UPLOAD);
  return (
    <div className="flex flex-col space-y-3">
      {googleDriveTool &&
        (fields.tools.includes(TOOL_GOOGLE_DRIVE_ID) ? (
          <></>
        ) : (
          // TODO: abi - use new google drive icon
          <Button
            kind="outline"
            label="Google Drive"
            icon="file"
            onClick={handleGoogleDriveEnable}
          />
        ))}
    </div>
  );
};

const EnabledDataSource: React.FC<{
  name: string;
  icon: IconName;
  artifacts?: DataSourceArtifact[];
}> = ({ name, icon, artifacts = [] }) => {
  return (
    <div className="flex flex-col space-y-6 rounded-md border border-volcanic-500 p-4">
      <div className="flex flex-col space-y-2">
        <div className="flex justify-between">
          <div className="flex space-x-2">
            <Icon name="add" />
            <Text>{name}</Text>
          </div>
          {/* TODO: iconbutton! */}
          <Icon name="trash" />
        </div>
        <Text className="text-marble-800">
          {name === TOOL_GOOGLE_DRIVE_ID ? 'Connect to Google Drive and add ' : 'Add '} files to the
          assistant.
        </Text>
      </div>
      <div className="flex flex-col">
        {artifacts.map(({ id, type, name }) => (
          <div
            key={id}
            className="flex w-full items-center gap-x-2 border-b border-mushroom-500 py-2 dark:border-volcanic-300"
          >
            <Icon
              kind="outline"
              name={type === 'folder' ? 'folder' : 'file'}
              className="text-mushroom-500 dark:text-marble-950"
              size="sm"
            />
            <Text styleAs="overline" className="dark:test-marble-950 mr-auto truncate">
              {name}
            </Text>
            <IconButton
              size="sm"
              iconName="close"
              className="text-mushroom-500 dark:text-marble-950"
              //   TODO: abi - onclick
              //   onClick={() => handleRemove(id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
