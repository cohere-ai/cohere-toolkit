import { Head, Html, Main, NextScript } from 'next/document';

import { env } from '@/env.mjs';
import { cn } from '@/utils';

export default function Document() {
  return (
    <Html lang="en" className={cn({ dark: env.NEXT_PUBLIC_DARK_MODE == 'true' })}>
      <Head />
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
