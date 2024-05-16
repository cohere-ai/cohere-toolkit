import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { useEffect } from 'react';
import { useRef } from 'react';
import { useState } from 'react';
import { ComponentPropsWithoutRef } from 'react';

import { cn } from '@/utils';

const MIN_HEIGHT = 400;

/**
 * Renders an iframe with a lazy loading mechanism.
 *
 * The iframe is initially rendered with a `data-src` attribute that points to a blob URL.
 * When the iframe is loaded, the `data-src` attribute is replaced with the actual source URL.
 * The height of the iframe is adjusted to fit the content.
 */
export const Iframe: Component<ComponentPropsWithoutRef<'iframe'> & ExtraProps> = (props) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [option, setOption] = useState<'live' | 'code'>('live');
  const [code, setCode] = useState('');

  const onload = (e: any) => {
    const iframe = e.target;
    const root = iframe.contentDocument.documentElement;
    const height = (root.offsetHeight || 0) + 16 + 4;
    iframe.style.height = Math.min(height, MIN_HEIGHT) + 'px';
  };

  useEffect(() => {
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.addEventListener('load', onload);
      return () => {
        iframe.removeEventListener('load', onload);
      };
    }
  }, []);

  // @ts-ignore
  const src = props['data-src'];

  useEffect(() => {
    // read the blob URL (src) and extract the text into the code state
    if (src) {
      fetch(src)
        .then((res) => res.text())
        .then((text) => {
          setCode(text.trim());
        });
    }
  }, [src]);

  return (
    <div className="relative">
      <div className="flex gap-2 rounded rounded-b-none border-2 border-b-0 border-gray-500 bg-stone-200 px-4 py-2">
        <button
          className={cn({
            'border-b border-gray-500 font-medium': option === 'live',
          })}
          onClick={() => setOption('live')}
        >
          Live Preview
        </button>
        <button
          className={cn({
            'border-b border-gray-500 font-medium': option === 'code',
          })}
          onClick={() => setOption('code')}
        >
          View Code
        </button>
      </div>
      <div className="rounded rounded-t-none border-2 border-t-0 border-gray-500 bg-white p-2">
        <iframe
          srcDoc={code}
          ref={iframeRef}
          className={cn('max-h-[900px] min-h-[150px] w-full resize-y ', {
            hidden: option !== 'live',
          })}
        />
        <pre
          className={cn('language-html', {
            hidden: option !== 'code',
          })}
        >
          <code className="">{code}</code>
        </pre>
      </div>
    </div>
  );
};
