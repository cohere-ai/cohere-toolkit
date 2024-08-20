import cx from 'classnames';
import { extendTailwindMerge } from 'tailwind-merge';

const customTwMerge = extendTailwindMerge({
  extend: {
    // @see: https://github.com/dcastil/tailwind-merge/blob/v2.5.2/docs/configuration.md#class-groups
    classGroups: {
      'font-size': [
        {
          text: [
            'caption',
            'label-sm',
            'label',
            'overline',
            'p-xs',
            'p-sm',
            'p',
            'p-lg',
            'code',
            'code-sm',
            'logo',
            'h5',
            'h5-m',
            'h4',
            'h4-m',
            'h3',
            'h3-m',
            'h2',
            'h2-m',
            'h1',
            'h1-m',
          ],
        },
      ],
      'min-w': [
        {
          'min-w': ['menu', 'left-panel-collapsed', 'left-panel-expanded'],
        },
      ],
      'max-w': [
        {
          'max-w': ['message', 'left-panel-collapsed', 'left-panel-expanded', 'share-content'],
        },
      ],
      z: [
        {
          z: [
            'navigation',
            'dropdown',
            'tag-suggestions',
            'drag-drop-input-overlay',
            'read-only-conversation-footer',
            'menu',
            'guide-tooltip',
            'tooltip',
            'backdrop',
            'modal',
          ],
        },
      ],
      w: [
        {
          w: ['modal', 'ep-icon-sm', 'ep-icon-md', 'ep-icon-lg', 'ep-icon-xl'],
        },
      ],
      h: [{ h: ['ep-icon-sm', 'ep-icon-md', 'ep-icon-lg', 'ep-icon-xl'] }],
      'max-h': [{ 'max-h': ['cell-xs', 'cell-sm', 'cell-md', 'cell-lg', 'cell-xl', 'modal'] }],
      'min-h': [{ 'min-h': ['cell-xs', 'cell-sm', 'cell-md', 'cell-lg', 'cell-xl'] }],
      shadow: [
        {
          shadow: ['menu', 'top'],
        },
      ],
    },
  },
});

/**
 * Combines classnames with tailwind-merge
 */
export function cn(...inputs: cx.ArgumentArray) {
  return customTwMerge(cx(inputs));
}
