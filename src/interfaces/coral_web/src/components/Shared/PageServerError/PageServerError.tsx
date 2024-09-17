'use client';

import { Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';

export const PageServerError: React.FC = () => {
  return (
    <div className="flex h-screen items-center justify-center">
      <Text as="h1" styleAs="h3" className="mr-5 border-r pr-5 font-medium">
        500
      </Text>
      <Text>{STRINGS.pageServerErrorDescription}</Text>
    </div>
  );
};
