import { Config } from 'tailwindcss';
import resolveConfig from 'tailwindcss/resolveConfig';

import tailwindConfig from '../../tailwind.config.js';

export const fullConfig = resolveConfig(tailwindConfig as unknown as Config);
export const colors = fullConfig?.theme?.colors as unknown as {
  white: string;
  black: string;
  inherit: string;
  volcanic: { [name: string]: string };
  marble: { [name: string]: string };
  green: { [name: string]: string };
  coral: { [name: string]: string };
  blue: { [name: string]: string };
  quartz: { [name: string]: string };
  success: { [name: string]: string };
  danger: { [name: string]: string };
};

export const screens = fullConfig?.theme?.screens as unknown as {
  [name: string]: string;
};

export const fontSize = fullConfig?.theme?.fontSize as unknown as {
  [name: string]: [string, { letterSpacing: string; lineHeight: string }];
};
export const fontFamily = fullConfig?.theme?.fontFamily as unknown as {
  body: string[];
  mono: string[];
};
export const zIndex = fullConfig?.theme?.zIndex as unknown as { [name: string]: string };
export const height = fullConfig?.theme?.height as unknown as { [name: string]: string };
export const boxShadow = fullConfig?.theme?.boxShadow as unknown as { [name: string]: string };
export const borderRadius = fullConfig?.theme?.borderRadius as unknown as {
  [name: string]: string;
};
export const backgroundColor = fullConfig?.theme?.backgroundColor as unknown as {
  [name: string]: string;
};
export const padding = fullConfig?.theme?.padding as unknown as {
  [name: string]: string;
};
