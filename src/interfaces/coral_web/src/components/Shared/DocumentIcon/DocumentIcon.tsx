import Image from 'next/image';
import { useEffect, useState } from 'react';

import { Icon, IconName, IconProps } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  url: string;
  icon?: IconName;
  className?: string;
  iconKind?: IconProps['kind'];
};

// Returns the primary domain name of a url,
// e.g. https://www.google.com -> google.com
// e.g. https://www.google.co.uk -> google.co.uk
// e.g. https://www.en.wikipedia.co.uk/search?q=hello -> wikipedia.co.uk
// e.g. not-a-valid-url --> ''
const getPrimaryDomain = (url: string) => {
  if (!url) return '';
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.split('.');
    if (hostname.length <= 2) {
      return hostname.join('.');
    }
    // Remove subdomain
    hostname.shift();
    return hostname.join('.');
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
  className = '',
  iconKind = 'outline',
}) => {
  const [error, setError] = useState<boolean | null>(null);
  const domain = getPrimaryDomain(url);

  useEffect(() => {
    setError(null);
  }, [url]);

  return (
    <div className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded', className)}>
      {icon ? (
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
