'use client';

import { useState } from 'react';

import { Input } from '@/components/Shared';
import { InputSearch } from '@/components/Shared/InputSearch';

const Page: React.FC = () => {
  const [copy, setCopy] = useState('');
  const [search, setSearch] = useState('');
  return (
    <div className="flex h-screen w-full items-center justify-center bg-volcanic-100">
      <div className="flex w-[600px] flex-col gap-y-5">
        <InputSearch
          className="w-[200px]"
          placeholder="Search chat history"
          value={search}
          onChange={setSearch}
        />
        <Input type="password" label="password" placeholder="••••••••••••" actionType="reveal" />
        <Input label="Basic" placeholder="Placeholder..." required />
        <Input label="Error" placeholder="Placeholder..." errorText="Oh snap!" required />
        <Input
          value={copy}
          onChange={(e) => setCopy(e.target.value)}
          label="Can copy"
          actionType="copy"
          placeholder="Placeholder..."
          required
        />
        <Input readOnly label="Read only" placeholder="Placeholder..." required />
        <Input readOnly label="Disabled" placeholder="Placeholder..." required />
      </div>
    </div>
  );
};

export default Page;
