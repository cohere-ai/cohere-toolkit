import React, { MouseEvent, useRef } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import bash from 'react-syntax-highlighter/dist/cjs/languages/hljs/bash';
import go from 'react-syntax-highlighter/dist/cjs/languages/hljs/go';
import javascript from 'react-syntax-highlighter/dist/cjs/languages/hljs/javascript';
import python from 'react-syntax-highlighter/dist/cjs/languages/hljs/python';

import { CopyToClipboardButton } from '..';
import natureTheme from './theme';

type CopyToClipboardRef = React.ElementRef<typeof CopyToClipboardButton>;

type Props = {
  lang: 'python' | 'go' | 'curl' | 'cli' | 'bash' | 'shell' | 'js';
  codeSnippet: string;
  onCopy?: VoidFunction;
  preview?: boolean;
};

type SupportedSyntaxHighlighterLanguages = 'python' | 'javascript' | 'go' | 'bash';
// supported languages are explicitly registered with the syntax highlighter library to reduce the bundle size
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('go', go);
SyntaxHighlighter.registerLanguage('bash', bash);

const mapLangToSyntaxHighlighterLang = (lang: string): SupportedSyntaxHighlighterLanguages => {
  switch (lang) {
    case 'python':
      return 'python';
    case 'node':
    case 'js':
    case 'javascript':
      return 'javascript';
    case 'go':
      return 'go';
    case 'curl':
    case 'cli':
    case 'shell':
    default:
      return 'bash';
  }
};

export const CodeSnippet: React.FC<Props> = ({ lang, codeSnippet, onCopy, preview = false }) => {
  const copyBtnRef = useRef<CopyToClipboardRef>(null);

  const handleCodeSnippetClick = (e: MouseEvent<HTMLElement>) => {
    copyBtnRef.current?.triggerCopy(e);
    onCopy?.();
  };

  return (
    <div
      className="group relative h-full w-full cursor-pointer rounded-lg"
      onClick={handleCodeSnippetClick}
    >
      <CopyToClipboardButton
        ref={copyBtnRef}
        value={codeSnippet}
        size="md"
        animate={false}
        kind="secondary"
        className="absolute right-3 top-3 rounded-lg bg-green-200 px-2 py-1 group-hover:bg-green-300"
      />
      <SyntaxHighlighter
        showLineNumbers
        language={mapLangToSyntaxHighlighterLang(lang)}
        style={natureTheme}
        customStyle={{
          height: '100%',
          paddingRight: '60px',
          fontSize: `${preview ? '12px' : '16px'}`,
        }}
      >
        {codeSnippet}
      </SyntaxHighlighter>
    </div>
  );
};
