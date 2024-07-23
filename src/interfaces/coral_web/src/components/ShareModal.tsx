'use client';

import React, { useEffect, useState } from 'react';

import { Button, Icon, Input, Spinner, Text } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useCreateSnapshotLinkId, useSnapshots } from '@/hooks/snapshots';

type ShareModalProps = {
  conversationId: string;
};

export const ShareModal: React.FC<ShareModalProps> = ({ conversationId }) => {
  const [status, setStatus] = useState<
    'modal-loading' | 'modal-error' | 'update-url-loading' | 'update-url-error' | undefined
  >('modal-loading');
  const { loadingSnapshots, getSnapshotLinksByConversationId, deleteAllSnapshotLinks } =
    useSnapshots();
  const { mutateAsync: createSnapshotLinkId } = useCreateSnapshotLinkId();
  const snapshotLinks = getSnapshotLinksByConversationId(conversationId);
  const snapshotLinksExists = !!snapshotLinks
    ? snapshotLinks && snapshotLinks.length > 0
    : undefined;

  const latestSnapshotLink = snapshotLinks[snapshotLinks.length - 1];
  const [linkId, setLinkId] = useState(latestSnapshotLink ?? '');

  useEffect(() => {
    if (loadingSnapshots) return;

    if (latestSnapshotLink && latestSnapshotLink) {
      setLinkId(latestSnapshotLink);
      setStatus(undefined);
    } else {
      const generateNewSnapshotLink = async () => {
        setStatus('modal-loading');
        try {
          const linkId = await createSnapshotLinkId({ conversationId });
          setLinkId(linkId);
          setStatus(undefined);
        } catch (e) {
          setStatus('modal-error');
        }
      };
      generateNewSnapshotLink();
    }
  }, [latestSnapshotLink, loadingSnapshots]);

  /**
   * @description deletes all snapshot links for a conversation and creates a new one
   */
  const updateSnapshotUrl = async () => {
    setStatus('update-url-loading');
    try {
      if (snapshotLinksExists) {
        await deleteAllSnapshotLinks(conversationId);
      }
      const linkId = await createSnapshotLinkId({ conversationId });
      if (linkId) {
        setLinkId(linkId);
        setStatus(undefined);
      } else {
        setStatus('update-url-error');
      }
    } catch (e) {
      setStatus('update-url-error');
      console.error(e);
    }
  };

  if (loadingSnapshots || snapshotLinksExists === undefined || status === 'modal-loading') {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (status === 'modal-error') {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Text className="text-danger-350">
          Unable to generate share link. Please try again later.
        </Text>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-y-8">
      {snapshotLinksExists && (
        <Text>
          You may have shared a part of this chat before. To share the current, full version of the
          chat, update the link below.
        </Text>
      )}
      <div className="flex flex-col gap-y-2">
        <Input
          truncate
          readOnly
          label="Share link"
          value={`${env.NEXT_PUBLIC_FRONTEND_HOSTNAME}/share/${linkId}`}
          actionType="copy"
          disabled={status === 'update-url-loading'}
        />
        <div className="flex justify-between">
          <Button
            kind="secondary"
            label="See preview"
            href={`${env.NEXT_PUBLIC_FRONTEND_HOSTNAME}/share/${linkId}`}
            target="_blank"
            endIcon="arrow-up-right"
            disabled={status === 'update-url-loading'}
            animate={false}
          />
          {snapshotLinksExists && (
            <Button
              kind="secondary"
              label={status === 'update-url-loading' ? 'Generating link' : 'Update link'}
              onClick={updateSnapshotUrl}
              endIcon={status === 'update-url-loading' ? <Spinner /> : <Icon name="redo" />}
              disabled={status === 'update-url-loading'}
              animate={false}
            />
          )}
        </div>
      </div>
      {status === 'update-url-error' && (
        <Text className="text-danger-350">
          Unable to generate a new share link. Please try again later.
        </Text>
      )}
      <div className="flex flex-col gap-y-2">
        <Text styleAs="label">Permissions & visibility</Text>
        <Text styleAs="caption" className="text-volcanic-400">
          Anyone with the link will see the full contents of this conversation history. You will be
          sharing the title, messages, and citations.
        </Text>
      </div>
    </div>
  );
};
