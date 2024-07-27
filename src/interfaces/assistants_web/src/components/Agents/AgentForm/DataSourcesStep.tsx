import { ManagedTool } from '@/cohere-client';
import {
  CreateAgentFormFields,
  UpdateAgentFormFields,
} from '@/components/Agents/AgentForm/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Button, Icon, Input, Text, Textarea } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { GoogleDriveToolArtifact } from '@/types/tools';

type Props<K extends UpdateAgentFormFields | CreateAgentFormFields> = {
  fields: K;
  tools: ManagedTool[];
  googleDriveFiles: GoogleDriveToolArtifact[];
  files: File[];
  isAgentCreator: boolean;
  onToolToggle: (toolName: string, checked: boolean, authUrl?: string) => void;
  handleOpenFilePicker: VoidFunction;
  handleRemoveGoogleDriveFile: (id: string) => void;
  setFields: React.Dispatch<React.SetStateAction<K>>;
};

export function DataSourcesStep<K extends CreateAgentFormFields | UpdateAgentFormFields>({
  fields,
  tools,
  googleDriveFiles,
  files,
  isAgentCreator,
  onToolToggle,
  handleOpenFilePicker,
  handleRemoveGoogleDriveFile,
  setFields,
}: Props<K>) {
  const googleDriveActive = fields.tools?.includes(TOOL_GOOGLE_DRIVE_ID);
  const filesActive = files.length > 0;

  const googleDriveTool = tools.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID);
  return (
    <div className="flex flex-col space-y-3">
      {googleDriveActive ? (
        <></>
      ) : (
        <Button label="Google Drive" icon="upload" onClick={handleOpenFilePicker} />
      )}
      {filesActive ? (
        <></>
      ) : (
        <input
          type="file"
          multiple={true}
          onChange={(e) => setDocuments}
          readOnly={!isAgentCreator}
        />
      )}
      {/* {googleDriveTool && !requireGoogleAuth ? ( */}
      {true ? (
        <>
          <Text styleAs="label">Active Data Sources</Text>
          <div className="flex w-full flex-col justify-start space-y-6 rounded-md border p-4 dark:border-volcanic-500">
            <div className="flex w-full flex-col">
              <div className="flex items-center justify-between">
                <Text styleAs="p-lg">
                  <Icon className="pr-2" name="upload" />
                  Google Drive
                </Text>
                <IconButton
                  iconName="trash"
                  className="dark:text-danger-500 dark:hover:text-danger-350"
                  onClick={() =>
                    onToolToggle(
                      googleDriveTool?.name ?? '',
                      false,
                      googleDriveTool?.auth_url ?? ''
                    )
                  }
                />
              </div>
              <Text className="dark:text-marble-800">
                Connect to Google Drive and add files to the assistant
              </Text>
            </div>
            {googleDriveFiles && (
              <FileList files={googleDriveFiles} handleRemove={handleRemoveGoogleDriveFile} />
            )}
            <Button label="Add files" kind="secondary" startIcon="add" className="w-fit" />
          </div>
          <Text className="pt-3" styleAs="label">
            Add More data sources
          </Text>
        </>
      ) : (
        <Button label="Google Drive" startIcon="upload" kind="secondary" className="w-fit" />
      )}
      <Button label="Upload files" startIcon="upload" kind="secondary" className="w-fit" />
    </div>
  );
}

const FileList: React.FC<{
  files: GoogleDriveToolArtifact[];
  handleRemove: (id: string) => void;
}> = ({ files, handleRemove }) => {
  return (
    <div className="flex flex-col">
      {files.map(({ id, type, name }) => (
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
            onClick={() => handleRemove(id)}
          />
        </div>
      ))}
    </div>
  );
};
