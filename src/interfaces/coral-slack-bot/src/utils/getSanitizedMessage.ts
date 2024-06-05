import slackify from 'slackify-markdown';

type GetSanitizedMessageArgs = {
  message: string;
  getUsersRealName: Function;
  botUserId?: string;
  isFirstMessage?: boolean;
};

/**
 * Replaces '@Mentions' and '<@mentions>' from strings with the user's real name fetched from Slack
 * Replaces channel links in the form of <#C04J5P41JSD|chat-interfaces> with channel names, i.e. #chat-interfaces
 * ex:
 *    input I, <@U03N7809HN2>, am gonna have a chat with <@U039SJJFB62> over in <#C05594QMD9Q|coral-slack-bot>
 *    output: I, Shubham Shukla, am gonna have a chat with Spencer Elliott over in #coral-slack-bot
 *
 */
export const getSanitizedMessage = async ({
  message,
  getUsersRealName,
  botUserId,
  isFirstMessage = false,
}: GetSanitizedMessageArgs) => {
  const userIDAndNames: { [key: string]: string } = {};

  // Match the format <@U03N7809HN2>
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

  // Match the format <#C04J5P41JSD|chat-interfaces> and replace with #chat-interfaces
  const msgWithChannelNamesAndMemberNames = msgWithMemberNames.replace(/<#\w+\|([-\w]+)>/g, '#$1');

  const msgWithSlackFormatting = slackify(msgWithChannelNamesAndMemberNames);

  return msgWithSlackFormatting;
};
