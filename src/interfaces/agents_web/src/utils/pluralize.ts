export const pluralize = (text: string, quantity: number, customPluralization?: string) => {
  const isPlural = quantity > 1 || quantity === 0;
  if (customPluralization) {
    return isPlural ? customPluralization : text;
  }
  const pluralization = text.endsWith('s') ? 'es' : 's';
  return `${text}${isPlural ? pluralization : ''}`;
};
