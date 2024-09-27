import Link from 'next/link';
import React from 'react';

import { pluralize } from '@/utils';

export const STRINGS = {
  // General
  instructions: 'Instructions',
  tool: 'Tool',
  tools: 'Tools',
  required: 'Required',
  discover: 'Discover',
  create: 'Create',
  cancel: 'Cancel',
  delete: 'Delete',
  deleting: 'Deleting',
  tryNow: 'Try now',
  search: 'Search',
  update: 'Update',
  updating: 'Updating',
  file: 'File',
  files: 'Files',
  seeMore: 'See more',
  output: 'Output',
  here: 'here',
  selected: 'Selected',
  dropToUpload: 'Drop to upload',
  save: 'Save',
  saving: 'Saving',
  settings: 'Settings',
  share: 'Share',
  reset: 'Reset',
  next: 'Next',
  done: 'Done',
  gotIt: 'Got it',
  copied: 'Copied!',
  copy: 'Copy',
  mostRecent: 'Most recent',
  on: 'On',
  off: 'Off',
  configure: 'Configure',
  value: 'Value',
  logIn: 'Log in',
  signUp: 'Sign up',
  logOut: 'Log out',
  selectAnOption: 'Select an option',
  noResultsFound: 'No results found',
  workingOnIt: 'Working on it',

  // Assistants
  createAssistantTitle: 'Create Assistant',
  createAnAssistantTitle: 'Create an Assistant',
  createAnAssistantDescription: 'Create a unique assistant and share with your org',
  hideAssistant: 'Hide assistant',
  editAssistant: 'Edit assistant',
  aboutAssistant: 'About assistant',
  deleteAssistant: 'Delete assistant',
  deleteAssistantTitle: 'Delete Assistant',
  assistantNameDescription: 'Give your assistant a name',
  assistantDescriptionDescription: 'What does your assistant do?',
  assistantPreambleDescription:
    'Give instructions to your chatbot. What does it do? How does it behave?',
  yourAssistants: 'Your assistants',
  selectFilesFolders: 'Select files/folders',
  assistantNameUniqueError: 'Assistant name must be unique',
  createAssistantError: 'Failed to create assistant',
  creatingAssistant: 'Creating assistant',
  yesMakeItPublic: 'Yes, make it public',
  discoverAssistantsTitle: 'Discover Assistants',
  discoverAssistantsDescription:
    'Assistants created by your peers to help you solve tasks and increase efficiency',
  baseAssistantDescription:
    'Review, understand and ask questions about internal financial documents.',
  loadAssistantError: 'Unable to load assistant information',
  attachFileWithExtensions:
    'Attach file (.PDF, .TXT, .MD, .JSON, .CSV, .XSLS, .XLS, .DOCX Max 20 MB)',
  noFilesFound: "You don't have any files, upload one to use with the assistant.",
  assistantToolsDescription:
    'Tools are data sources the assistant can search such as databases or the internet.',

  // Everything else
  newChat: 'New chat',
  messageInput: 'Message...',
  siteGroundingTitle: 'Site (Optional)',
  siteGroundingDescription: 'Ground on 1 domain e.g. wikipedia.org',
  multipleSiteGroundingError: 'Multiple domains are not supported.',
  shareLinkToConversation: 'Share link to conversation',
  toggleChatList: 'Toggle chat list',
  newMessage: 'New message',
  editTitle: 'Edit title',
  editTitleTitle: 'Edit Title',
  deleteChat: 'Delete chat',
  chats: 'Chats',
  fromTheWeb: 'from the web',
  loadConversationsError: 'Unable to load conversations.',
  noConversations: "It's quiet here... for now",
  updateConversationTitleError: 'Failed to update conversation title. Please try again.',
  actionRequired: 'Action required',
  readyToUse: 'Ready to use',
  connectYourData: 'Connect your data',
  connectYourDataDescription:
    'In order to get the most accurate answers grounded on your data, connect the following:',
  filesInConversation: 'Files in conversation',
  filesInConversationDescription:
    'To use uploaded files, at least 1 File Upload tool must be enabled',
  closeDrawer: 'Close drawer',
  model: 'Model',
  temperature: 'Temperature',
  preamble: 'Preamble',
  preambleExample:
    'e.g. You are Coral, a large language model trained to have polite, helpful, inclusive conversations with people.',
  toolsDescriptionLong:
    'Tools are functions that the model can access, such as searching Wikipedia or summarizing an uploaded PDF. Follow the documentation to add custom available tools.',
  toolsOnOffDescription: 'Tools can be turned on or off at any time in your conversation.',
  toolsDescriptionShort:
    'Tools are data sources the assistant can search such as databases or the internet.',
  dropFilesToUpload: 'Drop files to upload',
  pdfOrTxtRestriction: '.PDF or .TXT, Max 20MB',
  filterModel: 'Filter model',
  toSelect: 'to select',
  toMoveUpDown: 'to move up/down',
  toClose: 'to close',
  toViewAllOptions: 'to view all options',
  pageNotFoundDescription: 'This page could not be found.',
  pageServerErrorDescription: 'Something went wrong. Our team is working on it.',
  uploadingFile: 'Uploading file...',
  connectDataDescription:
    'Your data must be connected in order to use this assistant. Connecting to your data will allow you to use the assistant to its full potential.',
  startConnecting: 'Start connecting',
  somethingWentWrong: 'Something went wrong.',
  pleaseTryAgainLater: 'Please try again later.',
  downloadTableCSVError: 'Unable to download table as CSV.',
  downloadAsCSV: 'Download as CSV',
  selectADeployment: 'Select a deployment',
  configureModelDeploymentTitle: 'Configure Model Deployment',
  fileSizeExceededError: 'Each file can only be 20 MB max',
  incorrectFileTypeError: 'File type has to be .PDF or .TXT.',
  fileNameExistsError: 'File with the same name already exists.',
  generationErrorMessage: 'Unable to generate a response since an error was encountered.',
  retryQuestion: 'Retry?',
  generationWasStopped: 'This generation was stopped.',
  copyText: 'Copy text',
  hideSteps: 'Hide steps',
  showSteps: 'Show steps',
  startANewConversation: 'Start a new conversation',
  deleteCurrentConversation: 'Delete current conversation',
  generateShareLinkError: 'Unable to generate share link. Please try again later.',
  updateShareLinkError: 'Unable to generate a new share link. Please try again later.',
  existingShareLinkDescription:
    'You may have shared a part of this chat before. To share the current, full version of the chat, update the link below.',
  shareLink: 'Share link',
  seePreview: 'See preview',
  generatingLink: 'Generating link',
  updateLink: 'Update link',
  permissionsAndVisibility: 'Permissions & visibility',
  shareLinkDescription:
    'Anyone with the link will see the full contents of this conversation history. You will be sharing the title, messages, and citations.',
  noResourcesFound: 'No resources found.',
  botWelcomeMessage: 'Need help? Your wish is my command.',
  toggleLeftSidebar: 'Toggle left sidebar',
  toggleGroundingDrawer: 'Toggle grounding drawer',
  focusOnChatInput: 'Focus on chat input',
  copyLastResponse: 'Copy last response',
  copiedLastResponseToClipboard: 'Copied last response to clipboard',
  copiedLastResponseError: 'Unable to copy last response',
  agentIDNotFoundError: 'Agent ID not found',
  networkError: 'Something went wrong. This has been reported.',
  generationError: 'Unable to generate a response since an error was encountered.',
  networkErrorSuggestion: 'Ensure a COHERE_API_KEY is configured correctly',
  conversationIDNotFoundError: 'Conversation ID not found',
  deleteConversationConfirmation: 'Are you sure you want to delete this conversation?',

  // Welcome guide tooltips
  welcomeToToolkitTitle: 'Welcome to Toolkit',
  welcomeToToolkitDescription:
    'Say hi to the model! Open this sidebar to select tools and data sources the model should use in this conversation.',
  configureYourToolsTitle: 'Configure your Tools',
  configureYourToolsDescription:
    'Your configured Tools will be listed here, such as a sample PDF retrieval tool. Follow [these steps](link when available) to add your own.',
  uploadDocumentsAsASourcetitle: 'Upload Documents as a Source',
  uploadDocumentsAsASourceDescription:
    'Upload a PDF document as a retrieval source. This will use the PDF retrieval tool.',
  deleteFileError: 'Unable to delete file.',
  selectGoogleDriveFilesOrFolders: 'Please select either files or folders.',
  selectMaxGoogleDriveFilesDescription: 'You can only select a maximum of 5 files.',
  googleDriveUnavailableError: 'Google Drive is not available at the moment.',
  newConversationTitle: 'New Conversation',

  // First turn suggestions
  plotRealEstateData: 'Plot real estate data',
  plotRealEstateDataPrompt:
    'Plot the average 1 bedroom rental price in Jan 2024 for the 5 most expensive cities in North America',
  cleanUpDataInPython: 'Clean up data in Python',
  cleanUpDataInPythonPrompt: `I want to figure out how to remove nan values from my array. For example, my array looks something like this:
    
    x = [1400, 1500, 1600, nan, nan, nan, 1700] #Not in this exact configuration
        
    How can I remove the nan values from x to get something like:
        
    x = [1400, 1500, 1600, 1700]`,
  writeABusinessPlanInFrench: 'Write a business plan in French',
  writeABusinessPlanInFrenchPrompt:
    'Write a business plan outline for an marketing agency in French. Highlight all the section titles, and make it less than 300 words.',
};

