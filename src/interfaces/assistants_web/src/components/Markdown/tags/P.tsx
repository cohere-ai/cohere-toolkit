'use client';

import { ExtraProps } from 'react-markdown';
import { ComponentPropsWithoutRef, FC } from 'react';

export const P: FC<ComponentPropsWithoutRef<'p'> & ExtraProps> = ({ children }) => {
  return <p dir="auto">{children}</p>;
};
