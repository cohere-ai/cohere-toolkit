import { useRouter } from 'next/router';
import React from 'react';

import { Dot } from '@/components/Dot';
import { BasicButton, Text } from '@/components/Shared';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { useIsGroundingOn } from '@/hooks/grounding';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  className?: string;
};

/**
 * @description renders the button that opens the configuration drawer.
 */
export const ConfigurationDrawerButton: React.FC<Props> = ({ className = '' }) => {
  const router = useRouter();
  const { welcomeGuideState, progressWelcomeGuideStep, finishWelcomeGuide } =
    useWelcomeGuideState();
  const { setSettings } = useSettingsStore();
  const isGroundingOn = useIsGroundingOn();

  const handleGroundingClick = () => {
    setSettings({ isConfigDrawerOpen: true });

    if (welcomeGuideState === WelcomeGuideStep.ONE && router.pathname === '/') {
      progressWelcomeGuideStep();
    } else if (welcomeGuideState !== WelcomeGuideStep.DONE) {
      finishWelcomeGuide();
    }
  };

  return (
    <div className={cn('relative', className)}>
      <BasicButton
        label={<Text styleAs="overline">Tools</Text>}
        kind="tertiary"
        size="sm"
        dataTestId="button-grounding-drawer"
        startIcon={<Dot on={isGroundingOn} />}
        onClick={handleGroundingClick}
      />
      <WelcomeGuideTooltip
        step={1}
        className={cn('right-0 top-full mt-9', {
          'delay-1000': !welcomeGuideState || welcomeGuideState === WelcomeGuideStep.ONE,
        })}
      />
    </div>
  );
};
