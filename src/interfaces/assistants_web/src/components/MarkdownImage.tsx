'use client';

import { Text } from '@/components/Shared';
import { useCitationsStore } from '@/stores';

type Props = {
  node: {
    properties: {
      alt: string;
      src: string;
    };
  };
};

/**
 * @description Renders an image markdown node. Inserts files from the citations
 * store if they exist as a base64 image, otherwise uses the file path.
 */
export const MarkdownImage: React.FC<Props> = ({ node }) => {
  const {
    citations: { outputFiles },
  } = useCitationsStore();

  const caption = node.properties.alt;
  // Remove quotes from the url
  const fileName = decodeURIComponent(node.properties.src).replace(/['"]/g, '');

  if (outputFiles[fileName]) {
    return <B64Image data={outputFiles[fileName].data} caption={caption} />;
  } else {
    return (
      <>
        <img className="w-full" src={fileName} alt={caption} />
        {caption && (
          <Text as="span" styleAs="caption" className="mb-2 text-mushroom-300">
            {caption}
          </Text>
        )}
      </>
    );
  }
};

export const B64Image: React.FC<{ data: string; caption?: string }> = ({ data, caption }) => {
  return (
    <>
      <img className="w-full dark:invert" src={`data:image/png;base64,${data}`} alt={caption} />
      {caption && (
        <Text
          as="span"
          styleAs="caption"
          className="mb-2 text-mushroom-300 dark:bg-[#3D3B36] dark:text-mushroom-950"
        >
          {caption}
        </Text>
      )}
    </>
  );
};
