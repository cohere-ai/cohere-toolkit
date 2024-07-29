'use client';

import { useContext, useEffect } from 'react';

import { BannerContext } from '@/context/BannerContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useConversationStore, useParamsStore, useSettingsStore } from '@/stores';

const ChatLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const { resetConversation } = useConversationStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments } = useListAllDeployments();

  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { setMessage } = useContext(BannerContext);

  // Reset conversation when unmounting
  useEffect(() => {
    return () => {
      resetConversation();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deployment, allDeployments]);

  useEffect(() => {
    if (!isLangchainModeOn) return;
    setMessage('You are using an experimental langchain multihop flow. There will be bugs.');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLangchainModeOn]);

  return <div className="flex h-full">{children}</div>;
};

export default ChatLayout;
