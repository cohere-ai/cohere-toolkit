type Props = {
  fileId: string;
};

export const FileViewer: React.FC<Props> = ({ fileId }) => {
  return <div>{fileId}</div>;
};
