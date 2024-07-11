import { ChannelSettings as ChannelSettingsPrisma } from '@prisma/client';

import { prisma } from '..';
import { Tool } from '../cohere-client';

type GetChannelSettingsArgs = {
  teamId: string | undefined;
  enterpriseId: string | undefined;
  channelId: string;
};

type ChannelSettings = {
  deployment: string | null;
  model: string | null;
  temperature: number | null;
  preambleOverride: string | null;
  tools: Tool[];
};

const getChannelSettingsPrisma = async ({
  teamId,
  enterpriseId,
  channelId,
}: GetChannelSettingsArgs): Promise<ChannelSettingsPrisma | undefined> => {
  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId, enterpriseId },
    update: {},
    where: { teamId, enterpriseId },
    include: {
      channelSettings: true,
    },
  });

  return workspaceSettings.channelSettings.find((set) => set.channelId === channelId);
};

export const getChannelSettings = async ({
  teamId,
  enterpriseId,
  channelId,
}: GetChannelSettingsArgs): Promise<ChannelSettings> => {
  const defaultSettings: ChannelSettings = {
    deployment: null, // Leave to API default,
    model: null, // Leave to API default
    temperature: null, // Leave to API default
    preambleOverride: null, // Leave to API default
    tools: [],
  };

  if (!prisma) return defaultSettings;

  const channelSettings = await getChannelSettingsPrisma({
    teamId,
    enterpriseId,
    channelId,
  });

  if (!channelSettings) return defaultSettings;

  const formattedTools = channelSettings?.tools && channelSettings?.tools.map((t) => ({ name: t }));

  return {
    deployment: channelSettings.deployment || defaultSettings.deployment,
    model: channelSettings.modelName || defaultSettings.model,
    temperature: channelSettings.temperature || defaultSettings.temperature,
    preambleOverride: channelSettings.preamble || defaultSettings.preambleOverride,
    tools: formattedTools || defaultSettings.tools,
  };
};
