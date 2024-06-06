import { prisma } from '..';

const getSlackAuthToken = async (enterpriseId?: string, teamId?: string) => {
  if (!prisma || (!enterpriseId && !teamId)) return process.env.SLACK_BOT_TOKEN;

  const oauth = await prisma.oAuthInstallation.findUnique({
    where: {
      teamId: teamId,
      enterpriseId: enterpriseId,
    },
  });
  if (!oauth) return process.env.SLACK_BOT_TOKEN;

  // @ts-ignore - Prisma JSONObject doesn't play well with TS
  return oauth.installation.bot.token || process.env.SLACK_BOT_TOKEN;
};

export const getSlackFile = async (
  fileUrl: string,
  enterpriseId?: string,
  teamId?: string,
): Promise<ArrayBuffer> => {
  const authToken = await getSlackAuthToken(enterpriseId, teamId);

  return await fetch(fileUrl, {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  }).then((response) => {
    if (response.status !== 200) {
      throw new Error('unable to access file through slack');
    }
    // TODO: verify that the response is actually a file
    return response.arrayBuffer();
  });
};
