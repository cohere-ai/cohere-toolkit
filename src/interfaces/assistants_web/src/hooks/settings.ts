import { DEFAULT_CHAT_TEMPERATURE } from '@/cohere-client';

export const useSettingsDefaults = () => {
  return {
    preamble: '',
    temperature: DEFAULT_CHAT_TEMPERATURE,
    tools: [],
  };
};
