import { StateCreator } from 'zustand';

import { CohereChatRequest } from '@/cohere-client';

import { StoreState } from '..';

const INITIAL_STATE: ConfigurableParams = {
  model: undefined,
  temperature: undefined,
  preamble: '',
  tools: [],
  fileIds: [],
  deployment: undefined,
  deploymentConfig: undefined,
};

export type ConfigurableParams = Pick<CohereChatRequest, 'temperature' | 'tools'> & {
  preamble: string;
  fileIds: CohereChatRequest['file_ids'];
  model?: string;
  deployment?: string;
  deploymentConfig?: string;
};

type State = ConfigurableParams;
type Actions = {
  setParams: (params?: Partial<ConfigurableParams> | null) => void;
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
  resetFileParams() {
    set((state) => {
      return {
        params: {
          ...state.params,
          fileIds: [],
        },
      };
    });
  },
  params: INITIAL_STATE,
});
