import { useEffect, useState } from 'react';

import { useCohereClient } from '@/cohere-client';
import { useConversationStore } from '@/stores';

export enum SynthesisStatus {
  NotStarted = 'not-started',
  Loading = 'loading',
  Playing = 'playing',
  Ended = 'ended',
}

export const useSynthesizer = () => {
  const client = useCohereClient();

  const [audios, setAudios] = useState<Map<string, HTMLAudioElement>>(new Map());

  const {
    conversation: { id: conversationId },
  } = useConversationStore();

  useEffect(() => {
    stopPlayingSyntheses();
  }, [conversationId]);

  const synthesisStatus = (messageId: string) => {
    const audio = audios.get(messageId);

    if (!audio) {
      return SynthesisStatus.NotStarted;
    }

    if (!audio.src) {
      return SynthesisStatus.Loading;
    }

    if (!audio.paused && !audio.ended) {
      return SynthesisStatus.Playing;
    }

    return SynthesisStatus.Ended;
  };

  const toggleSynthesis = async (messageId: string) => {
    if (synthesisStatus(messageId) == SynthesisStatus.Playing) {
      stopSynthesis(messageId);
    } else {
      await startSynthesis(messageId);
    }
  };

  const startSynthesis = async (messageId: string) => {
    stopPlayingSyntheses();

    let audio = audios.get(messageId);

    if (audio && !audio.src) {
      return;
    }

    if (!audio) {
      audio = createEmptyAudioElement();
      setAudios((prev) => new Map(prev).set(messageId, audio!));
    }

    if (!audio.src) {
      const blob = await client.synthesizeMessage(conversationId!, messageId);
      audio.src = URL.createObjectURL(blob);
    }

    await audio.play();

    setAudios((prev) => new Map(prev));
  };

  const createEmptyAudioElement = () => {
    const audio = new Audio();

    audio.addEventListener('ended', () => {
      setAudios((prev) => new Map(prev));
    });

    return audio;
  };

  const stopSynthesis = (messageId: string) => {
    const audio = audios.get(messageId);

    if (!audio) {
      return;
    }

    audio.pause();
    audio.currentTime = 0;

    setAudios((prev) => new Map(prev));
  };

  const stopPlayingSyntheses = () => {
    for (const messageId of audios.keys()) {
      if (synthesisStatus(messageId) == SynthesisStatus.Playing) {
        stopSynthesis(messageId);
      }
    }
  }

  return { synthesisStatus, toggleSynthesis };
};
