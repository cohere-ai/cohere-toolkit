import { useState } from 'react';

/**
 *
 * A hook used to track steps in a type-safe way.
 *
 * @param numberOfSteps The number of steps to track
 * @param onComplete A callback to be called when the last step is reached
 * @returns An object containing the current step and a function to set the current step
 *
 * @example
 * const { step, setStep } = useSteps(3, () => console.info('done'));
 * setStep(1); // step is now 1
 * setStep(2); // step is now 2
 * setStep(3); // step is now 3 and 'done' is logged to the console
 *
 * Note: It's best used with numeric enums
 *
 * @example
 * enum Steps {
 *  Step1,
 *  Step2,
 *  Step3,
 * }
 * const { step, setStep } = useSteps<Steps>(Steps.Step3, () => console.info('done'));
 */
export const useSteps = <T extends number>(numberOfSteps: number, onComplete: VoidFunction) => {
  const [step, _setStep] = useState(0);

  const setStep = (step: T) => {
    if (step > numberOfSteps) return;
    _setStep(step);
    if (step === numberOfSteps) {
      onComplete();
    }
  };

  return {
    step: step as T,
    setStep,
  };
};
