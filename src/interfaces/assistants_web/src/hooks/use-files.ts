import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  ApiError,
  DeleteAgentFileResponse,
  ListConversationFile,
  useCohereClient,
} from '@/cohere-client';
import { ACCEPTED_FILE_TYPES, MAX_NUM_FILES_PER_UPLOAD_BATCH } from '@/constants';
import { useNotify, useSession } from '@/hooks';
import { useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import { UploadingFile } from '@/stores/slices/filesSlice';
import { fileSizeToBytes, formatFileSize, getFileExtension, mapExtensionToMimeType } from '@/utils';

export const useFile = ({
  fileId,
  agentId,
  conversationId,
}: {
  fileId: string;
  agentId?: string;
  conversationId?: string;
}) => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['file', fileId],
    queryFn: async () => {
      if ((!agentId && !conversationId) || (agentId && conversationId)) {
        throw new Error('Exactly one of agentId or conversationId must be provided');
      }
      return agentId
        ? await cohereClient.getAgentFile({ agentId: agentId!, fileId })
        : await cohereClient.getConversationFile({ conversationId: conversationId!, fileId });
    },
  });
};

export const useListConversationFiles = (
  conversationId?: string,
  options?: { enabled?: boolean }
) => {
  const cohereClient = useCohereClient();
  return useQuery<ListConversationFile[], ApiError>({
    queryKey: ['listFiles', conversationId],
    queryFn: async () => {
      if (!conversationId) throw new Error('Conversation ID not found');
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

export const useUploadAgentFile = () => {
  const cohereClient = useCohereClient();

  return useMutation({
    mutationFn: ({ files }: { files: File[] }) => cohereClient.batchUploadAgentFile({ files }),
  });
};

export const useUploadConversationFile = () => {
  const cohereClient = useCohereClient();
  return useMutation({
    mutationFn: ({ files, conversationId }: { files: File[]; conversationId?: string }) =>
      cohereClient.batchUploadConversationFile({ files, conversation_id: conversationId }),
  });
};

export const useDeleteUploadedConversationFile = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();

  return useMutation<DeleteAgentFileResponse, ApiError, { conversationId: string; fileId: string }>(
    {
      mutationFn: async ({ conversationId, fileId }) =>
        cohereClient.deletefile({ conversationId, fileId }),
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ['listFiles'] });
      },
    }
  );
};

export const useConversationFileActions = () => {
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
  const { userId } = useSession();
  const { mutateAsync: uploadFiles } = useUploadConversationFile();
  const { mutateAsync: deleteFile } = useDeleteUploadedConversationFile();
  const { error } = useNotify();
  const { setConversation } = useConversationStore();

  const handleUploadFiles = async (files?: File[], conversationId?: string) => {
    // cleanup uploadingFiles with errors
    const uploadingFilesWithErrors = uploadingFiles.filter((file) => file.error);
    uploadingFilesWithErrors.forEach((file) => deleteUploadingFile(file.id));

    if (!files?.length) return;
    if (files.length > MAX_NUM_FILES_PER_UPLOAD_BATCH) {
      addUploadingFiles([
        {
          id: 'error',
          error: `You can upload a maximum of ${MAX_NUM_FILES_PER_UPLOAD_BATCH} files at a time.`,
          file: new File([], ''),
          progress: 0,
        },
      ]);
      return;
    }

    const MAX_FILE_SIZE = fileSizeToBytes(20);

    const newUploadingFiles: UploadingFile[] = [];
    files.forEach((file) => {
      if (file.type.length === 0) {
        const fileExtension = getFileExtension(file.name)!;
        Object.defineProperty(file, 'type', {
          value: mapExtensionToMimeType(fileExtension),
        });
      }
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
        newUploadingFile.error = `File type not supported (${fileExtension?.toUpperCase()})`;
      } else if (!isFileSizeValid) {
        newUploadingFile.error = `File size cannot exceed ${formatFileSize(MAX_FILE_SIZE)}`;
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
        addComposerFile({ ...uploadedFile });
      });

      if (!conversationId) {
        const newConversationId = uploadedFiles[0].conversation_id;
        setConversation({ id: newConversationId });
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
      error('Unable to delete file');
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
