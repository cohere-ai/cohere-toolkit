import { expect, test } from 'vitest';

import { getSanitizedMessage } from './getSanitizedMessage';

const REAL_NAME_OBJ: { [key: string]: string } = {
  U0000000123: 'John Doe',
  U0000000456: 'Richard Roe',
  U0000000789: 'Jane Smith',
  U059C8BPCP4: 'Command',
};

const getUsersRealName = ({ userId }: { userId: string }) => {
  return REAL_NAME_OBJ[userId];
};
const sanitizeTestData = [
  ['Hi <@U0000000123>! How are you?', 'Hi John Doe! How are you?\n'],
  [
    'I, <@U0000000123>, am gonna have a chat with <@U0000000456> over in <#C000000ABC|command-slack-bot>',
    'I, John Doe, am gonna have a chat with Richard Roe over in #command-slack-bot\n',
  ],
  [
    "<@U0000000456>, will be working with <@U0000000789> on a future project, updates for which they'll provide in <#C0000000XYZ|updates>. They'll move updates to <#C03SMGA4P62|secret-project> once enough people have joined the channel.",
    "Richard Roe, will be working with Jane Smith on a future project, updates for which they'll provide in #updates. They'll move updates to #secret-project once enough people have joined the channel.\n",
  ],
  [
    "This message doesn't have any mentions or channel links, so nothing should change.",
    "This message doesn't have any mentions or channel links, so nothing should change.\n",
  ],
  [
    "Lets say this message has an @mention and #channel-name but it's not formatted in slack format. Nothing should change.",
    "Lets say this message has an @mention and #channel-name but it's not formatted in slack format. Nothing should change.\n",
  ],
  [
    'This has a non-existing user present, like <@U0000000ABC>, or <@BOB>. So it should remove them all together.',
    'This has a non-existing user present, like , or . So it should remove them all together.\n',
  ],
  [
    'Check chars involved: < > # 5<6 6>5 #slackBot </b>',
    'Check chars involved: &lt; > # 5&lt;6 6&gt;5 #slackBot </b>\n',
  ],
];

test.each(sanitizeTestData)('Sanitizes message correctly', async (input, expectedOutput) => {
  expect(
    await getSanitizedMessage({
      message: input,
      getUsersRealName,
    }),
  ).toBe(expectedOutput);
});

const sanitizeFirstMessageTestData = [
  ['Hi <@U0000000123>! How are you?', 'Hi John Doe! How are you?\n'],
  ['<@U059C8BPCP4> How are you?', 'How are you?\n'],
  ['<@U059C8BPCP4> How is <@U059C8BPCP4>?', 'How is Command?\n'],
];

test.each(sanitizeFirstMessageTestData)(
  'Sanitizes first message correctly',
  async (input, expectedOutput) => {
    expect(
      await getSanitizedMessage({
        message: input,
        getUsersRealName,
        botUserId: 'U059C8BPCP4',
        isFirstMessage: true,
      }),
    ).toBe(expectedOutput);
  },
);
