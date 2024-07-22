'use client';

import { type ReactElement } from 'react';

import { IconName, Text } from '@/components/Shared';
import {
  CellButton,
  type CellButtonProps,
  type CellButtonTheme,
} from '@/components/Shared/Button/CellButton';
import {
  MinimalButton,
  MinimalButtonProps,
  type MinimalButtonSize,
} from '@/components/Shared/Button/MinimalButton';
import { cn } from '@/utils';

type CellButtonKind = 'primary' | 'primaryOutline' | 'danger' | 'volcanic' | 'green';
export type ButtonKind = CellButtonKind | 'secondary';

const BUTTON_KIND_THEMES: Record<CellButtonKind, CellButtonTheme> = {
  primary: {
    cellKind: 'default',
    theme: 'primary',
    hoverTheme: 'primary',
    focusTheme: 'volcanicLight',
    disabledTheme: 'gray',
    leftCell: false,
    rightCell: true,
  },
  danger: {
    cellKind: 'default',
    theme: 'danger',
    hoverTheme: 'dangerDark',
    focusTheme: 'volcanicLight',
    disabledTheme: 'gray',
    leftCell: false,
    rightCell: true,
  },

  primaryOutline: {
    cellKind: 'outline',
    theme: 'primary',
    disabledTheme: 'primary',
    focusTheme: 'primary',
    hoverTheme: 'primary',
    leftCell: false,
    rightCell: false,
  },
  volcanic: {
    cellKind: 'default',
    theme: 'volcanic',
    hoverTheme: 'volcanic',
    focusTheme: 'volcanicLight',
    disabledTheme: 'gray',
    leftCell: false,
    rightCell: true,
  },
  green: {
    cellKind: 'default',
    theme: 'green',
    hoverTheme: 'green',
    focusTheme: 'green',
    disabledTheme: 'gray',
    leftCell: false,
    rightCell: true,
  },
};

type Props =
  | (CellButtonProps & { kind?: ButtonKind })
  | (MinimalButtonProps & {
      kind?: ButtonKind;
      size?: MinimalButtonSize;
      startIcon?: ReactElement | IconName;
    });

/**
 * Component that renders a `CellButton` or a `MinimalButton`.
 */
export const Button: React.FC<Props> = (props) => {
  const { kind = 'primary', label, theme, ...buttonProps } = props;
  const isLabelString = typeof label === 'string';

  if (kind === 'secondary') {
    const { size, ...minimalButtonProps } = buttonProps;
    const wrappedLabel = isLabelString ? (
      <Text as="span" styleAs={size === 'lg' ? 'p-lg' : 'p'}>
        {label}
      </Text>
    ) : (
      label
    );

    const minimalButtonTheme = typeof theme === 'string' ? theme : 'volcanic';

    return (
      <MinimalButton
        {...minimalButtonProps}
        size={size === 'sm' ? 'sm' : 'md'}
        label={wrappedLabel}
        theme={minimalButtonTheme}
        hideFocusStyles
        className={cn(
          'border-y border-y-transparent focus-visible:border-b-black focus-visible:outline-none',
          minimalButtonProps.className
        )}
      />
    );
  }

  const wrappedLabel = isLabelString ? (
    <Text as="span" styleAs={buttonProps.size === 'lg' ? 'p-lg' : 'p'}>
      {label}
    </Text>
  ) : (
    label
  );

  return (
    <CellButton
      {...buttonProps}
      label={wrappedLabel}
      theme={BUTTON_KIND_THEMES[kind]}
      shouldCenterContent
    />
  );
};
