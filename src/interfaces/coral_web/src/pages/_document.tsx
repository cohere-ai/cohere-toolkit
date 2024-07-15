import { Head, Html, Main, NextScript } from 'next/document';

import { env } from '@/env.mjs';
import { cn } from '@/utils';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';

export default function Document() {
  // const { data: experimentalFeatures } = useExperimentalFeatures();
  // console.debug(experimentalFeatures)
  return (
    <Html lang="en" className={cn({ dark: env.NEXT_PUBLIC_DARK_MODE })}>
      <Head />
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
