import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { useEffect } from 'react';
import { useRef } from 'react';
import { useState } from 'react';
import { ComponentPropsWithoutRef } from 'react';

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
  const onload = (e: any) => {
    const iframe = e.target;
    const root = iframe.contentDocument.documentElement;
    const height = (root.offsetHeight || 0) + 16 + 4;
    iframe.style.height = Math.min(height, MIN_HEIGHT) + 'px';
  };

  useEffect(() => {
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.addEventListener('load', onload, { once: true });
      return () => {
        iframe.removeEventListener('load', onload);
      };
    }
  }, []);

  // @ts-ignore
  const src = props['data-src'];

  return (
    <iframe
      src={src}
      ref={iframeRef}
      className="w-full p-2 bg-white border-2 border-gray-500 rounded"
    />
  );
};
