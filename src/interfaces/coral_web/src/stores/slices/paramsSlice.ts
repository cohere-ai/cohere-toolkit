import { StateCreator } from 'zustand';

import { CohereChatRequest, DEFAULT_CHAT_TEMPERATURE } from '@/cohere-client';

import { StoreState } from '..';

const INITIAL_STATE = {
  model: undefined,
  temperature: DEFAULT_CHAT_TEMPERATURE,
  preamble: '',
  tools: [],
  fileIds: [],
  deployment: undefined,
};

export type ConfigurableParams = Pick<CohereChatRequest, 'temperature' | 'tools'> & {
  preamble: string;
  fileIds: CohereChatRequest['file_ids'];
  model?: string;
  deployment?: string;
};

type State = ConfigurableParams;
type Actions = {
  setParams: (params?: Partial<ConfigurableParams> | null) => void;
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
  params: INITIAL_STATE,
});
