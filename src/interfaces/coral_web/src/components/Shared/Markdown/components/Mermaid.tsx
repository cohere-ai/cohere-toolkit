import mermaid, { MermaidConfig } from 'mermaid';
import { ReactElement, useEffect, useId, useRef, useState } from 'react';

export function Mermaid({ chart }: { chart: string }): ReactElement {
  const id = useId();
  const [svg, setSvg] = useState('');
  const containerRef = useRef(null);

  useEffect(() => {
    const htmlElement = document.documentElement;
    const mutationObserver = new MutationObserver(renderChart);
    mutationObserver.observe(htmlElement, { attributes: true });
    renderChart();

    return () => {
      mutationObserver.disconnect();
    };

    // Switching themes taken from https://github.com/mermaid-js/mermaid/blob/1b40f552b20df4ab99a986dd58c9d254b3bfd7bc/packages/mermaid/src/docs/.vitepress/theme/Mermaid.vue#L53
    async function renderChart() {
      const isDarkTheme =
        htmlElement.classList.contains('dark') ||
        htmlElement.attributes.getNamedItem('data-theme')?.value === 'dark';
      const mermaidConfig: MermaidConfig = {
        startOnLoad: false,
        securityLevel: 'loose',
        fontFamily: 'inherit',
        themeCSS: 'margin: 1.5rem auto 0;',
        theme: isDarkTheme ? 'dark' : 'default',
      };

      try {
        mermaid.initialize(mermaidConfig);
        const { svg } = await mermaid.render(
          // strip invalid characters for `id` attribute
          id.replaceAll(':', ''),
          chart,
          containerRef.current || undefined
        );
        setSvg(svg);
      } catch (error) {
        // eslint-disable-next-line no-console -- show error
        // console.error('Error while rendering mermaid', error);
      }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps -- when chart code changes, we need to re-render
  }, [chart]);

  return <div ref={containerRef} dangerouslySetInnerHTML={{ __html: svg }} />;
}
