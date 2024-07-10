'use client';

import { NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useShowUnauthedToolsModal } from '@/hooks/tools';
import { useParamsStore } from '@/stores';

const Page: NextPage = () => {
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: allDeployments } = useListAllDeployments();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;

  const { setMessage } = useContext(BannerContext);
  const { open, close } = useContext(ModalContext);

  useEffect(() => {
    if (showUnauthedToolsModal) {
      open({
        title: 'Connect your data',
        content: (
          <ConnectDataModal
            onClose={() => {
              onDismissed();
              close();
            }}
          />
        ),
      });
    }
  }, [showUnauthedToolsModal]);

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
  }, [deployment, allDeployments]);

  useEffect(() => {
    if (!isLangchainModeOn) return;
    setMessage('You are using an experimental langchain multihop flow. There will be bugs.');
  }, [isLangchainModeOn]);

  return <Conversation startOptionsEnabled />;
};

export default Page;
