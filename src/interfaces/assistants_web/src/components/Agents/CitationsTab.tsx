import { useEventListener, useResizeObserver } from '@react-hookz/web';
import { useEffect, useRef } from 'react';

import { CitationPanel } from '@/components/Citations/CitationPanel';
import { MESSAGES_CONTAINER_ID, ReservedClasses } from '@/constants';
import { cn } from '@/utils';

type Props = {};

export const CitationsTab: React.FC<Props> = () => {
  const ref = useRef<HTMLDivElement>(null);

  // Update citation panel height when messages container height changes
  useResizeObserver(
    document.getElementById(MESSAGES_CONTAINER_ID),
    (event) => {
      if (ref.current) {
        ref.current.style.height = `${event.target.clientHeight}px`;
      }
    },
    Boolean(document.getElementById(MESSAGES_CONTAINER_ID))
  );

  // Sync citation panel scroll position with messages container
  useEventListener(
    document.querySelector(`.${ReservedClasses.MESSAGES_SCROLL_VIEW}`),
    'scroll',
    (event: Event & { target: HTMLElement }) => {
      document
        ?.querySelector(`.${ReservedClasses.CITATION_PANEL}`)
        ?.scroll({ behavior: 'smooth', top: event.target.scrollTop });
    }
  );

  // Set initial citation panel height
  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = `${
        document.getElementById(MESSAGES_CONTAINER_ID)?.clientHeight
      }px`;
    }
  }, []);

  return (
    <aside className={cn('flex max-h-full overflow-y-auto pb-12', ReservedClasses.CITATION_PANEL)}>
      <div className="h-auto flex-grow" ref={ref}>
        <CitationPanel />
      </div>
    </aside>
  );
};
