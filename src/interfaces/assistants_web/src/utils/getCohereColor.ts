const BG_COLOR_LIST = [
  'bg-quartz-700',
  'bg-green-600',
  'bg-coral-500',
  'bg-quartz-700',
  'bg-green-250',
  'bg-coral-700',
];

const TEXT_COLOR_LIST = [
  'text-quartz-700',
  'text-green-600',
  'text-coral-500',
  'text-quartz-700',
  'text-green-250',
  'text-coral-700',
];

/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @param background - if true, returns a background color, otherwise returns a text color
 * @returns color from the Cohere color palette
 */
export const getCohereColor = (
  id?: string,
  options: { background?: boolean } = { background: true }
) => {
  const COLOR_LIST = options?.background ? BG_COLOR_LIST : TEXT_COLOR_LIST;
  if (id === undefined) {
    const randomIndex = Math.floor(Math.random() * COLOR_LIST.length);

    return COLOR_LIST[randomIndex];
  }
  const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % COLOR_LIST.length;
  return COLOR_LIST[index];
};
