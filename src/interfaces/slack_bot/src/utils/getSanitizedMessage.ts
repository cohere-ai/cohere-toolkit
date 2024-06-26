import slackify from 'slackify-markdown';

type GetSanitizedMessageArgs = {
  message: string;
  getUsersRealName: Function;
  botUserId?: string;
  isFirstMessage?: boolean;
};

/**
 * Replaces '@Mentions' and '<@mentions>' from strings with the user's real name fetched from Slack
 * Replaces channel links in the form of <#C0000ABC123|test-channel> with channel names, i.e. #test-channel
 * ex:
 *    input I, <@U0000000123>, am gonna have a chat with <@U0000000456> over in <#C000000ABC|command-slack-bot>
 *    output: I, John Doe, am gonna have a chat with Richard Roe over in #command-slack-bot
 */
export const getSanitizedMessage = async ({
  message,
  getUsersRealName,
  botUserId,
  isFirstMessage = false,
}: GetSanitizedMessageArgs) => {
  const userIDAndNames: { [key: string]: string } = {};

  // Match the format <@U0000000123>
  const usersMentionedInMsg = message.match(/<@(.*?)>/g) || [];

  // Construct the userID and real name object
  if (usersMentionedInMsg.length > 0)
    for (let user of usersMentionedInMsg) {
      // extract the user id from the string
      const userId = (user.match(/\w+/g) ?? [''])[0];
      if (userId && !userIDAndNames[userId]) {
        const usersRealName = await getUsersRealName({ userId });
        userIDAndNames[userId] = usersRealName ?? '';
      }
    }

  let msgWithMemberNames = message;
  if (Object.keys(usersMentionedInMsg).length > 0)
    for (let [index, [key, value]] of Object.entries(userIDAndNames).entries()) {
      // If this is the initial app_mention message, remove the first mention
      if (isFirstMessage && index === 0 && key === botUserId)
        msgWithMemberNames = msgWithMemberNames.replace(`<@${key}> `, '');

      // After handling the first mention, replace all mentions with the user's real name
      msgWithMemberNames = msgWithMemberNames.replaceAll(`<@${key}>`, value);
    }

  // Match the format <#C0000ABC123|test-channel> and replace with #test-channel
  const msgWithChannelNamesAndMemberNames = msgWithMemberNames.replace(/<#\w+\|([-\w]+)>/g, '#$1');

  const msgWithSlackFormatting = slackify(msgWithChannelNamesAndMemberNames);

  return msgWithSlackFormatting;
};
