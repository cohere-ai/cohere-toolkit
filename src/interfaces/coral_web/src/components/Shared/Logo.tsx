import cx from 'classnames';

interface LogoProps {
  includeBrandName?: boolean;
  hasCustomLogo?: boolean;
  style?: 'default' | 'grayscale' | 'coral';
  className?: string;
  darkModeEnabled?: boolean;
}

export const Logo: React.FC<LogoProps> = ({
  includeBrandName = true,
  hasCustomLogo,
  className,
  style = 'default',
  darkModeEnabled,
}) => {
  // if (hasCustomLogo) {
    // Modify this section to render a custom logo or text based on specific design guidelines.

  // const customLogoStyle = {
  //   height: '24px',
  //   width: 'auto'
  // }
  // return <img style={customLogoStyle} src="/images/logo.png" alt="Logo" className={cx('h-full', className)} />;
  // }

  const customLogoStyle = {
     height: '24px',
     width: 'auto'
  }

  return <img style={customLogoStyle} src="/images/logo.png" alt="Logo" className={cx('h-full', className)} />;

};
