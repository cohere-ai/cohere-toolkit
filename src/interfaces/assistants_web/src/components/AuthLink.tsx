'use client';

import React, { ReactElement } from 'react';

import { Button, ButtonKind, IconName, InlineLink } from '@/components/Shared';
import { useAuthConfig } from '@/hooks/authConfig';

type Props = {
  action: 'login' | 'register' | 'logout';
  styleAs?: 'link' | 'button';
  endIcon?: ReactElement | IconName;
  splitIcon?: ReactElement | IconName;
  kind?: ButtonKind;
  redirect?: string;
  className?: string;
};

/**
 * A helper UI component for navigating users to the different auth actions in both auth host and
 * client apps
 */
export const AuthLink: React.FC<Props> = ({
  styleAs = 'link',
  action,
  kind,
  endIcon,
  splitIcon,
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

  return styleAs === 'button' ? (
    <Button
      label={label}
      href={href}
      kind={kind}
      endIcon={endIcon}
      splitIcon={splitIcon}
      className={className}
      id="auth-link"
    />
  ) : (
    <InlineLink label={label} href={href} endIcon={endIcon} className={className} />
  );
};
