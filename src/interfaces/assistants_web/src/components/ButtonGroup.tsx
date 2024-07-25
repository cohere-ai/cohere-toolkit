'use client';

import { MouseEventHandler } from 'react';

import { NewButton } from '@/components/Shared';

type Props = {
  buttons: Array<{
    label: string;
    onClick: MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  }>;
};

/**
 * Renders a group of slanted buttons where middle buttons will slant in the same direction.
 * e.g. visually below:
 * ________  ________  _______
 * |______/ /_______/ /______|
 */
const ButtonGroup: React.FC<Props> = ({ buttons }) => {
  const total = buttons.length;
  return (
    <>
      {buttons.map((button, i) => (
        <NewButton
          key={i}
          animate={false}
          onClick={button.onClick}
          label={button.label}
          kind="outline"
          theme="mushroom-marble"
        />
      ))}
    </>
  );
};

export default ButtonGroup;
