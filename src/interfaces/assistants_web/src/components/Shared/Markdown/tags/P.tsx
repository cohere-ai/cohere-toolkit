'use client';

import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

export const P: Component<ComponentPropsWithoutRef<'p'> & ExtraProps> = ({ children }) => {
  return <p dir="auto">{children}</p>;
};
