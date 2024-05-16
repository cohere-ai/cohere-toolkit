import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
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
  const [loaded, setLoaded] = useState(false);
  const onload = (e: any) => {
    const iframe = e.target;
    if (loaded) {
      return;
    }
    // @ts-ignore
    const src = props['data-src'];
    if (!src) {
      return null;
    }
    iframe.src = src;
    setLoaded(true);

    // Adjust the height of the iframe to fit the content
    setTimeout(() => {
      const root = iframe.contentDocument.documentElement;
      const height = (root.offsetHeight || 0) + 16 + 4;
      iframe.style.height = Math.min(height, MIN_HEIGHT) + 'px';
    }, 500);
  };
  return (
    <iframe onLoad={onload} className="w-full rounded border-2 border-gray-500 bg-white p-2" />
  );
};
