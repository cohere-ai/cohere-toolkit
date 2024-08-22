'use client';

import Head from 'next/head';

/*
 * Some basic meta tag values for the site.
 */
export const GlobalHead: React.FC = () => {
  const description =
    'Cohere provides access to advanced Large Language Models and NLP tools through one easy-to-use API. Get started for free.';

  return (
    <Head>
      <link rel="icon" href="/favicon.ico" />
      <meta name="description" content={description} />
      <meta
        name="viewport"
        content="initial-scale=1.0, width=device-width, viewport-fit=cover, maximum-scale=1.0"
      />

      <meta property="og:description" content={description} />
      <meta property="og:image" content="/images/share.png" />
      <meta property="og:image:width" content="800" />
      <meta property="og:image:height" content="600" />
      <meta property="og:site_name" content="Cohere" />
    </Head>
  );
};
