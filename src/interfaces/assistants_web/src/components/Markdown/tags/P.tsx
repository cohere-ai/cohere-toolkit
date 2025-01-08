'use client';

import { ComponentPropsWithoutRef, FC } from 'react';
import { ExtraProps } from 'react-markdown';

export const P: FC<ComponentPropsWithoutRef<'p'> & ExtraProps> = ({ children }) => {
  return <p dir="auto">{children}</p>;
};
