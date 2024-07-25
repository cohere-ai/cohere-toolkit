'use client';

import React, { MouseEvent, useRef } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import bash from 'react-syntax-highlighter/dist/cjs/languages/hljs/bash';
import go from 'react-syntax-highlighter/dist/cjs/languages/hljs/go';
import javascript from 'react-syntax-highlighter/dist/cjs/languages/hljs/javascript';
import python from 'react-syntax-highlighter/dist/cjs/languages/hljs/python';
import xml from 'react-syntax-highlighter/dist/cjs/languages/hljs/xml';

import { CopyToClipboardButton } from '..';
import natureTheme from './theme';

type CopyToClipboardRef = React.ElementRef<typeof CopyToClipboardButton>;

type Props = {
  lang: 'python' | 'go' | 'curl' | 'cli' | 'bash' | 'shell' | 'js' | 'html';
  codeSnippet: string;
  customStyle?: React.CSSProperties;
  onCopy?: VoidFunction;
  preview?: boolean;
};

type SupportedSyntaxHighlighterLanguages = 'python' | 'javascript' | 'go' | 'bash' | 'html';
// supported languages are explicitly registered with the syntax highlighter library to reduce the bundle size
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('go', go);
SyntaxHighlighter.registerLanguage('bash', bash);
SyntaxHighlighter.registerLanguage('html', xml);

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
    case 'html':
      return 'html';
    case 'curl':
    case 'cli':
    case 'shell':
    default:
      return 'bash';
  }
};

export const CodeSnippet: React.FC<Props> = ({
  lang,
  codeSnippet,
  onCopy,
  preview = false,
  customStyle,
}) => {
  const copyBtnRef = useRef<CopyToClipboardRef>(null);

  const handleCodeSnippetClick = (e: MouseEvent<HTMLElement>) => {
    copyBtnRef.current?.triggerCopy(e);
    onCopy?.();
  };

  return (
    <div
      className="group relative h-full w-full cursor-pointer rounded-lg bg-mushroom-900"
      onClick={handleCodeSnippetClick}
    >
      <CopyToClipboardButton
        ref={copyBtnRef}
        value={codeSnippet}
        size="md"
        animate={false}
        kind="secondary"
        className="absolute right-3 top-3 rounded-lg bg-mushroom-800 px-2 py-1 group-hover:bg-mushroom-800"
      />
      <SyntaxHighlighter
        showLineNumbers
        language={mapLangToSyntaxHighlighterLang(lang)}
        style={natureTheme}
        customStyle={{
          paddingRight: '60px',
          fontSize: `${preview ? '12px' : '16px'}`,
          ...customStyle,
        }}
      >
        {codeSnippet}
      </SyntaxHighlighter>
    </div>
  );
};
