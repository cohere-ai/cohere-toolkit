import {
  TOOL_CALCULATOR_ID,
  TOOL_CHAT_DEFAULT,
  TOOL_INTERNET_SEARCH_ID,
  TOOL_PYTHON_INTERPRETER_ID,
} from '@/cohere-client';
import { IconName } from '@/components/Shared';
import { useFocusFileInput } from '@/hooks/actions';
import { useParamsStore, useSettingsStore } from '@/stores';

enum StartMode {
  UNGROUNDED = 'ungrounded',
  WEB_SEARCH = 'web_search',
  TOOLS = 'tools',
  DOCUMENTS = 'documents',
}

type Prompt = {
  title: string;
  description: React.ReactNode;
  icon: IconName;
  prompt: string;
};

const UNGROUNDED_PROMPTS: Prompt[] = [
  {
    title: 'English to French',
    description: (
      <>
        Create a business plan for a marketing agency in <span className="font-medium">French</span>
      </>
    ),
    icon: 'globe-stand',
    prompt:
      'Write a business plan outline for an marketing agency in French. Highlight all the section titles, and make it less than 300 words.',
  },
  {
    title: 'Multilingual',
    description: 'Redacta una descripción de empleo Diseñador(a) Web',
    icon: 'globe-stand',
    prompt:
      'Redacta una descripción de empleo para la posición de Diseñador(a) Web. Esta descripción debe incluir un segmento detallando las responsabilidades asociadas al puesto, así como 4 puntos destacando los atributos que valoramos en los aspirantes. La lista de cualidades debe seguir el formato: Nombre del atributo: Descripción.',
  },
  {
    title: 'Code Generation',
    description: 'Help me clean up some data in Python',
    icon: 'code',
    prompt: `I want to figure out how to remove nan values from my array. For example, My array looks something like this:
    
        x = [1400, 1500, 1600, nan, nan, nan ,1700] #Not in this exact configuration
            
        How can I remove the nan values from x to get something like:
            
        x = [1400, 1500, 1600, 1700]
    `,
  },
];

const WEB_SEARCH_PROMPTS: Prompt[] = [
  {
    title: 'Current Events',
    description: 'Gather business insights on the Chinese market',
    icon: 'newspaper',
    prompt:
      'My company specializing in audio equipment manufacturing is thinking about expanding into China. What do we need to know?',
  },
  {
    title: 'Topic Learning',
    description: 'Give me a run down of Productivity AI startups',
    icon: 'book',
    prompt: `I'm interested in learning more about AI startups focused on productivity. Give me a summary of the top 3.`,
  },
  {
    title: 'Research',
    description: 'Get a quick overview of the solar panels market conditions  ',
    icon: 'flask',
    prompt: 'Can you give me an overview of the global solar panels market?',
  },
];

const TOOL_PROMPTS: Prompt[] = [
  {
    title: 'Stay Up To Date',
    description: 'US tech company employee count',
    icon: 'newspaper',
    prompt:
      'Create a plot of the number of full time employees at the 3 tech companies with the highest market cap in the United States in 2024.',
  },
  {
    title: 'Research',
    description: 'Overview of solar panel industry',
    icon: 'flask',
    prompt: 'Plot the top five companies in the solar panel industry by revenue last year.',
  },
  {
    title: 'Learn a Topic',
    description: 'Explain trigonometry',
    icon: 'book',
    prompt: "Plot sin() and explain the math behind this graph to me like I'm five.",
  },
];

const DOCUMENT_PROMPTS: Prompt[] = [
  {
    title: 'Summarize',
    description: 'Help me summarize this document',
    icon: 'list',
    prompt:
      'Help me summarize the document. Format your answer in the form of bullet points. Make sure to use exactly 3 bullets. Each bullet should use between 10 words and 50 words.',
  },
  {
    title: 'Analyze',
    description: 'Tell me the main theme of this document',
    icon: 'book-open-text',
    prompt: `Tell me the main theme of this document. Format your answer in the form of bullets. Don't use your own words, but instead reuse passages from the document where possible.`,
  },
  {
    title: 'Extraction',
    description: 'Extract the opinions of different people in the documents',
    icon: 'list-magnifying-glass',
    prompt: `Extract the contributions and opinions of the different people mentioned in the document. Don't reuse passages from the text, but instead use your own words where possible.`,
  },
];

export const useStartModes = () => {
  const { params } = useParamsStore();
  const {
    settings: { isConfigDrawerOpen },
  } = useSettingsStore();
  const { queueFocusFileInput, focusFileInput } = useFocusFileInput();

  const modes = [
    {
      id: StartMode.UNGROUNDED,
      title: 'Just Chat',
      description: 'Use Coral without any access to external sources.',
      params: { connectors: [], documents: [], tools: [] },
      promptOptions: UNGROUNDED_PROMPTS,
    },
    {
      id: StartMode.TOOLS,
      title: 'Multihop Tool Use',
      description: 'Uses multiple sources and tools to answer questions with citations.',
      params: {
        connectors: [],
        documents: [],
        tools: [
          { id: TOOL_PYTHON_INTERPRETER_ID },
          { id: TOOL_CALCULATOR_ID },
          { id: TOOL_INTERNET_SEARCH_ID },
        ],
      },
      promptOptions: TOOL_PROMPTS,
    },
    {
      id: StartMode.WEB_SEARCH,
      title: 'Web Search',
      description:
        'Coral will search the web to find an answer and generates a response with citations.',
      params: { connectors: [{ id: TOOL_CHAT_DEFAULT }], documents: [], tools: [] },
      promptOptions: WEB_SEARCH_PROMPTS,
    },
    {
      id: StartMode.DOCUMENTS,
      title: 'Analyze Files',
      description: 'Upload a file and Coral will answer questions about it.',
      params: { connectors: [], documents: [], tools: [] },
      onChange: () => {
        if (!isConfigDrawerOpen) {
          queueFocusFileInput();
        } else {
          focusFileInput();
        }
      },
      promptOptions: DOCUMENT_PROMPTS,
    },
  ];

  const getSelectedModeIndex = (): number => {
    let selectedTabKey = StartMode.UNGROUNDED;
    if (params.tools && params.tools.length > 0) {
      selectedTabKey = StartMode.WEB_SEARCH;
    } else if (params.fileIds && params.fileIds.length > 0) {
      selectedTabKey = StartMode.DOCUMENTS;
    }
    return modes.findIndex((m) => m.id === selectedTabKey);
  };

  return { modes, getSelectedModeIndex };
};
