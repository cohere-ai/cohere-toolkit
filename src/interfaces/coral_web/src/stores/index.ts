import { create } from 'zustand';
import { shallow } from 'zustand/shallow';

import { Tool } from '@/cohere-client';
import { AgentsStore, createAgentsSlice } from '@/stores/slices/agentsSlice';
import { CitationsStore, createCitationsSlice } from '@/stores/slices/citationsSlice';
import { ConversationStore, createConversationSlice } from '@/stores/slices/conversationSlice';
import { FilesStore, createFilesSlice } from '@/stores/slices/filesSlice';
import { ParamStore, createParamsSlice } from '@/stores/slices/paramsSlice';

export type ChatSettingsDefaultsValue = {
  preamble?: string;
  model?: string;
  temperature?: number;
  tools?: Tool[];
};

export type StoreState = CitationsStore & ConversationStore & FilesStore & ParamStore & AgentsStore;

const useStore = create<StoreState>((...a) => ({
  ...createCitationsSlice(...a),
  ...createConversationSlice(...a),
  ...createFilesSlice(...a),
  ...createParamsSlice(...a),
  ...createAgentsSlice(...a),
}));

export const useCitationsStore = () => {
  return useStore(
    (state) => ({
      citations: state.citations,
      addSearchResults: state.addSearchResults,
      addCitation: state.addCitation,
      selectCitation: state.selectCitation,
      hoverCitation: state.hoverCitation,
      resetCitations: state.resetCitations,
      saveOutputFiles: state.saveOutputFiles,
      agents: state.agents,
    }),
    shallow
  );
};

export const useConversationStore = () => {
  return useStore(
    (state) => ({
      conversation: state.conversation,
      setConversation: state.setConversation,
      setPendingMessage: state.setPendingMessage,
      resetConversation: state.resetConversation,
    }),
    shallow
  );
};

export const useFilesStore = () => {
  return useStore(
    (state) => ({
      files: state.files,
      queueFocusFileInput: state.queueFocusFileInput,
      clearFocusFileInput: state.clearFocusFileInput,
      addUploadingFile: state.addUploadingFile,
      addUploadingFiles: state.addUploadingFiles,
      deleteUploadingFile: state.deleteUploadingFile,
      addComposerFile: state.addComposerFile,
      deleteComposerFile: state.deleteComposerFile,
      clearComposerFiles: state.clearComposerFiles,
      clearUploadingErrors: state.clearUploadingErrors,
      updateUploadingFileError: state.updateUploadingFileError,
    }),
    shallow
  );
};

export const useParamsStore = () => {
  return useStore(
    (state) => ({
      params: state.params,
      setParams: state.setParams,
      resetFileParams: state.resetFileParams,
    }),
    shallow
  );
};

export const useAgentsStore = () => {
  return useStore(
    (state) => ({
      agents: state.agents,
      setAgentsSidePanelOpen: state.setAgentsSidePanelOpen,
      setEditAgentPanelOpen: state.setEditAgentPanelOpen,
    }),
    shallow
  );
};

export { useSettingsStore } from '@/stores/persistedStore';
