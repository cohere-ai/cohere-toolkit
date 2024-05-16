import { Transition } from '@headlessui/react';
import { PropsWithChildren } from 'react';

import { CitationTextHighlighter } from '@/components/Citations/CitationTextHighlighter';
import { DataTable } from '@/components/DataTable';
import { MarkdownImage } from '@/components/MarkdownImage';
import { Icon } from '@/components/Shared';
import { Markdown, Text } from '@/components/Shared';
import { UploadedFile } from '@/components/UploadedFile';
import {
  type ChatMessage,
  MessageType,
  isAbortedMessage,
  isErroredMessage,
  isFulfilledMessage,
  isFulfilledOrTypingMessage,
  isLoadingMessage,
} from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isLast: boolean;
  message: ChatMessage;
  onRetry?: VoidFunction;
};

const BOT_ERROR_MESSAGE = 'Unable to generate a response since an error was encountered. ';

function addOnErrorToImg(html: string) {
  //add an onError=getImage(this) to all img elements in the html string
  //this is a hacky way to do it but it works
  const regex = /<img([\s\S]+?)>/g;
  const imgElements = html.match(regex);
  if (imgElements) {
    for (let i = 0; i < imgElements.length; i++) {
      const imgElement = imgElements[i];
      const newImgElement = imgElement.replace('>', ' onError="getImage(this)">');
      html = html.replace(imgElement, newImgElement);
    }
  }
  html = html + GET_IMAGE_DEF;
  return html;
}
const GET_IMAGE_DEF = `
<script>
function getImage(element) {
  console.log(element.alt);
  console.log(element);

  return fetch(
    'https://api.pexels.com/v1/search?query=' + element.alt + '&per_page=1&total_results=1',
    {
      method: 'GET',
      headers: {
        Authorization: 'JMr4ZI1Ap8UmPwuPbFBjjNzvnzD3urK7l8EQTpHa66PdDhOOfebAe426',
      },
      // We are not sending any data in the request, so we use null as the body.
    }
  )
    .then((response) => response.json())
    .then((data) => {
      element.src = data['photos'][0]['src']['original'];
      this.src = data['photos'][0]['src']['original'];
    });
}
</script>
`;

const replaceCodeBlockWithIframe = (content: string) => {
  const regex = /```html([\s\S]+)(```)/;

  const match = content.match(regex);

  if (!match) {
    return content;
  }

  console.log(match[1]);

  const blob = new Blob([match[1]], { type: 'text/html' });
  const src = URL.createObjectURL(blob);
  const iframe = `<iframe data-src="${src}"></iframe>`;

  content = content.replace(regex, iframe);
  //content = addOnErrorToImg(content);

  return content;
};

export const MessageContent: React.FC<Props> = ({ isLast, message, onRetry }) => {
  const isUser = message.type === MessageType.USER;
  const isLoading = isLoadingMessage(message);
  const isBotError = isErroredMessage(message);
  const isUserError = isUser && message.error;
  const isAborted = isAbortedMessage(message);
  const isTypingOrFulfilledMessage = isFulfilledOrTypingMessage(message);

  let content: React.ReactNode = null;

  if (isUserError) {
    content = (
      <>
        <Text>{message.text}</Text>
        <MessageInfo type="error">
          {message.error}
          {isLast && (
            <button className="underline underline-offset-1" type="button" onClick={onRetry}>
              Retry?
            </button>
          )}
        </MessageInfo>
      </>
    );
  } else if (isUser) {
    content = (
      <>
        <Markdown text={message.text} />
        {message.files && message.files.length > 0 && (
          <div className="flex flex-wrap py-2 gap-2">
            {message.files.map((file) => (
              <UploadedFile key={file.id} file={file} />
            ))}
          </div>
        )}
      </>
    );
  } else if (isLoading) {
    const hasLoadingMessage = message.text.length > 0;
    content = (
      <Text className={cn('flex min-w-0 text-volcanic-700')} as="span">
        {hasLoadingMessage && (
          <Transition
            appear={true}
            show={true}
            enterFrom="opacity-0"
            enterTo="opacity-full"
            enter="transition-opacity ease-in-out duration-500"
          >
            {message.text}
          </Transition>
        )}
        {!hasLoadingMessage && (
          <span className="w-max">
            <div className="pr-1 overflow-hidden animate-typing-ellipsis whitespace-nowrap">
              ...
            </div>
          </span>
        )}
      </Text>
    );
  } else if (isBotError) {
    content = (
      <>
        {message.text.length > 0 ? (
          <Markdown text={message.text} />
        ) : (
          <Text className={cn('text-volcanic-700')}>{BOT_ERROR_MESSAGE}</Text>
        )}
        <MessageInfo type="error">{message.error}</MessageInfo>
      </>
    );
  } else {
    const hasCitations =
      isTypingOrFulfilledMessage && message.citations && message.citations.length > 0;
    // replace the code block with an iframe
    const md = replaceCodeBlockWithIframe(message.originalText);
    content = (
      <>
        <Markdown
          className={cn({
            'text-volcanic-700': isAborted,
          })}
          text={md}
          customComponents={{
            img: MarkdownImage as any,
            cite: CitationTextHighlighter as any,
            table: DataTable as any,
          }}
          renderLaTex={!hasCitations}
        />
        {isAborted && (
          <MessageInfo>
            This generation was stopped.{' '}
            {isLast && isAborted && (
              <button className="underline underline-offset-1" type="button" onClick={onRetry}>
                Retry?
              </button>
            )}
          </MessageInfo>
        )}
      </>
    );
  }

  return (
    <div className="flex flex-col justify-center w-full py-1 gap-y-1">
      <Text
        as="div"
        className="flex flex-col gap-y-1 whitespace-pre-wrap [overflow-wrap:anywhere] md:max-w-4xl"
      >
        {content}
      </Text>
    </div>
  );
};

const MessageInfo = ({
  type = 'default',
  children,
}: PropsWithChildren & { type?: 'default' | 'error' }) => (
  <div
    className={cn('flex items-start gap-1', {
      'text-volcanic-700': type === 'default',
      'text-danger-500': type === 'error',
    })}
  >
    <Icon name="warning" size="md" className="flex items-center text-p" />
    <Text as="span">{children}</Text>
  </div>
);
