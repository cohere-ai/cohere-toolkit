/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [require('./src/themes/cohereTheme')],
  content: ['src/**/*.{js,jsx,ts,tsx}'],
  plugins: [require('@tailwindcss/typography')],
  darkMode: 'selector',
  safelist: [
    {
      pattern:
        /(bg|text|border|fill)-(blue|evolved-blue|coral|green|evolved-green|quartz|evolved-quartz|mushroom|evolved-mushroom|marble|volcanic|danger)-\S+/,
      variants: ['hover', 'dark', 'dark:hover'],
    },
  ],
  theme: {
    extend: {
      screens: {
        '3xl': '2000px',
      },
      minWidth: {
        'citation-panel-md': '259px', // subtract 10px for scrollbar and 1px for border
        'citation-panel-lg': '325px', // subtract 10px for scrollbar and 1px for border
        'citation-panel-xl': '349px', // subtract 10px for scrollbar and 1px for border
        menu: '174px',
        'agents-panel-collapsed': '82px',
        'agents-panel-expanded': '240px',
        'agents-panel-expanded-lg': '320px',
        'left-panel-lg': '242px',
        'left-panel-2xl': '300px',
        'left-panel-3xl': '360px',
      },
      width: {
        'icon-xs': '12px',
        'icon-sm': '14px',
        'icon-md': '16px',
        'icon-lg': '24px',
        'icon-xl': '36px',
        'btn-sm': '280px',
        'btn-md': '312px',
        'btn-lg': '350px',
        'btn-xl': '370px',
        modal: '648px',
        toast: '320px',
        'toast-sm': '280px',
        'citation-md': '250px',
        'citation-lg': '298px',
        'citation-xl': '320px',
        file: '224px',
        'edit-agent-panel': '350px',
        'edit-agent-panel-lg': '683px',
        'edit-agent-panel-2xl': '800px',
      },
      maxWidth: {
        message: '976px',
        'agents-panel-collapsed': '82px',
        'agents-panel-expanded': '240px',
        'agents-panel-expanded-lg': '320px',
        drawer: '288px',
        'drawer-lg': '360px',
        'left-panel-lg': '242px',
        'left-panel-2xl': '300px',
        'left-panel-3xl': '360px',
        'share-content': '700px',
        'share-content-with-citations': '1500px',
      },
      height: {
        'cell-button': '40px',
        'icon-xs': '12px',
        'icon-sm': '14px',
        'icon-md': '16px',
        'icon-lg': '24px',
        'icon-xl': '36px',
        header: '64px',
      },
      minHeight: {
        'cell-xs': '24px',
        'cell-sm': '32px',
        'cell-md': '40px',
        'cell-lg': '50px',
        'cell-xl': '64px',
        header: '64px',
      },
      maxHeight: {
        modal: 'calc(100vh - 120px)',
        'cell-xs': '24px',
        'cell-sm': '32px',
        'cell-md': '40px',
        'cell-lg': '50px',
        'cell-xl': '64px',
      },
      zIndex: {
        navigation: '30',
        dropdown: '60',
        toast: '70',
        'main-section': '10',
        'tag-suggestions': '10',
        'drag-drop-input-overlay': '10',
        'configuration-drawer': '20',
        'read-only-conversation-footer': '60',
        menu: '90',
        'guide-tooltip': '30',
        tooltip: '50',
        backdrop: '150',
        modal: '200',
      },
      boxShadow: {
        drawer: '-10px 4px 12px -10px rgba(197, 188, 172, 0.48)', // secondary-400
        menu: '0px 4px 12px 0px rgba(197, 188, 172, 0.48)', // secondary-400
        top: '4px 0px 12px 0px rgba(197, 188, 172, 0.48)', // secondary-400
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.volcanic.300'),
          },
        },
      }),
      keyframes: {
        typing: {
          '0%': {
            width: '0%',
            visibility: 'hidden',
          },
          '100%': {
            width: '100%',
          },
        },
        'left-to-right': {
          '0%': {
            left: '0%',
            transform: 'translateX(-100%)',
          },
          '100%': {
            left: '100%',
            transform: 'translateX(0%)',
          },
        },
        borealisBar: {
          '0%': {
            left: '0%',
            right: '100%',
            width: '0%',
          },
          '20%': {
            left: '0%',
            right: '75%',
            width: '25%',
          },
          '80%': {
            right: '0%',
            left: '75%',
            width: '25%',
          },
          '100%': {
            left: '100%',
            right: '0%',
            width: '0%',
          },
        },
      },
      transitionProperty: {
        spacing: 'padding',
      },
      animation: {
        'typing-ellipsis': 'typing 2s steps(4) infinite',
        'typing-loading-message': 'typing 0.7s steps(20)',
        'ping-once': 'ping 1s cubic-bezier(0, 0, 0.2, 1)',
        'left-to-right': 'left-to-right 0.5s ease-in-out infinite',
        borealisBar: 'borealisBar 2s linear infinite',
      },
      scale: {
        175: '1.75',
      },
      variants: {
        extend: {},
      },
      plugins: [],
    },
  },
};
