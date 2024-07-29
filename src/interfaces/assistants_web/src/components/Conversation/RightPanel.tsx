'use client';

import { useState } from 'react';

import { Banner, Button, Icon, Switch, Tabs } from '@/components/Shared';

type Props = {};

const RightPanel: React.FC<Props> = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [useAssistantKnowledge, setUseAssistantKnowledge] = useState(true);

  return (
    <Tabs
      selectedIndex={selectedIndex}
      onChange={setSelectedIndex}
      tabs={[
        <span className="flex items-center gap-x-2" key="knowledge">
          <Icon name="folder" kind="outline" />
          Knowledge
        </span>,
        <span className="flex items-center gap-x-2" key="citations">
          <Icon name="link" kind="outline" />
          Citations
        </span>,
      ]}
      tabGroupClassName="h-full"
      kind="blue"
    >
      <div className="flex flex-col gap-y-4">
        <Switch
          label="assistant knowledge"
          theme="blue"
          className="w-full"
          checked={useAssistantKnowledge}
          onChange={setUseAssistantKnowledge}
          tooltip={{ label: 'tbd' }}
          reverse
        />
        <Banner theme="dark">Add a data source to expand the assistant’s knowledge.</Banner>
      </div>
      <div>Citations</div>
    </Tabs>
  );
};

export default RightPanel;
