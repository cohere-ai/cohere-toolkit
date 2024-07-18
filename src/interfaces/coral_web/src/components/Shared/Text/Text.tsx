'use client';

import React, { ComponentPropsWithoutRef } from 'react';

import { cn } from '@/utils';

type AsElement = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'span' | 'p' | 'div' | 'li' | 'label' | 'pre';
type StyleAs = keyof typeof STYLE_LEVEL_TO_CLASSES;

type TextProps<T extends AsElement> = {
  as?: T;
  styleAs?: StyleAs;
  className?: string;
  role?: string;
  children?: React.ReactNode;
} & ComponentPropsWithoutRef<T>;

export const STYLE_LEVEL_TO_CLASSES = {
  h1: 'text-h1-m lg:text-h1 font-variable font-cuts-3',
  h2: 'text-h2-m lg:text-h2 font-variable font-cuts-2',
  h3: 'text-h3-m lg:text-h3 font-variable font-[420]',
  h4: 'text-h4-m lg:text-h4 font-variable font-[450]',
  h5: 'text-h5-m lg:text-h5 font-variable font-[420]',
  logo: 'text-logo lowercase font-variable',
  'p-lg': 'text-p-lg font-body',
  p: 'text-p font-body',
  'p-sm': 'text-p-sm font-body',
  'p-xs': 'text-p-xs font-body',
  overline: 'text-overline uppercase font-code',
  'label-sm': 'text-label-sm uppercase font-code',
  label: 'text-label uppercase font-code',
  caption: 'text-caption font-code',
  code: 'text-code font-code',
  'code-sm': 'text-code-sm font-code',
};

const getStyleLevelClasses = (level: StyleAs | AsElement) => {
  return STYLE_LEVEL_TO_CLASSES[level as StyleAs] ?? STYLE_LEVEL_TO_CLASSES.p;
};

/**
 * Convenience component to help apply the correct responsive styling to texts.
 *
 * In the nature design system, bolded fonts **always** use Cohere Variable. This behaviour
 * is reflected in `@cohere-ai/tailwind-themes/nature/fonts.css`.
 *
 * @param props.as - what HTML element it will render as
 * @param props.styleAs - what text styling will apply
 */
export const Text = <T extends AsElement>({
  as,
  styleAs,
  className = '',
  children,
  role,
  ...rest
}: TextProps<T>) => {
  const renderAs: AsElement = as ?? 'p';
  const classes = cn(getStyleLevelClasses(styleAs ?? renderAs), className);
  const Element = React.createElement(renderAs, { className: classes, role, ...rest }, children);

  return Element;
};
