'use client';

import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/react';
import type { Component } from 'hast-util-to-jsx-runtime/lib/components';
import { Fragment, useEffect } from 'react';
import { useRef } from 'react';
import { useState } from 'react';
import { ComponentPropsWithoutRef } from 'react';

import { CodeSnippet } from '@/components/Shared/CodeSnippet';
import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';
import { cleanupCodeBlock } from '@/utils/preview';

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
  const [code, setCode] = useState('');
  const [codePreview, setCodePreview] = useState('');
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
          setCodePreview(cleanupCodeBlock(text).trim());
          //
        });
    }
  }, [src]);

  return (
    <TabGroup>
      <TabPanels>
        <TabPanel>
          <iframe
            srcDoc={code}
            ref={iframeRef}
            className="max-h-[450px] min-h-[450px] w-full overflow-y-auto rounded-lg border border-mushroom-800 bg-white"
          />
        </TabPanel>
        <TabPanel>
          <CodeSnippet
            customStyle={{ minHeight: '450px', maxHeight: '450px', overflowY: 'auto' }}
            preview
            lang="html"
            codeSnippet={codePreview}
          />
        </TabPanel>
      </TabPanels>
      <TabList className="ml-auto mt-2 flex w-fit gap-x-2 rounded bg-mushroom-900 p-1">
        <Tab as={Fragment}>
          {({ selected }) => (
            <button
              className={cn(
                'w-[60px] rounded p-1 outline-none transition-colors hover:bg-mushroom-800',
                {
                  'bg-mushroom-800 shadow hover:bg-mushroom-800': selected,
                }
              )}
            >
              <Text styleAs="p-sm">Preview</Text>
            </button>
          )}
        </Tab>
        <Tab as={Fragment}>
          {({ selected }) => (
            <button
              className={cn(
                'w-[60px] rounded p-1 outline-none transition-colors hover:bg-mushroom-800',
                {
                  'bg-mushroom-800 shadow hover:bg-mushroom-800': selected,
                }
              )}
            >
              <Text styleAs="p-sm">Code</Text>
            </button>
          )}
        </Tab>
      </TabList>
    </TabGroup>
  );
};
