import { DataSourceArtifact } from '@/types/tools';

export const getDefaultUploadArtifacts = (
  readDocArtifacts?: DataSourceArtifact[],
  searchFileArtifacts?: DataSourceArtifact[]
): DataSourceArtifact[] => {
  const combinedArtifacts = (readDocArtifacts ?? []).concat(searchFileArtifacts ?? []);
  if (!readDocArtifacts || !searchFileArtifacts) return combinedArtifacts;

  const dedupedArtifacts: DataSourceArtifact[] = [];

  combinedArtifacts.forEach(({ type, id, name }) => {
    if (
      !dedupedArtifacts.find(
        (artifact) => artifact.type === type && artifact.id === id && artifact.name === name
      )
    ) {
      dedupedArtifacts.push({ type, id, name });
    }
  });
  return dedupedArtifacts;
};