export const DYNAMIC_STRINGS = {
  assistantInstructionsDescription: (
    <>
      Learn about writing a custom assistant instructions with{' '}
      <Link
        href="https://docs.cohere.com/docs/preambles#advanced-techniques-for-writing-a-preamble"
        className="underline"
      >
        Cohere&apos;s guide
      </Link>
    </>
  ),
  createAssistantConfirmationTitle: (name: string) => `Create ${name}?`,
  createAssistantConfirmationDescription: (name: string) =>
    `Your assistant ${name} is about be visible publicly. Everyone in your organization will be able to see and use it.`,
  deleteAssistantConfirmationDescription: (name: string) => (
    <>
      Your assistant <strong>{name}</strong> will be deleted. This action cannot be undone.
    </>
  ),
  updatedAssistantConfirmation: (name: string) => `Updated ${name}`,
  updateAssistantError: (name: string) => `Failed to update ${name}`,
  updateAssistantTitle: (name: string) => `Update ${name}`,
  aboutAssistantTitle: (name: string) => `About ${name}`,
  updateAssistantInfo: (name: string) =>
    `Updating ${name} will affect everyone using the assistant`,
  numReferences: (num: number) => `${num} ${pluralize('reference', num)}`,
  fromTool: (toolName: string) => `from ${toolName}`,
  executionTime: (time: string) => `Execution time: ${time}ms`,
  // Usage of this string requires the use of STRINGS.here
  unauthedToolError: (toolName: string, hereLink: React.ReactNode) => (
    <>
      You need to connect {toolName} before you can use this tool. Authenticate {hereLink}.
    </>
  ),
  noResultsFoundForQuery: (query: string) => `No results found for "${query}".`,
  deleteConversationDescription: (numConversations: number) => `Once you delete ${
    numConversations === 1 ? 'this chat' : 'these chats'
  } you will be unable to
        see or retrieve the messages. You cannot undo this action.`,
  deleteNumConversations: (numConversations: number) =>
    `Delete ${numConversations === 1 ? '' : numConversations} ${pluralize(
      'conversation',
      numConversations
    )}`,
  noToolsAssistant: (name: string) => `${name} does not use any tools.`,
  continueWithLoginService: (serviceName: string) => `Continue with ${serviceName}`,
  conversationNotFoundDescription: (url: string) => (
    <>
      This conversation does not exist, <br /> why not create a{' '}
      <Link href={url} className="underline">
        new one
      </Link>
      ?
    </>
  ),
  usingTool: (toolName: string) => (
    <>
      Using <b className="font-medium">{toolName}</b>.
    </>
  ),
  calculatingExpression: (expression: string) => (
    <>
      Calculating <b className="font-medium">{expression}</b>.
    </>
  ),
  searchingQuery: (query: string) => (
    <>
      Searching <b className="font-medium">{query}</b>.
    </>
  ),
  uploadFilesBatchMaximumError: (maxFiles: number) =>
    `You can upload a maximum of ${maxFiles} files at a time.`,
  fileTypeNotSupportedError: (type: string) => `File type not supported (${type})`,
  fileSizeCannotExceedError: (size: string) => `File size cannot exceed ${size}`,
  referenceNumber: (num: number) => `Reference #${num}`,
  fromReferences: (references: string) => `From: ${references}`,
  weeksAgo: (weeksAgo: number) => `${weeksAgo} ${pluralize('week', weeksAgo)} ago`,
  numBytes: (bytes: number) => `${bytes} bytes`,
  numKB: (kb: string) => `${kb} KB`,
  numMB: (mb: string) => `${mb} MB`,
};
