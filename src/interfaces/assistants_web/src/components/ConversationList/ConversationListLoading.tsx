'use client';

import React from 'react';

import { Skeleton } from '@/components/Shared';

type Props = { numBars?: number };

/**
 * Simple component to render the loading state of the conversation list panel.
 */
export const ConversationListLoading: React.FC<Props> = ({ numBars = 6 }) => {
  return (
    <>
      {Array.from({ length: numBars }).map((_, index) => (
        <article key={index} className="flex w-full flex-col gap-y-1 rounded-lg p-3">
          <Skeleton className="h-6 w-3/5" />
          <Skeleton className="h-6 w-full" />
        </article>
      ))}
    </>
  );
};
