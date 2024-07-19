import { useEffect, useState } from 'react';

type TypeOptions = {
  typeSpeed?: number;
  charactersPerInterval?: number;
  paragraphDelay?: number;
  enabled?: boolean;
  onParagraphTyped?: (paragraphIndex: number) => void;
};

/**
 * A hook to render text with a typing effect.
 * Each character in a phrase is "typed" at the designated `typeSpeed` and each
 * phrase begins "typing" after the designated `paragraphDelay`.
 * @param texts - the phrases to be typed out
 * @param options.typeSpeed - delay between characters typed in ms
 * @param options.charactersPerInterval - number of chars to be typed at a time
 * @param options.paragraphDelay - delay between paragraphs in ms
 * @param options.enabled - whether or not to start typing
 * @param options.onParagraphTyped - callback when a paragraph is fully typed

 */
export const useTyped = (
  texts: string[],
  {
    typeSpeed = 5,
    charactersPerInterval = 1,
    paragraphDelay = 1000,
    enabled = true,
    onParagraphTyped,
  }: TypeOptions
) => {
  const [typed, setTyped] = useState('');
  const [isTyping, setIsTyping] = useState<boolean>();
  const [isFinished, setIsFinished] = useState(false);
  const [timer, setTimer] = useState<NodeJS.Timeout>();

  // reset state when texts change
  useEffect(() => {
    setTyped('');
    setIsTyping(false);
    setIsFinished(false);
    clearTimeout(timer);
    setTimer(undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [texts]);

  useEffect(() => {
    if (!enabled) return;
    if (isFinished) return;

    setIsTyping(true);

    let fullyTyped = '';
    let phraseIndex = 0;
    let charIndex = 0;
    setTimer(
      setTimeout(function type() {
        fullyTyped += texts[phraseIndex].slice(charIndex, charIndex + charactersPerInterval);
        setTyped(fullyTyped);
        charIndex += charactersPerInterval;

        if (charIndex >= texts[phraseIndex].length) {
          charIndex = 0;
          phraseIndex += 1;
          onParagraphTyped?.(phraseIndex);

          if (phraseIndex === texts.length) {
            setIsTyping(false);
            setIsFinished(true);
            clearTimeout(timer);
          } else {
            setTimer(setTimeout(type, paragraphDelay));
          }
        } else {
          setTimer(setTimeout(type, typeSpeed));
        }
      }, 0)
    );

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    texts,
    typeSpeed,
    isTyping,
    paragraphDelay,
    charactersPerInterval,
    enabled,
    isFinished,
    onParagraphTyped,
  ]);

  return { typed, isTyping };
};
