import cx from 'classnames';
import { extendTailwindMerge } from 'tailwind-merge';

const customTwMerge = extendTailwindMerge({
  // @see: https://github.com/dcastil/tailwind-merge/blob/v1.14.0/docs/configuration.md#class-groups
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
        'min-w': [
          'citation-panel-md',
          'citation-panel-lg',
          'citation-panel-xl',
          'menu',
          'left-panel-lg',
          'left-panel-2xl',
          'left-panel-3xl',
        ],
      },
    ],
    'max-w': [
      {
        'max-w': [
          'modal-xs',
          'modal-sm',
          'modal-md',
          'modal',
          'modal-lg',
          'modal-xl',
          'container',
          'page',
          'drawer',
          'drawer-lg',
        ],
      },
    ],
    z: [{ z: ['navigation', 'modal', 'dropdown', 'toast'] }],
    w: [
      {
        w: [
          'modal',
          'ep-icon-sm',
          'ep-icon-md',
          'ep-icon-lg',
          'ep-icon-xl',
          'btn-sm',
          'btn-md',
          'btn-lg',
          'btn-xl',
        ],
      },
    ],
    h: [{ h: ['ep-icon-sm', 'ep-icon-md', 'ep-icon-lg', 'ep-icon-xl'] }],
    'max-h': [{ 'max-h': ['cell-xs', 'cell-sm', 'cell-md', 'cell-lg', 'cell-xl'] }],
    'min-h': [{ 'min-h': ['cell-xs', 'cell-sm', 'cell-md', 'cell-lg', 'cell-xl'] }],
  },
});

/**
 * Combines classnames with tailwind-merge
 */
export function cn(...inputs: cx.ArgumentArray) {
  return customTwMerge(cx(inputs));
}
