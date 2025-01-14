'use client';

import { ComponentPropsWithoutRef, FC } from 'react';
import { ExtraProps } from 'react-markdown';

import { Text } from '@/components/UI';

// Since we're inserting a Text component
// And that we're not specifyng the "as" prop
// And that the default of Text is "p" styling
// We get the props of p
export const References: FC<ComponentPropsWithoutRef<'p'> & ExtraProps> = ({ children }) => {
  return <Text>From {children}</Text>;
};
