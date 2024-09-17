import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { uniqBy } from 'lodash';
import { useMemo } from 'react';

import {
  ApiError,
  File as CohereFile,
  DeleteFile,
  ListFile,
  useCohereClient,
} from '@/cohere-client';
import { ACCEPTED_FILE_TYPES, MAX_NUM_FILES_PER_UPLOAD_BATCH } from '@/constants';
import { DYNAMIC_STRINGS, STRINGS } from '@/constants/strings';
import { useNotify } from '@/hooks/toast';
import { useListTools } from '@/hooks/tools';
import { useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import { UploadingFile } from '@/stores/slices/filesSlice';
import { MessageType } from '@/types/message';
import {
  fileSizeToBytes,
  formatFileSize,
  getFileExtension,
  isDefaultFileLoaderTool,
} from '@/utils';

class FileUploadError extends Error {
  constructor(message: string) {
    super(message);
  }
}

export const useListFiles = (conversationId?: string, options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
  return useQuery<ListFile[], ApiError>({
    queryKey: ['listFiles', conversationId],
    queryFn: async () => {
      if (!conversationId) throw new Error(STRINGS.conversationIDNotFoundError);
      try {
        return await cohereClient.listFiles({ conversationId });
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    enabled: !!conversationId,
    refetchOnWindowFocus: false,
    ...options,
  });
};

export const useFilesInConversation = () => {
  const {
    conversation: { messages },
  } = useConversationStore();
  const files = useMemo<CohereFile[]>(() => {
    return messages.reduce<CohereFile[]>((filesInConversation, msg) => {
      if (msg.type === MessageType.USER && msg.files) {
        filesInConversation.push(...msg.files);
      }
      return filesInConversation;
    }, []);
  }, [messages.length]);

  return { files };
};

export const useUploadFile = () => {
  const cohereClient = useCohereClient();

  return useMutation({
    mutationFn: ({ file, conversationId }: { file: File; conversationId?: string }) =>
      cohereClient.uploadFile({ file, conversation_id: conversationId }),
  });
};

export const useBatchUploadFile = () => {
  const cohereClient = useCohereClient();

  return useMutation({
    mutationFn: ({ files, conversationId }: { files: File[]; conversationId?: string }) =>
      cohereClient.batchUploadFile({ files, conversation_id: conversationId }),
  });
};

export const useDeleteUploadedFile = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();

  return useMutation<DeleteFile, ApiError, { conversationId: string; fileId: string }>({
    mutationFn: async ({ conversationId, fileId }) =>
      cohereClient.deletefile({ conversationId, fileId }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['listFiles'] });
    },
  });
};

