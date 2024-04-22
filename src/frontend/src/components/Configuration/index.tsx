import { createElement, useState } from 'react';

import { Settings } from '@/components/Configuration/Settings';
import { Tools } from '@/components/Configuration/Tools';
import { Tabs } from '@/components/Shared';
import { CONFIGURATION_PANEL_ID } from '@/constants';

const TABS = [
  { name: 'Tools', component: Tools },
  { name: 'Settings', component: Settings },
];

export const Configuration: React.FC = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <section id={CONFIGURATION_PANEL_ID} className="h-full w-full overflow-y-auto rounded-b-lg">
      <Tabs
        tabs={TABS.map((t) => t.name)}
        selectedIndex={selectedIndex}
        onChange={setSelectedIndex}
        tabClassName="pt-2.5"
        panelsClassName="pt-7 lg:pt-7 px-0 flex flex-col rounded-b-lg bg-marble-100 md:rounded-b-none"
        fitTabsContent={true}
      >
        {TABS.map((t) => createElement(t.component, { key: t.name }))}
      </Tabs>
    </section>
  );
};
