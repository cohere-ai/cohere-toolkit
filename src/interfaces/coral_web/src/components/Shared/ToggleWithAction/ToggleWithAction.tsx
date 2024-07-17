'use client';

import { useEffect, useState } from 'react';

type Props = {
  onClick?: VoidFunction;
  duration?: number;
  originalComponent: React.ReactNode;
  alternateComponent: React.ReactNode;
};

/**
 * A component that toggles between two components when clicked.
 * @param onClick - A function to be called when the component is clicked.
 * @param duration - The duration in milliseconds to show the alternate component.
 * @param originalComponent - The component to show when the component is not clicked.
 * @param alternateComponent - The component to show when the component is clicked.
 */
export const ToggleWithAction: React.FC<Props> = ({
  onClick,
  duration,
  originalComponent,
  alternateComponent,
}) => {
  const [showAlternateComponent, setShowAlternateComponent] = useState(false);

  useEffect(() => {
    if (showAlternateComponent) {
      const timeoutId = setTimeout(() => {
        setShowAlternateComponent(false);
      }, duration ?? 2000);
      return () => clearTimeout(timeoutId);
    }
  }, [showAlternateComponent]);

  const handleClick = () => {
    onClick?.();
    setShowAlternateComponent(!showAlternateComponent);
  };

  return (
    <button onClick={handleClick} type="button" className="flex">
      {showAlternateComponent ? alternateComponent : originalComponent}
    </button>
  );
};
