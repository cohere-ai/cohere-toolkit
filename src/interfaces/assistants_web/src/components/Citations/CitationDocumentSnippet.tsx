'use client';

import { Fragment, useContext, useMemo } from 'react';

import { Document } from '@/cohere-client';
import { CitationDocumentHeader } from '@/components/Citations/CitationDocumentHeader';
import { B64Image } from '@/components/MarkdownImage';
import { Markdown, Text } from '@/components/Shared';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { ModalContext } from '@/context/ModalContext';
import { cn } from '@/utils';
import { PythonInterpreterOutputFile, parsePythonInterpreterToolFields } from '@/utils/tools';

type Props = {
  document: Document;
  keyword: string;
  isExpandable?: boolean;
};

/**
 * @descroption Segments the snippet by the text before the found keyword and the in-context
 * keyword itself to allow for styling of the in-context keyword.
 *
 * E.g. if the snippet is "This is a snippet. Snippets are great." and the keyword is "snippet",
 * the result will be:
 * [
 *   {beforeKeyword: "This is a ", snippetKeyword: "snippet"},
 *   {beforeKeyword: ". ", snippetKeyword: "Snippet"},
 *   {beforeKeyword: "s are great."}
 * ]
 */

const getSnippetSegments = (snippet: string | undefined, keyword: string) => {
  if (!snippet) return null;
  const normalizedSnippet = snippet.toLowerCase();
  const normalizedKeyword = keyword.toLowerCase();

  if (!!normalizedKeyword && normalizedSnippet.includes(normalizedKeyword)) {
    const sections = normalizedSnippet.split(normalizedKeyword);
    let currentIndex = 0;

    const sectionsAndKeyword = sections.reduce<{ beforeKeyword: string; snippetKeyword: string }[]>(
      (acc, section) => {
        const newIndices = [
          ...acc,
          {
            beforeKeyword: snippet.slice(currentIndex, currentIndex + section.length),
            snippetKeyword: snippet.slice(
              currentIndex + section.length,
              currentIndex + section.length + keyword.length
            ),
          },
        ];
        currentIndex += section.length + keyword.length;
        return newIndices;
      },
      []
    );

    return sectionsAndKeyword;
  } else {
    return [{ beforeKeyword: snippet, snippetKeyword: undefined }];
  }
};

/**
 * @description Renders the body of the citation document. It will either render
 * the snippet provided or the fields provided by the tool.
 */
export const CitationDocumentSnippet: React.FC<
  Props & { toolId?: string; onToggle: VoidFunction }
> = ({ toolId, document, keyword, onToggle }) => {
  const { open } = useContext(ModalContext);

  const openFullSnippetModal = () => {
    open({
      title: '',
      content: (
        <div className="flex flex-col gap-y-3">
          <CitationDocumentHeader
            toolId={toolId}
            url={document.url ?? ''}
            title={document.title && document.title.length > 0 ? document.title : undefined}
            isExpandable={false}
            isExpanded={true}
            isSelected={true}
            onToggleSnippet={onToggle}
          />
          <Snippet snippet={document.text} keyword={keyword} />
        </div>
      ),
      kind: 'coral',
    });
  };

  if (toolId === TOOL_PYTHON_INTERPRETER_ID && document.fields) {
    const {
      success,
      stdErr = '',
      stdOut = '',
      codeRuntime,
      outputFile,
      error,
    } = parsePythonInterpreterToolFields(document);

    return (
      <div className="flex flex-col gap-y-1">
        {success !== undefined && (stdErr.length > 0 || stdOut.length > 0) && (
          <ConsoleOutput type={success ? 'Output' : 'Error'} message={success ? stdOut : stdErr} />
        )}
        {success !== undefined && !success && error && (
          <ConsoleOutput type={error.type} message={error.message} />
        )}
        {codeRuntime && <CodeExecutionTime runtime={codeRuntime} />}
        {outputFile && <OutputFiles outputFile={outputFile} />}
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <Snippet
        snippet={document.text}
        keyword={keyword}
        beforeKeywordCharLimit={30}
        lineLimitClass="line-clamp-3"
      />

      <button
        className="self-end p-0 text-coral-200 transition-colors ease-in-out hover:text-coral-400"
        onClick={openFullSnippetModal}
        data-testid="button-see-full-snippet"
      >
        <Text as="span" styleAs="caption">
          See more
        </Text>
      </button>
    </div>
  );
};

const Snippet: React.FC<{
  keyword: string;
  snippet: string | undefined;
  beforeKeywordCharLimit?: number;
  lineLimitClass?: string;
}> = ({ snippet, keyword, beforeKeywordCharLimit, lineLimitClass }) => {
  const snippetSections = useMemo(() => getSnippetSegments(snippet, keyword), [snippet, keyword]);
  if (!snippetSections) return null;

  return (
    <Text className={cn('content text-coral-200', lineLimitClass)}>
      {snippetSections.map(({ beforeKeyword, snippetKeyword }, i) => {
        return (
          <Fragment key={i}>
            {i === 0 &&
            beforeKeywordCharLimit !== undefined &&
            beforeKeyword.length > beforeKeywordCharLimit &&
            snippetKeyword
              ? `...${beforeKeyword.slice(-1 * beforeKeywordCharLimit)}`
              : beforeKeyword}
            {snippetKeyword ? <span className="font-medium">{snippetKeyword}</span> : null}
          </Fragment>
        );
      })}
    </Text>
  );
};

const ConsoleOutput: React.FC<{ type: string; message: string }> = ({ type, message }) => {
  return (
    <>
      <Text as="span" styleAs="code-sm" className="text-coral-200">
        {type}
      </Text>
      <Markdown text={'```python\n' + message + '\n```'} />
    </>
  );
};

const CodeExecutionTime: React.FC<{ runtime: string }> = ({ runtime }) => {
  return (
    <Text as="span" styleAs="code-sm" className="mt-2 text-coral-200">
      Execution time: {runtime}ms
    </Text>
  );
};

const OutputFiles: React.FC<{ outputFile: PythonInterpreterOutputFile }> = ({ outputFile }) => {
  return (
    <div className="flex flex-col gap-y-3">
      <B64Image caption={outputFile.filename} data={outputFile.b64_data ?? ''} />
    </div>
  );
};
