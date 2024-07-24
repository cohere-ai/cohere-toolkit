'use client';

import { Button, Text } from '@/components/Shared';
import { useCitationsStore } from '@/stores';
import { base64ToBlobUrl, guessFileType } from '@/utils';

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
    return <B64Image data={outputFiles[fileName].data} fileName={fileName} caption={caption} />;
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

const IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'];

export const B64Image: React.FC<{ data: string; fileName: string; caption?: string }> = ({
  data,
  fileName,
  caption,
}) => {
  if (!fileName) {
    return null;
  }

  if (IMAGE_FORMATS.some((format) => fileName.endsWith(format))) {
    return (
      <>
        <img className="w-full" src={`data:image/png;base64,${data}`} alt={caption} />
        {caption && (
          <Text as="span" styleAs="caption" className="mb-2 text-mushroom-300">
            {caption}
          </Text>
        )}
      </>
    );
  }

  // TODO(tomeu): model should not send downloable files as images. 
  // Remove when model is fixed.
  const fileType = guessFileType(fileName);
  const blobUrl = base64ToBlobUrl(data, fileType);

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = fileName;
    a.click();
  };

  return (
    <Button kind="secondary" onClick={handleDownload}>
      {fileName}
    </Button>
  );
};
