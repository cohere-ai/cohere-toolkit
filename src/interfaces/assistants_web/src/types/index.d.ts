type Nullable<T> = T | null;

declare module 'js-resume-parser' {
  export function getDataFromPDF(file: File): Promise<{ text: string }>;
  export function getDataFromDocx(file: File): Promise<{ text: string }>;
}

// from https://github.com/compulim/react-scroll-to-bottom/issues/81 with additions
declare module 'react-scroll-to-bottom' {
  import * as React from 'react';

  interface ReactScrollToBottomProps {
    checkInterval?: number;
    className?: string;
    debounce?: number;
    followButtonClassName?: string;
    mode?: string;
    scrollViewClassName?: string;
    children: React.ReactNode;
    debug?: boolean;
    initialScrollBehavior?: 'smooth' | 'auto';
  }

  interface ScrollOptions {
    behavior: ScrollBehavior;
  }

  interface FunctionContextProps {
    scrollTo: (scrollTo: number, options: ScrollOptions) => void;
    scrollToBottom: (options: ScrollOptions) => void;
    scrollToEnd: (options: ScrollOptions) => void;
    scrollToStart: (options: ScrollOptions) => void;
    scrollToTop: (options: ScrollOptions) => void;
  }

  export const useScrollToBottom: () => FunctionContextProps.scrollToBottom;
  export const useAtTop: () => [boolean];
  export const useSticky: () => [boolean];

  const FunctionContext: React.Context<FunctionContextProps>;

  export default class ScrollToBottom extends React.PureComponent<ReactScrollToBottomProps> {}
}