export const useFileActions = () => {
  const {
    files: { uploadingFiles, composerFiles },
    addUploadingFiles,
    addComposerFile,
    deleteUploadingFile,
    deleteComposerFile,
    clearComposerFiles,
    updateUploadingFileError,
  } = useFilesStore();
  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();
  const { mutateAsync: uploadFiles } = useBatchUploadFile();
  const { mutateAsync: deleteFile } = useDeleteUploadedFile();
  const { error } = useNotify();
  const { setConversation, conversation } = useConversationStore();

  const handleUploadFiles = async (files?: File[], conversationId?: string) => {
    // cleanup uploadingFiles with errors
    const uploadingFilesWithErrors = uploadingFiles.filter((file) => file.error);
    uploadingFilesWithErrors.forEach((file) => deleteUploadingFile(file.id));

    if (!files?.length) return;
    if (files.length > MAX_NUM_FILES_PER_UPLOAD_BATCH) {
      addUploadingFiles([
        {
          id: 'error',
          error: DYNAMIC_STRINGS.uploadFilesBatchMaximumError(MAX_NUM_FILES_PER_UPLOAD_BATCH),
          file: new File([], ''),
          progress: 0,
        },
      ]);
      return;
    }

    const MAX_FILE_SIZE = fileSizeToBytes(20);

    const newUploadingFiles: UploadingFile[] = [];
    files.forEach((file) => {
      const uploadingFileId = new Date().valueOf().toString();
      const newUploadingFile: UploadingFile = {
        id: uploadingFileId,
        file,
        error: '',
        progress: 0,
      };
      const fileExtension = getFileExtension(file.name);
      const isAcceptedExtension = ACCEPTED_FILE_TYPES.some(
        (acceptedFile) => file.type === acceptedFile
      );
      const isFileSizeValid = file.size <= MAX_FILE_SIZE;
      if (!isAcceptedExtension) {
        newUploadingFile.error = DYNAMIC_STRINGS.fileTypeNotSupportedError(
          fileExtension?.toUpperCase() ?? ''
        );
      } else if (!isFileSizeValid) {
        newUploadingFile.error = DYNAMIC_STRINGS.fileSizeCannotExceedError(
          formatFileSize(MAX_FILE_SIZE)
        );
      }

      newUploadingFiles.push(newUploadingFile);
    });

    const firstInvalidFile = newUploadingFiles.find((file) => file.error);
    if (!!firstInvalidFile) {
      // If error exists, update all files with the same error so that none
      // are shown as uploading in the composer and then exist the function.
      // This is because batch file upload will currently fail if any one file is invalid.
      const invalidFiles = newUploadingFiles.map((file) =>
        !file.error ? { ...file, error: firstInvalidFile.error } : file
      );
      addUploadingFiles(invalidFiles);
      return;
    }
    addUploadingFiles(newUploadingFiles);

    try {
      const uploadedFiles = await uploadFiles({ files, conversationId });

      newUploadingFiles.forEach((file) => deleteUploadingFile(file.id));

      const newFileIds: string[] = fileIds ?? [];
      uploadedFiles.forEach((uploadedFile) => {
        newFileIds.push(uploadedFile.id);
        setParams({ fileIds: newFileIds });
        addComposerFile(uploadedFile);
      });

      if (!conversationId) {
        setConversation({ id: uploadedFiles[0].conversation_id });
      }

      return newFileIds;
    } catch (e: any) {
      uploadingFiles.forEach((file) => updateUploadingFileError(file, e.message));
    }
  };

  const deleteUploadedFile = async ({
    conversationId,
    fileId,
  }: {
    conversationId: string;
    fileId: string;
  }) => {
    try {
      await deleteFile({ conversationId, fileId });
    } catch (e) {
      error(STRINGS.deleteFileError);
    }
  };

  return {
    uploadingFiles,
    composerFiles,
    uploadFiles: handleUploadFiles,
    deleteFile: deleteUploadedFile,
    deleteUploadingFile,
    deleteComposerFile,
    clearComposerFiles,
  };
};

/**
 * @description Hook to fetch and enable the default file loader tool.
 * This tool must be on for files to work in the conversation.
 */
export const useDefaultFileLoaderTool = () => {
  const { data: tools } = useListTools();
  const { params, setParams } = useParamsStore();
  // Returns the first visible file loader tool from tools list
  const defaultFileLoaderTool = useMemo(
    () => tools?.find(isDefaultFileLoaderTool),
    [tools?.length]
  );

  const enableDefaultFileLoaderTool = () => {
    if (!defaultFileLoaderTool) return;

    const visibleFileToolNames = tools?.filter(isDefaultFileLoaderTool).map((t) => t.name) ?? [];
    const isDefaultFileLoaderToolEnabled = visibleFileToolNames.some((name) =>
      params.tools?.some((tool) => tool.name === name)
    );

    if (isDefaultFileLoaderToolEnabled) return;

    const newTools = uniqBy([...(params.tools ?? []), defaultFileLoaderTool], 'name');
    setParams({ tools: newTools });
  };

  const disableDefaultFileLoaderTool = () => {
    if (!defaultFileLoaderTool) return;

    const visibleFileToolNames = tools?.filter(isDefaultFileLoaderTool).map((t) => t.name) ?? [];
    const isDefaultFileLoaderToolEnabled = visibleFileToolNames.some((name) =>
      params.tools?.some((tool) => tool.name === name)
    );

    if (!isDefaultFileLoaderToolEnabled) return;

    const newTools = (params.tools ?? []).filter((t) => t.name !== defaultFileLoaderTool.name);
    setParams({ tools: newTools });
  };

  return { defaultFileLoaderTool, enableDefaultFileLoaderTool, disableDefaultFileLoaderTool };
};
