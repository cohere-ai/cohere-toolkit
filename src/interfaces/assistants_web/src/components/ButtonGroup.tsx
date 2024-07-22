'use client';

import { MouseEventHandler } from 'react';

import { CellButton } from '@/components/Shared/Button/CellButton';
import { Text } from '@/components/Shared/Text';

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
        <CellButton
          key={i}
          size="sm"
          shouldCenterContent
          theme={{
            cellKind: 'outline',
            theme: 'secondary',
            disabledTheme: 'volcanicLight',
            focusTheme: 'volcanicLight',
            hoverTheme: 'secondaryDark',
            leftCell: i > 0,
            rightCell: i < total - 1,
          }}
          animate={false}
          onClick={button.onClick}
        >
          <Text>{button.label}</Text>
        </CellButton>
      ))}
    </>
  );
};

export default ButtonGroup;
