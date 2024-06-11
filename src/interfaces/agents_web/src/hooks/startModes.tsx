import { DEFAULT_CHAT_TOOL } from '@/cohere-client';
import { IconName } from '@/components/Shared';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';

export enum StartMode {
  UNGROUNDED = 'ungrounded',
  WEB_SEARCH = 'web_search',
  TOOLS = 'tools',
}

type Prompt = {
  title: string;
  description: React.ReactNode;
  icon: IconName;
  prompt: string;
};

type Mode = {
  id: StartMode;
  title: string;
  description: string;
  params: Partial<ConfigurableParams>;
  promptOptions: Prompt[];
  onChange?: VoidFunction;
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
    title: 'Stay up to date',
    description: 'US tech company employee count',
    icon: 'newspaper',
    prompt: 'Give me the number of employees at Apple, Amazon, and Google in a table.',
  },
  {
    title: 'Research',
    description: 'Overview of solar panel industry',
    icon: 'flask',
    prompt: 'What are some cutting edge companies working on solar energy?',
  },
  {
    title: 'Learn a topic',
    description: 'Missions to the moon',
    icon: 'book',
    prompt: `How many missions have there been to the moon?`,
  },
];

export const useStartModes = () => {
  const { params } = useParamsStore();

  const modes: Mode[] = [
    {
      id: StartMode.UNGROUNDED,
      title: 'Just Chat',
      description: 'Use Coral without any access to external sources.',
      params: { fileIds: [], tools: [] },
      promptOptions: UNGROUNDED_PROMPTS,
    },
    {
      id: StartMode.WEB_SEARCH,
      title: 'Wikpedia',
      description: 'Use multiple sources and tools to answer questions with citations.',
      params: { fileIds: [], tools: [{ name: DEFAULT_CHAT_TOOL }] },
      promptOptions: WEB_SEARCH_PROMPTS,
    },
  ];

  const getSelectedModeIndex = (): number => {
    let selectedTabKey = StartMode.UNGROUNDED;
    if (params.tools && params.tools.length > 0) {
      selectedTabKey = StartMode.WEB_SEARCH;
    }
    return modes.findIndex((m) => m.id === selectedTabKey);
  };

  return { modes, getSelectedModeIndex };
};
