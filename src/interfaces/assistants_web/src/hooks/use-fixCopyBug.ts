import { useEventListener } from '@react-hookz/web';

/**
 * This hook fixes the bug where the copied text has a lot of spaces in Chrome
 */
export const useFixCopyBug = () => {
  const target = typeof document !== 'undefined' ? document : null;
  useEventListener(target, 'copy', async (event: Event) => {
    const selectedText = window.getSelection()?.toString().trim();
    if (selectedText) {
      event.preventDefault(); // Prevents the default copy behavior
      const modifiedText = selectedText?.trim();
      try {
        await window?.navigator?.clipboard.writeText(modifiedText);
      } catch (e) {
        console.error(e);
      }
    }
  });
};
