'use client';

import { useState } from 'react';

import { Button, Input } from '@/components/Shared';
import { useParamsStore } from '@/stores';

/**
 * @description Modal for configuring options on the web search tool.
 * @wujessica: This component is not currently used since we do not have the tool options param yet.
 */
export const WebSearchModal: React.FC<{
  onSave: (site: string) => void;
  onCancel: VoidFunction;
}> = ({ onSave, onCancel }) => {
  const {
    params: { tools },
  } = useParamsStore();
  const [site, setSite] = useState('');

  return (
    <form
      className="flex flex-col gap-y-8"
      onSubmit={(e) => {
        e.stopPropagation();
        e.preventDefault();
        onSave(site);
      }}
    >
      <Input
        label="Site"
        placeholder="Ground on 1 domain e.g. wikipedia.org"
        value={site}
        onChange={(e) => setSite(e.target.value)}
      />
      <div className="flex w-full items-center justify-between">
        <Button label="Cancel" theme="danger" onClick={onCancel} />
        <Button buttonType="submit" label="Save" kind="cell" />
      </div>
    </form>
  );
};
