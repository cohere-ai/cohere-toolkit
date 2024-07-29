'use client';

import React from 'react';

import { Button, ButtonTheme, IconName } from '@/components/Shared';
import { useAuthConfig } from '@/hooks/authConfig';

type Props = {
  action: 'login' | 'register' | 'logout';
  icon?: IconName;
  iconPosition?: 'start' | 'end';
  theme?: ButtonTheme;
  cellButton?: boolean;
  redirect?: string;
  className?: string;
};

/**
 * A helper UI component for navigating users to the different auth actions in both auth host and
 * client apps
 */
export const AuthLink: React.FC<Props> = ({
  action,
  icon,
  iconPosition = 'end',
  theme,
  cellButton = false,
  redirect,
  className = '',
}) => {
  // context for auth provider
  const authConfig = useAuthConfig();

  let href = '';
  let label = '';
  const searchParams = new URLSearchParams({
    ...(redirect ? { redirect_uri: redirect } : {}),
  });
  const searchString = searchParams.toString().length > 0 ? `?${searchParams.toString()}` : '';
  switch (action) {
    case 'login':
      href = `${authConfig.loginUrl}${searchString}`;
      label = 'Log in';
      break;
    case 'register':
      href = `${authConfig.registerUrl}${searchString}`;
      label = 'Sign up';
      break;
    case 'logout':
      href = `${authConfig.logoutUrl}`;
      label = 'Log out';
      break;
  }

  return (
    <Button
      label={label}
      href={href}
      kind={cellButton ? 'cell' : 'secondary'}
      theme={theme}
      icon={icon}
      iconPosition={iconPosition}
      className={className}
      id="auth-link"
    />
  );
};
