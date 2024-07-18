'use client';

import { useEffect } from 'react';

import { PageServerError } from '@/components/Shared';

export default function Error({
  error,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return <PageServerError />;
}
