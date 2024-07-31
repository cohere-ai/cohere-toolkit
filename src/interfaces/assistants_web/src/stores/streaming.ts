import { create } from 'zustand';

import { StreamingMessage } from '@/types/message';

type State = {
  streamingMessage: StreamingMessage | null;
  setStreamingMessage: (message: StreamingMessage | null) => void;
};

export const useStreamingStore = create<State>((set) => ({
  streamingMessage: null,
  setStreamingMessage: (message) => set({ streamingMessage: message }),
}));
