import type { Component } from 'hast-util-to-jsx-runtime/lib/components';
import { useEffect } from 'react';
import { useRef } from 'react';
import { useState } from 'react';
import { ComponentPropsWithoutRef } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter/dist/cjs/prism-light';
import theme from 'react-syntax-highlighter/dist/cjs/styles/prism/atom-dark';

import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

const MIN_HEIGHT = 600;

/**
 * Renders an iframe with a lazy loading mechanism.
 *
 * The iframe is initially rendered with a `data-src` attribute that points to a blob URL.
 * When the iframe is loaded, the `data-src` attribute is replaced with the actual source URL.
 * The height of the iframe is adjusted to fit the content.
 */
export const Iframe: Component<ComponentPropsWithoutRef<'iframe'> & { 'data-src': string }> = (
  props
) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [option, setOption] = useState<'live' | 'code'>('live');
  const [code, setCode] = useState('');
  const src = props[`data-src`];

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
    <div>
      <div className="rounded rounded-b-none border border-b-0 border-marble-500 bg-secondary-50 p-2">
        <iframe
          srcDoc={code}
          ref={iframeRef}
          className={cn('max-h-[900px] min-h-[150px] w-full resize-y rounded-lg bg-white', {
            hidden: option !== 'live',
          })}
        />
        <pre
          className={cn('language-html max-h-[900px]  min-h-[150px] bg-[#1d1f21]', {
            hidden: option !== 'code',
          })}
        >
          <SyntaxHighlighter style={theme} language="html">
            {code}
          </SyntaxHighlighter>
        </pre>
      </div>
      <div className="flex justify-end gap-2 rounded rounded-t-none border border-t-0 border-marble-500 bg-secondary-50 px-4 py-2">
        <div className="space-x-2 rounded-lg border border-marble-400 bg-white p-[2.5px]">
          <button
            className={cn('w-[42px] py-2 transition-colors', {
              'rounded-lg bg-secondary-300': option === 'live',
            })}
            onClick={() => setOption('live')}
          >
            <Text styleAs="caption">App</Text>
          </button>
          <button
            className={cn('w-[42px] py-2 transition-colors', {
              'rounded-lg bg-secondary-300': option === 'code',
            })}
            onClick={() => setOption('code')}
          >
            <Text styleAs="caption">Code</Text>
          </button>
        </div>
      </div>
    </div>
  );
};
