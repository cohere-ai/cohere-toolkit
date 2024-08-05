'use client';

import { Button } from '@/components/Shared';
import { cn } from '@/utils';

type ButtonProps = {
  onClick: () => void;
  service?: string;
  className?: string;
};

const googleLogo = (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 0 24 24" width="20">
    <path
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      fill="#4285F4"
    />
    <path
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      fill="#34A853"
    />
    <path
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      fill="#FBBC05"
    />
    <path
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      fill="#EA4335"
    />
    <path d="M1 1h22v22H1z" fill="none" />
  </svg>
);

const oidLogo = (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    version="1.0"
    width="30"
    height="120"
    viewBox="0 -50 150 240"
    id="svg2593"
  >
    <defs id="defs2596">
      <clipPath id="clipPath2616">
        <path d="M 0,14400 L 14400,14400 L 14400,0 L 0,0 L 0,14400 z" id="path2618" />
      </clipPath>
    </defs>
    <g transform="matrix(1.25,0,0,-1.25,-8601.9012,9121.1624)" id="g2602">
      <g transform="matrix(0.375,0,0,0.375,4301.4506,4557.5812)" id="g2734">
        <g id="g2726">
          <g transform="translate(6998.0969,7259.1135)" id="g2604">
            <path
              d="M 0,0 L 0,-159.939 L 0,-180 L 32,-164.939 L 32,15.633 L 0,0 z"
              id="path2606"
              fill="#f8931e"
            />
          </g>
          <g transform="translate(7108.9192,7206.3137)" id="g2608">
            <path d="M 0,0 L 4.417,-45.864 L -57.466,-32.4" id="path2610" fill="#b3b3b3" />
          </g>
          <g transform="translate(6934.0969,7147.6213)" id="g2620">
            <path
              d="M 0,0 C 0,22.674 24.707,41.769 58.383,47.598 L 58.383,67.923 C 6.873,61.697 -32,33.656 -32,0 C -32,-34.869 9.725,-63.709 64,-68.508 L 64,-48.447 C 27.484,-43.869 0,-23.919 0,0 M 101.617,67.915 L 101.617,47.598 C 115.016,45.279 127.002,40.871 136.568,34.958 L 159.195,48.942 C 143.775,58.473 123.873,65.225 101.617,67.915"
              id="path2622"
              fill="#b3b3b3"
            />
          </g>
        </g>
      </g>
    </g>
  </svg>
);

/**
 * Button used for OIDC sign up and login.
 * Note: one-off styling is included to match the OIDC SSO button since we are limited in how we can style it.
 */
export const OidcSSOButton: React.FC<ButtonProps> = ({ className, service, onClick }) => {
  return (
    <Button
      iconOptions={{ customIcon: service === 'Google' ? googleLogo : oidLogo }}
      iconPosition="start"
      theme="evolved-green"
      onClick={onClick}
      label={`Continue with ${service ? service : 'OpenID'}`}
      kind="outline"
      className="w-full md:w-fit"
    />
  );
};

export default OidcSSOButton;
