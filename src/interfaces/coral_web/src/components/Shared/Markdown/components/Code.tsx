import { CodeSnippet } from '@/components/Shared/CodeSnippet';

type Props = {
  children: React.ReactNode;
  language?: string;
};

export const Code: React.FC<Props> = ({ children }) => {
  let code = '';
  for (const child of children as any) {
    if (typeof child === 'string') {
      code += child;
    } else if (typeof child === 'object' && 'props' in child) {
      code += child.props.children;
    }
  }

  return <CodeSnippet lang="python" codeSnippet={code} />;
};
