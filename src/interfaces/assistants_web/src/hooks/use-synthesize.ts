import { useEffect, useState } from 'react';

import { useCohereClient } from '@/cohere-client';
import { useNotify } from '@/hooks/use-toast';
import { useConversationStore } from '@/stores';

export const useSynthesize = () => {
  const client = useCohereClient();
  const notify = useNotify();

  const [isStreamStarting, setIsStreamStarting] = useState<boolean>(false);
  const [audios, setAudios] = useState<Map<string, HTMLAudioElement>>(new Map());

  const {
    conversation: { id: conversationId },
  } = useConversationStore();

  useEffect(() => {
    for (const messageId of audios.keys()) {
      stopSynthesis(messageId);
    }
  }, [conversationId]);

  const isPlaying = (messageId: string) => {
    const audio = audios.get(messageId);

    if (!audio) {
      return false;
    }

    return !audio.paused && !audio.ended;
  };

  const handleToggleSynthesis = async (messageId: string) => {
    return isPlaying(messageId) ? stopSynthesis(messageId) : await startSynthesis(messageId);
  };

  const startSynthesis = async (messageId: string) => {
    if (isStreamStarting) {
      return;
    }

    for (const messageId of audios.keys()) {
      stopSynthesis(messageId);
    }

    const audio = audios.get(messageId);

    if (audio) {
      await audio.play();
      setAudios((prev) => new Map(prev));
      return;
    }

    try {
      setIsStreamStarting(true);

      const stream = await client.synthesizeMessage(conversationId!, messageId);

      if (!stream.ok) {
        notifySynthesisError();
        return;
      }

      const mediaSource = createMediaSource(stream);
      const audio = createAudioElement(mediaSource);

      await audio.play();

      setAudios((prev) => new Map(prev).set(messageId, audio));
    } catch (e) {
      notifySynthesisError(e);
    } finally {
      setIsStreamStarting(false);
    }
  };

  const stopSynthesis = (messageId: string) => {
    const audio = audios.get(messageId);

    if (audio) {
      audio.pause();
      audio.currentTime = 0;
      setAudios((prev) => new Map(prev));
    }
  };

  const createMediaSource = (stream: Response) => {
    const mediaSource = new MediaSource();

    mediaSource.addEventListener('sourceopen', async () => {
      const sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
      const reader = stream.body!.getReader();

      const readChunk = async () => {
        const { done, value } = await reader!.read();

        if (done) {
          mediaSource.endOfStream();
          return;
        }

        sourceBuffer.appendBuffer(value);

        sourceBuffer.addEventListener('updateend', readChunk, { once: true });
      };

      await readChunk();
    });

    return mediaSource;
  };

  const createAudioElement = (mediaSource: MediaSource) => {
    const audio = new Audio();

    audio.src = URL.createObjectURL(mediaSource);

    audio.addEventListener('ended', () => {
      setAudios((prev) => new Map(prev));
    });

    return audio;
  };

  const notifySynthesisError = (e?: unknown) => {
    notify.error('Failed to synthesize the message');
    if (e) {
      console.error(e);
    }
  };

  return { isPlaying, handleToggleSynthesis };
};
