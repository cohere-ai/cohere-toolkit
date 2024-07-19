'use client';

import Head from 'next/head';

/*
 * The meta tags for PWA pages.
 * This expects the following files are under the /public folder:
 * - /public/images/mushroom-filled-icon-512x512.png
 * - /public/images/favicon-32x32.png
 * - /public/images/favicon-16x16.png
 * - /public/images/apple-touch-icon.png
 * - /public/site.webmanifest
 */
export const WebManifestHead: React.FC = () => {
  return (
    <Head>
      <link rel="manifest" href="/site.webmanifest" />
      <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png" />
      <link
        rel="apple-touch-icon"
        sizes="512x512"
        href="/images/mushroom-filled-icon-512x512.png"
      />
      <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png" />
      <link rel="apple-touch-icon" sizes="32x32" href="/images/favicon-32x32.png" />
      <link rel="apple-touch-icon" sizes="16x16" href="/images/favicon-16x16.png" />
      <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png" />
      <meta name="msapplication-TileColor" content="#e8e6de" />
      <meta name="theme-color" content="#e8e6de" />
    </Head>
  );
};
