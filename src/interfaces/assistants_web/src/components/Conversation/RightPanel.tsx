'use client';

import { Transition } from '@headlessui/react';
import { useEffect, useMemo, useState } from 'react';

import { ListFile } from '@/cohere-client';
import { Banner, Button, Checkbox, Icon, Switch, Tabs, Text, Tooltip } from '@/components/Shared';
import { useFocusFileInput } from '@/hooks/actions';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useDefaultFileLoaderTool, useFilesInConversation } from '@/hooks/files';
import { useParamsStore } from '@/stores';
import { cn, formatFileSize } from '@/utils';

interface UploadedFile extends ListFile {
  checked: boolean;
}

type Props = {};

const RightPanel: React.FC<Props> = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [useAssistantKnowledge, setUseAssistantKnowledge] = useState(true);
  const { agentId } = useChatRoutes();

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();

  const { isFileInputQueuedToFocus, focusFileInput } = useFocusFileInput();
  const { files } = useFilesInConversation();
  const { enableDefaultFileLoaderTool, disableDefaultFileLoaderTool } = useDefaultFileLoaderTool();

  useEffect(() => {
    if (isFileInputQueuedToFocus) {
      focusFileInput();
    }
  }, [isFileInputQueuedToFocus]);

  const uploadedFiles: UploadedFile[] = useMemo(() => {
    if (!files) return [];

    return files
      .map((document: ListFile) => ({
        ...document,
        checked: (fileIds ?? []).some((id) => id === document.id),
      }))
      .sort(
        (a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      );
  }, [files, fileIds]);

  const handleToggle = (fileId?: string) => {
    if (!fileId) return;

    let newFileIds: string[] = [];
    if (fileIds?.some((id) => id === fileId)) {
      newFileIds = fileIds.filter((id) => id !== fileId);
    } else {
      newFileIds = [...(fileIds ?? []), fileId];
    }

    if (newFileIds.length === 0) {
      disableDefaultFileLoaderTool();
    } else {
      enableDefaultFileLoaderTool();
    }

    setParams({ fileIds: newFileIds });
  };

  return (
    <Tabs
      selectedIndex={selectedIndex}
      onChange={setSelectedIndex}
      tabs={[
        <span className="flex items-center gap-x-2" key="knowledge">
          <Icon name="folder" kind="outline" />
          Knowledge
        </span>,
        <span className="flex items-center gap-x-2" key="citations">
          <Icon name="link" kind="outline" />
          Citations
        </span>,
      ]}
      tabGroupClassName="h-full"
      kind="blue"
    >
      <div className="flex flex-col gap-y-10">
        {agentId && (
          <div className="flex flex-col gap-y-4">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-x-2">
                <Text styleAs="label" className="font-medium">
                  Assistant Knowledge
                </Text>
                <Tooltip
                  hover
                  size="sm"
                  placement="top-start"
                  hoverDelay={250}
                  label="Enables assistant knowledge to provide more accurate responses."
                />
              </span>
              <Switch
                theme="blue"
                checked={useAssistantKnowledge}
                onChange={setUseAssistantKnowledge}
              />
            </div>
            <Transition
              show={useAssistantKnowledge}
              enter="duration-300 ease-in-out transition-all"
              enterFrom="opacity-0 scale-90"
              enterTo="opacity-100 scale-100"
              leave="duration-200 ease-in-out transition-all"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-90"
              as="div"
            >
              <Banner theme="dark" className="flex flex-col">
                Add a data source to expand the assistant’s knowledge.
                <Button theme="acrylic-blue" className="mt-4" label="Add Data Source" icon="add" />
              </Banner>
            </Transition>
          </div>
        )}

        <section className="relative flex flex-col gap-y-8">
          <div className="flex gap-x-2">
            <Text styleAs="label" className="font-medium">
              My files
            </Text>
            <Tooltip
              hover
              size="sm"
              placement="top-start"
              label="To use uploaded files, at least 1 File Upload tool must be enabled"
            />
          </div>
          {uploadedFiles.length > 0 && (
            <div className="flex w-full flex-col gap-y-14 pb-2">
              <div className="flex flex-col gap-y-4">
                {uploadedFiles.map(({ file_name: name, file_size: size, id, checked }) => (
                  <div key={id} className="group flex w-full flex-col gap-y-2">
                    <div className="flex w-full items-center justify-between gap-x-2">
                      <div className={cn('flex w-[60%] overflow-hidden lg:w-[70%]')}>
                        <Checkbox
                          checked={checked}
                          onChange={() => handleToggle(id)}
                          label={name}
                          name={name}
                          theme="evolved-green"
                          className="w-full"
                          labelClassName="ml-0 truncate w-full"
                          labelSubContainerClassName="w-full"
                          labelContainerClassName="w-full"
                        />
                      </div>
                      <div className="flex h-5 w-32 grow items-center justify-end gap-x-1">
                        <Text styleAs="caption" className="text-volcanic-400 dark:text-marble-800">
                          {formatFileSize(size ?? 0)}
                        </Text>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <Text styleAs="caption" className="text-mushroom-300 dark:text-marble-800">
            These files will only be accessible to you and won’t impact others.
          </Text>
        </section>
      </div>
      <div>Citations</div>
    </Tabs>
  );
};

export default RightPanel;
