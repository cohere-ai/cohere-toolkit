import { AllMiddlewareArgs } from '@slack/bolt';

/**
 * Given a slack user id, and bolt client, get the user's real name.
 */
export type GetUsersRealNameArgs = Pick<AllMiddlewareArgs, 'client'> & {
  userId: string;
};

export const getUsersRealName = async ({ client, userId }: GetUsersRealNameArgs) => {
  const userInfo = await client.users.info({ user: userId });
  return userInfo.user?.real_name ?? '';
};
