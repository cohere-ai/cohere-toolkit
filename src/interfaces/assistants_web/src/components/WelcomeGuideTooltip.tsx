'use client';

import { GuideTooltip } from '@/components/GuideTooltip';
import { useFocusComposer } from '@/hooks/actions';
import { useShowWelcomeGuide, useWelcomeGuideState } from '@/hooks/ftux';
import { useSettingsStore } from '@/stores';

type Props = {
  step: number;
  className?: string;
};

/**
 * @description Renders the welcome guide tooltips depending on the given step.
 */
export const WelcomeGuideTooltip: React.FC<Props> = ({ className = '', step }) => {
  const { welcomeGuideState, progressWelcomeGuideStep, finishWelcomeGuide } =
    useWelcomeGuideState();
  const { setSettings } = useSettingsStore();
  const showWelcomeGuide = useShowWelcomeGuide();
  const { focusComposer } = useFocusComposer();

  if (!showWelcomeGuide) return null;

  const TOOLTIP_CONFIGURATIONS = [
    {
      title: 'Welcome to Toolkit',
      description:
        'Say hi to the model! Open this sidebar to select tools and data sources the model should use in this conversation.',
      buttonLabel: 'Next',
      onNext: () => {
        setSettings({ isConfigDrawerOpen: true });
      },
    },
    {
      title: 'Configure your Tools',
      description:
        'Your configured Tools will be listed here, such as a sample PDF retrieval tool. Follow [these steps](link when available) to add your own.',
      buttonLabel: 'Next',
      onNext: () => {
        focusComposer();
        setSettings({ isConfigDrawerOpen: false });
      },
    },
    {
      title: 'Upload Documents as a Source',
      description:
        'Upload a PDF document as a retrieval source. This will use the PDF retrieval tool.',
      buttonLabel: 'Done',
    },
  ];
  const { title, description, buttonLabel, onNext } = TOOLTIP_CONFIGURATIONS[step - 1];

  return (
    <GuideTooltip
      show={welcomeGuideState === String(step)}
      currentStep={step}
      totalSteps={TOOLTIP_CONFIGURATIONS.length}
      title={title}
      description={description}
      buttonLabel={buttonLabel}
      className={className}
      onNext={() => {
        onNext?.();
        progressWelcomeGuideStep();
      }}
      onClose={finishWelcomeGuide}
    />
  );
};
