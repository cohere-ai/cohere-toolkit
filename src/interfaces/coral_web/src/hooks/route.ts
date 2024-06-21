import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

type RouteChangeOptions = {
  onRouteChangeStart?: (destRoute: string) => void;
  onRouteChangeComplete?: (destRoute: string) => void;
};

export const useRouteChange = (options?: RouteChangeOptions) => {
  const [isRouteChanging, setIsRouteChanging] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const handleRouteChangeStart = (destRoute: string) => {
      setIsRouteChanging(true);
      options?.onRouteChangeStart?.(destRoute);
    };
    const handleRouteChangeComplete = (destRoute: string) => {
      setIsRouteChanging(false);
      options?.onRouteChangeComplete?.(destRoute);
    };
    router.events.on('routeChangeStart', handleRouteChangeStart);
    router.events.on('routeChangeComplete', handleRouteChangeComplete);
    return () => {
      router.events.off('routeChangeStart', handleRouteChangeStart);
      router.events.off('routeChangeComplete', handleRouteChangeComplete);
    };
  }, [router.events, options]);

  return [isRouteChanging];
};
