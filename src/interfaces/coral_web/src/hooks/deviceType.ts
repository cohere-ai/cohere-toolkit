import is from 'is_js';
import { useEffect, useState } from 'react';

interface UseDeviceType {
  isDesktop: boolean;
  isTablet: boolean;
  isMobile: boolean;
}

/*
 * Using is_js libary to check device types to aid with performant rendering.
 * Include additional checks as needed.
 *
 * The device checks are wrapped in a useEffect to avoid dom hydration issues
 *
 * Usage:
 * const { isDesktop } = useDeviceType()
 */
export const useDeviceType = (): UseDeviceType => {
  const [isDesktop, setIsDesktop] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    setIsDesktop(is.desktop());
    setIsTablet(is.tablet());
    setIsMobile(is.mobile());
  }, []);

  return { isDesktop, isTablet, isMobile };
};
