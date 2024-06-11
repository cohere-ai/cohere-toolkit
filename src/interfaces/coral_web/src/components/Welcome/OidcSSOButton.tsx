import { BasicButton } from '@/components/Shared';
import { cn } from '@/utils';

type ButtonProps = {
  onClick: () => void;
  className?: string;
};

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
            <path d="M 0,0 L 0,-159.939 L 0,-180 L 32,-164.939 L 32,15.633 L 0,0 z" id="path2606" fill="#f8931e" />
          </g>
          <g transform="translate(7108.9192,7206.3137)" id="g2608">
            <path d="M 0,0 L 4.417,-45.864 L -57.466,-32.4" id="path2610" fill="#b3b3b3"/>
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
export const OidcSSOButton: React.FC<ButtonProps> = ({ className, onClick }) => {
  return (
    <BasicButton
      startIcon={oidLogo}
      onClick={onClick}
      label="Continue with OpenID"
      size="sm"
      kind="secondary"
      className={cn(
        // align with the max-width of the OIDC SSO button, which is 400px
        'h-10 !max-w-[400px] !rounded border-[#dadce0] bg-[#ffffff]',
        className
      )}
    />
  );
};

export default OidcSSOButton;
