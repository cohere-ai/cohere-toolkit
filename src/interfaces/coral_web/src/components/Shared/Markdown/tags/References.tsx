'use client';

import type { Component, ExtraProps } from 'hast-util-to-jsx-runtime/lib/components';
import { ComponentPropsWithoutRef } from 'react';

import { Text } from '@/components/Shared';

// Since we're inserting a Text component
// And that we're not specifyng the "as" prop
// And that the default of Text is "p" styling
// We get the props of p
export const References: Component<ComponentPropsWithoutRef<'p'> & ExtraProps> = ({ children }) => {
  return <Text>From {children}</Text>;
};
