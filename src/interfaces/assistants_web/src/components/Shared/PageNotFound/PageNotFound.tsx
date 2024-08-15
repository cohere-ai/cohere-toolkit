'use client';

import { Button, Text } from '@/components/Shared';

export const PageNotFound: React.FC = () => {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-y-8 text-volcanic-100 dark:bg-volcanic-100 dark:text-marble-950 dark:selection:bg-volcanic-300">
      <div className="flex items-center justify-center">
        <Text as="h1" styleAs="h3" className="mr-5 border-r pr-5 font-medium">
          404
        </Text>
        <Text>This page could not be found.</Text>
      </div>
      <Button href="/" icon="arrow-left">
        Go back
      </Button>
    </div>
  );
};
