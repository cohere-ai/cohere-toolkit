export const COLOR_LIST = [
  'bg-quartz-500',
  'bg-green-500',
  'bg-primary-500',
  'bg-quartz-700',
  'bg-green-700',
  'bg-primary-700',
];

/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @returns color from the Cohere color palette
 */
export const getCohereColor = (id?: string) => {
  if (id === undefined) {
    const randomIndex = Math.floor(Math.random() * COLOR_LIST.length);
    console.log(randomIndex);
    return COLOR_LIST[randomIndex];
  }

  const index = id.charCodeAt(0) % COLOR_LIST.length;
  return COLOR_LIST[index % COLOR_LIST.length];
};
