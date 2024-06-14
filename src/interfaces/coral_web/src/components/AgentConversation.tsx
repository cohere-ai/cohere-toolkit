import React from 'react';

import Conversation from '@/components/Conversation';

import { UpdateAgentDrawer } from './UpdateAgentDrawer';

type Props = {
  conversationId?: string;
};

export const AgentConversation: React.FC<Props> = ({ conversationId }) => {
  return (
    <div>
      <Conversation conversationId={conversationId} startOptionsEnabled />
      <UpdateAgentDrawer agent={{}} />
    </div>
  );
};
