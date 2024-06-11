import { throttle } from 'lodash';
import { useEffect, useMemo, useState } from 'react';
import { Config } from 'tailwindcss';
import resolveConfig from 'tailwindcss/resolveConfig';

import tailwindConfig from '../../tailwind.config';

const fullConfig = resolveConfig(tailwindConfig as unknown as Config);

export enum Breakpoint {
  sm = 'sm',
  md = 'md',
  lg = 'lg',
  xl = 'xl',
  '2xl' = '2xl',
}

const screens = fullConfig.theme?.screens as Record<Breakpoint, string>;
const parseScreen = (screen: string) => parseInt(screen.replace('px', ''));
const MD_WIDTH = parseScreen(screens.md);
const LG_WIDTH = parseScreen(screens.lg);
const XL_WIDTH = parseScreen(screens.xl);
const TWO_XL_WIDTH = parseScreen(screens['2xl']);

const getDeviceConfig = (width: number): Breakpoint => {
  if (width < MD_WIDTH) {
    return Breakpoint.sm;
  } else if (width >= MD_WIDTH && width < LG_WIDTH) {
    return Breakpoint.md;
  } else if (width >= LG_WIDTH && width < XL_WIDTH) {
    return Breakpoint.lg;
  } else if (width >= XL_WIDTH && width < TWO_XL_WIDTH) {
    return Breakpoint.xl;
  } else {
    return Breakpoint['2xl'];
  }
};

export const useBreakpoint = () => {
  const [breakingPoint, setBreakingPoint] = useState<Breakpoint>();

  useEffect(() => {
    setBreakingPoint(getDeviceConfig(window.innerWidth));
    const calculateInnerWidth = throttle(function () {
      setBreakingPoint(getDeviceConfig(window.innerWidth));
    }, 500);
    window.addEventListener('resize', calculateInnerWidth);
    return () => window.removeEventListener('resize', calculateInnerWidth);
  }, []);

  return breakingPoint;
};

export const useIsDesktop = (): boolean => {
  const breakpoint = useBreakpoint();
  const isDesktop = useMemo(
    () =>
      breakpoint === Breakpoint.lg ||
      breakpoint === Breakpoint.xl ||
      breakpoint === Breakpoint['2xl'],
    [breakpoint]
  );

  return isDesktop;
};

export const useIsSmBreakpoint = (): boolean => {
  const breakpoint = useBreakpoint();
  const isSm = useMemo(() => breakpoint === Breakpoint.sm, [breakpoint]);
  return isSm;
};

export const getIsTouchDevice = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(hover: none)').matches;
};
