'use client';

import { GuideTooltip } from '@/components/GuideTooltip';
import { STRINGS } from '@/constants/strings';
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
      title: STRINGS.welcomeToToolkitTitle,
      description: STRINGS.welcomeToToolkitDescription,
      buttonLabel: STRINGS.next,
      onNext: () => {
        setSettings({ isConfigDrawerOpen: true });
      },
    },
    {
      title: STRINGS.configureYourToolsTitle,
      description: STRINGS.configureYourToolsDescription,
      buttonLabel: STRINGS.next,
      onNext: () => {
        focusComposer();
        setSettings({ isConfigDrawerOpen: false });
      },
    },
    {
      title: STRINGS.uploadDocumentsAsASourcetitle,
      description: STRINGS.uploadDocumentsAsASourceDescription,
      buttonLabel: STRINGS.done,
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
