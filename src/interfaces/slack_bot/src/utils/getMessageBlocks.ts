import { Block, KnownBlock } from '@slack/bolt';

type GetEphemeralBlockArgs = {
  text: string;
  isDismissible?: boolean;
};

type GetFeedbackBlocksArgs = {
  responseID: string;
  threadTs: string;
};

type BlockArr = Array<Block | KnownBlock>;
/**
 * Ephemeral (ghost message that is only visible to the user) block that can have an optional dismiss button
 * This can be used in the built in say/respond functions and the postEphemeral function
 * Provide the output of this as the blocks property when making a call.
 * Use this to avoid code repetition of these block elements.
 */

export const getEphemeralBlocks = ({
  text,
  isDismissible = true,
}: GetEphemeralBlockArgs): BlockArr => {
  return isDismissible
    ? [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text,
          },
        },
        {
          type: 'actions',
          elements: [
            {
              type: 'button',
              action_id: 'dismiss_ephemeral',
              text: {
                type: 'plain_text',
                emoji: true,
                text: 'Dismiss',
              },
              value: 'dismiss',
            },
          ],
        },
      ]
    : [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text,
          },
        },
      ];
};

export const getContentBlocks = (text: string): BlockArr => {
  if (text.length > 3000) {
    throw new Error(`getContentBlocks: text length ${text.length} exceeds 3000 character limit`);
  }

  return [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text,
      },
    },
  ];
};

/**
 * Defines the feedback blocks used for bot responses.
 * Provide the output of this as the blocks property when making a call.
 */
export const getFeedbackBlocks = ({ threadTs }: GetFeedbackBlocksArgs): BlockArr => {
  return [
    {
      type: 'actions',
      elements: [
        {
          type: 'button',
          action_id: 'stop_conversation',
          text: {
            type: 'plain_text',
            emoji: true,
            text: ':shushing_face:',
          },
          value: `stop-${threadTs}`,
        },
      ],
    },
  ];
};
