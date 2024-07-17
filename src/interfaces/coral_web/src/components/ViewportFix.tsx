'use client';

import { useEffect } from 'react';

export const ViewportFix: React.FC = () => {
  useEffect(() => {
    const doc = document.documentElement;
    const customVar = '--vh';
    let prevClientHeight: number;
    function handleResize() {
      const { clientHeight } = doc;
      if (clientHeight === prevClientHeight) return;
      requestAnimationFrame(function updateViewportHeight() {
        doc.style.setProperty(customVar, clientHeight * 0.01 + 'px');
        prevClientHeight = clientHeight;
      });
    }
    // Initial resize
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return null;
};
