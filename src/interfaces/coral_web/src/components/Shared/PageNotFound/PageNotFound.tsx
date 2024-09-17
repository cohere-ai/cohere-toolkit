'use client';

import { Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';

export const PageNotFound: React.FC = () => {
  return (
    <div className="flex h-screen flex-row items-center justify-center">
      <Text as="h1" styleAs="h3" className="mr-5 border-r pr-5 font-medium">
        404
      </Text>
      <Text>{STRINGS.pageNotFoundDescription}</Text>
    </div>
  );
};
