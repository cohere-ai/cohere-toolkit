import { expect, test } from 'vitest';

import { getSanitizedMessage } from './getSanitizedMessage';

const REAL_NAME_OBJ: { [key: string]: string } = {
  U03N7809HN2: 'John Doe',
  U039SJJFB62: 'Richard Roe',
  U057LCN53UK: 'Jane Smith',
  U059C8BPCP4: 'Command',
};

const getUsersRealName = ({ userId }: { userId: string }) => {
  return REAL_NAME_OBJ[userId];
};
const sanitizeTestData = [
  ['Hi <@U03N7809HN2>! How are you?', 'Hi John Doe! How are you?\n'],
  [
    'I, <@U03N7809HN2>, am gonna have a chat with <@U039SJJFB62> over in <#C05594QMD9Q|command-slack-bot>',
    'I, John Doe, am gonna have a chat with Richard Roe over in #command-slack-bot\n',
  ],
  [
    "<@U039SJJFB62>, will be working with <@U057LCN53UK> on a future project, updates for which they'll provide in <#C03SMGA4P62|squad-growth>. They'll move updates to <#C03SMGA4P62|secret-project> once enough people have joined the channel.",
    "Richard Roe, will be working with Jane Smith on a future project, updates for which they'll provide in #squad-growth. They'll move updates to #secret-project once enough people have joined the channel.\n",
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
    'This has a non-existing user present, like <@U039SGGFB62>, or <@BOB>. So it should remove them all together.',
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
  ['Hi <@U03N7809HN2>! How are you?', 'Hi John Doe! How are you?\n'],
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
