import React from 'react';

type Props = {
  children?: React.ReactNode;
  label: string;
};

export const AccessibleIcon: React.FC<Props> = ({ children, label }) => {
  const child = React.Children.only(children);
  return (
    <>
      {React.cloneElement(child as React.ReactElement, {
        'aria-hidden': 'true',
        focusable: 'false', // See: https://allyjs.io/tutorials/focusing-in-svg.html#making-svg-elements-focusable
      })}
      <span className="sr-only">{label}</span>
    </>
  );
};
