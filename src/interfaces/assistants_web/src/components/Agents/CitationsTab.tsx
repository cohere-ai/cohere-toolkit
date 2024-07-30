import { useResizeObserver } from '@react-hookz/web';
import { useRef } from 'react';

import { CitationPanel } from '@/components/Citations/CitationPanel';
import { useCalculateCitationStyles } from '@/hooks/citations';
import { useConversationStore } from '@/stores';
import { useStreamingStore } from '@/stores/streaming';

type Props = {};

export const CitationsTab: React.FC<Props> = () => {
  const ref = useRef<HTMLDivElement>(null);
  const {
    conversation: { messages },
  } = useConversationStore();
  const { streamingMessage } = useStreamingStore();

  const { citationToStyles } = useCalculateCitationStyles(messages, streamingMessage);

  useResizeObserver(document.getElementById('messages-container'), (event) => {
    // update aside hight and scroll when messages container height changes
    if (ref.current) {
      ref.current.style.height = `${event.contentRect.height}px`;
      ref.current.scrollIntoView({ behavior: 'smooth' });
    }
  });

  return (
    <aside className="flex max-h-full overflow-y-auto">
      <div className="flex-grow" ref={ref}>
        <CitationPanel citationToStyles={citationToStyles} streamingMessage={streamingMessage} />
      </div>
    </aside>
  );
};
