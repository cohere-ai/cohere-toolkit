import { StateCreator } from 'zustand';

import { CohereChatRequest, DEFAULT_CHAT_TEMPERATURE } from '@/cohere-client';
import { isDefaultFileLoaderTool } from '@/utils';

import { StoreState } from '..';

const INITIAL_STATE: ConfigurableParams = {
  model: undefined,
  temperature: DEFAULT_CHAT_TEMPERATURE,
  preamble: '',
  tools: [],
  fileIds: [],
  deployment: undefined,
  deploymentConfig: undefined,
  googleDriveFiles: [],
};

export type ConfigurableParams = Pick<CohereChatRequest, 'temperature' | 'tools'> & {
  preamble: string;
  fileIds: CohereChatRequest['file_ids'];
  model?: string;
  deployment?: string;
  deploymentConfig?: string;
  googleDriveFiles?: {
    id: string;
    name: string;
    type: string;
  }[];
};

type State = ConfigurableParams;
type Actions = {
  setParams: (params?: Partial<ConfigurableParams> | null) => void;
  setGoogleDriveFiles: (files: ConfigurableParams['googleDriveFiles']) => void;
  removeGoogleDriveFile: (id: string) => void;
  resetFileParams: VoidFunction;
};

export type ParamStore = {
  params: State;
} & Actions;

export const createParamsSlice: StateCreator<StoreState, [], [], ParamStore> = (set) => ({
  setParams(params?) {
    let tools = params?.tools;
    let fileIds = params?.fileIds;

    set((state) => {
      return {
        params: {
          ...state.params,
          ...params,
          ...(tools ? { tools } : []),
          ...(fileIds ? { fileIds } : {}),
        },
      };
    });
  },
  setGoogleDriveFiles(files) {
    set((state) => {
      return {
        params: {
          ...state.params,
          googleDriveFiles: files,
        },
      };
    });
  },
  removeGoogleDriveFile(id) {
    set((state) => {
      return {
        params: {
          ...state.params,
          googleDriveFiles: state.params?.googleDriveFiles?.filter((f) => f.id !== id),
        },
      };
    });
  },
  resetFileParams() {
    set((state) => {
      return {
        params: {
          ...state.params,
          fileIds: [],
          tools: state.params?.tools?.filter((t) => !isDefaultFileLoaderTool(t)),
        },
      };
    });
  },
  params: INITIAL_STATE,
});
