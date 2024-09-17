'use client';

import { useEffect, useRef, useState } from 'react';

import { Button, Input } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { hasCommonDelimiters } from '@/utils';

/**
 * @description Modal for configuring options on the web search tool.
 * @wujessica: This component is not currently used since we do not have the tool options param yet.
 */
export const WebSearchModal: React.FC<{
  onSave: (site: string) => void;
  onCancel: VoidFunction;
}> = ({ onSave, onCancel }) => {
  const [site, setSite] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

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
        ref={inputRef}
        label="Site"
        placeholder={STRINGS.siteGroundingDescription}
        description={
          site.length > 0 && hasCommonDelimiters(site)
            ? STRINGS.multipleSiteGroundingError
            : undefined
        }
        value={site}
        onChange={(e) => setSite(e.target.value)}
      />
      <div className="flex w-full items-center justify-between">
        <Button label={STRINGS.cancel} kind="secondary" onClick={onCancel} />
        <Button label={STRINGS.save} type="submit" splitIcon="arrow-right" theme="volcanic" />
      </div>
    </form>
  );
};
