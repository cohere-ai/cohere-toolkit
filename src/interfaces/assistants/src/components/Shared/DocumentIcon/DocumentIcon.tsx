'use client';

import type { StaticImport } from 'next/dist/shared/lib/get-img-props';
import Image from 'next/image';
import { useEffect, useState } from 'react';

import { Icon, IconName, IconProps } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  url?: string;
  toolIcon?: StaticImport;
  icon?: IconName;
  className?: string;
  iconKind?: IconProps['kind'];
};

// Returns the domain name of a url,
// e.g. https://www.google.com -> www.google.com
// e.g. https://www.google.co.uk -> www.google.co.uk
// e.g. https://en.wikipedia.co.uk/search?q=hello -> en.wikipedia.co.uk
// e.g. not-a-valid-url --> ''
const getHostname = (url?: string) => {
  if (!url) return '';
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
};

/**
 * Renders the favicon for a given url or the given icon with a background.
 */
export const DocumentIcon: React.FC<Props> = ({
  icon,
  url,
  toolIcon,
  className = '',
  iconKind = 'outline',
}) => {
  const [error, setError] = useState<boolean | null>(null);
  const domain = getHostname(url);

  useEffect(() => {
    setError(null);
  }, [url]);

  return (
    <div className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded', className)}>
      {toolIcon ? (
        <Image
          src={toolIcon}
          alt={`Icon for ${domain}`}
          width={16}
          height={16}
          onError={() => setError(true)}
        />
      ) : icon ? (
        <Icon name={icon} kind={iconKind} />
      ) : domain === '' ? (
        <Icon name="file" kind={iconKind} />
      ) : error ? (
        <Icon name="web" kind={iconKind} />
      ) : (
        <Image
          src={`https://www.google.com/s2/favicons?domain=${domain}`}
          alt={`Favicon for ${domain}`}
          width={16}
          height={16}
          onError={() => setError(true)}
        />
      )}
    </div>
  );
};
