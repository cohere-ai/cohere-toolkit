'use client';

import { useMemo } from 'react';

import { COHERE_BRANDED_COLORS } from '@/constants';
import { cn } from '@/utils/cn';

const COHERE_THEMES_MAP: { default: COHERE_BRANDED_COLORS; branded: COHERE_BRANDED_COLORS[] } = {
  default: 'evolved-blue',
  branded: ['green', 'coral', 'evolved-quartz', 'evolved-mushroom', 'evolved-green', 'mushroom'],
};

const ASSISTANT_COLORS = [
  'green-500',
  'coral-600',
  'evolved-quartz-500',
  'evolved-mushroom-500',
  'evolved-green-500',
  'mushroom-700',
];
const ASSISTANT_CONTRAST_COLORS = [
  'marble-950',
  'volcanic-100',
  'marble-950',
  'volcanic-100',
  'volcanic-100',
  'mushroom-300',
];
const DEFAULT_COLOR = 'evolved-blue-500';
const DEFAULT_CONTRAST_COLOR = 'blue-800';

const getAssistantColor = (assistantId: string | undefined): string => {
  if (!assistantId) return DEFAULT_COLOR;

  const idNumber = assistantId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % ASSISTANT_COLORS.length;

  return ASSISTANT_COLORS[index];
};

const getAssistantContrastColor = (assistantId: string | undefined): string => {
  if (!assistantId) return DEFAULT_CONTRAST_COLOR;

  const idNumber = assistantId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % ASSISTANT_CONTRAST_COLORS.length;
  return ASSISTANT_CONTRAST_COLORS[index];
};

export const getCohereTheme = (assistantId?: string): COHERE_BRANDED_COLORS => {
  if (assistantId === undefined) {
    return COHERE_THEMES_MAP.default;
  } else {
    const idNumber = assistantId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const index = idNumber % COHERE_THEMES_MAP.branded.length;
    return COHERE_THEMES_MAP.branded[index];
  }
};

const getDarkMode = (color: string) => `dark:${color}`;
const getHover = (color: string) => `hover:${color}`;
const getText = (color: string) => `text-${color}`;
const getBg = (color: string) => `bg-${color}`;
const getFill = (color: string) => `fill-${color}`;
const getBorder = (color: string) => `border-${color}`;

interface Context {
  hover: (color: string) => string;
  theme: COHERE_BRANDED_COLORS;
  text: string;
  bg: string;
  fill: string;
  border: string;
  contrastText: string;
  contrastBg: string;
  contrastFill: string;
  contrastBorder: string;
}

export const useBrandedColors = (assistantId?: string): Context => {
  const color = useMemo(() => getAssistantColor(assistantId), [assistantId]);
  const contrastColor = useMemo(() => getAssistantContrastColor(assistantId), [assistantId]);

  const colors = {
    theme: getCohereTheme(assistantId),
    text: cn(getText(color), getDarkMode(getText(color))),
    bg: cn(getBg(color), getDarkMode(getBg(color))),
    fill: cn(getFill(color), getDarkMode(getFill(color))),
    border: cn(getBorder(color), getDarkMode(getBorder(color))),
    contrastText: cn(getText(contrastColor), getDarkMode(getText(contrastColor))),
    contrastBg: cn(getBg(contrastColor), getDarkMode(getBg(contrastColor))),
    contrastFill: cn(getFill(contrastColor), getDarkMode(getFill(contrastColor))),
    contrastBorder: cn(getBorder(contrastColor), getDarkMode(getBorder(contrastColor))),
  };

  const hover = (color: string) => {
    return color
      .split(' ')
      .map((c) => {
        if (c.includes('dark:')) return getDarkMode(getHover(c));
        return getHover(c);
      })
      .join(' ');
  };

  return { ...colors, hover };
};
