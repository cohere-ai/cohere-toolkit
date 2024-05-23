const defaultTheme = require('tailwindcss/defaultTheme');

// Any changes to the theme should be reflected into our `customTwMerge` in `utils/cn.ts`
module.exports = {
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        pureWhite: '#FFFFFF',
        black: '#212121',
        white: '#FAFAFA',
        primary: {
          900: '#511D12',
          800: '#903420',
          700: '#CA492D',
          600: '#E25D41',
          500: '#FF7759',
          400: '#FF967E',
          300: '#FFAD9B',
          200: '#F8C8BC',
          100: '#F6DDD5',
          75: '#FBE0DA',
          50: '#FDF2F0',
        },
        secondary: {
          900: '#39352E',
          800: '#676054',
          700: '#8E8572',
          600: '#9D9482',
          500: '#AFA694',
          400: '#C5BCAC',
          300: '#D7CFC1',
          200: '#E4DED2',
          100: '#E9E6DE',
          50: '#F5F4F2',
        },
        // Marble white
        marble: {
          500: '#BDBDBD',
          400: '#E0E0E0',
          300: '#EEEEEE',
          200: '#F5F5F5',
          100: '#FAFAFA',
        },
        // Volcanic black
        volcanic: {
          900: '#212121',
          800: '#424242',
          700: '#616161',
          600: '#757575',
          500: '#9E9E9E',
        },
        // Coniferous green
        green: {
          900: '#16211C',
          800: '#2B4239',
          700: '#39594D',
          500: '#71867E',
          400: '#869790',
          300: '#9DAAA4',
          200: '#B2BBB6',
          100: '#D4D9D4',
          50: '#EEF0EF',
        },
        // Synthetic Quartz
        quartz: {
          900: '#3E2644',
          800: '#754880',
          700: '#9B60AA',
          600: '#B576C5',
          500: '#D18EE2',
          300: '#E8C3F0',
          200: '#EAD0F0',
          100: '#F0DFF3',
          50: '#F8F1F9',
        },
        // Acrylic Blue
        blue: {
          900: '#121E4A',
          700: '#2D4CB9',
          500: '#4C6EE6',
          300: '#A9B9F3',
          200: '#C0CAEF',
          100: '#DBE0F2',
          50: '#F0F2FB',
        },

        // Safety Green
        success: {
          500: '#05690D',
          200: '#C3DBC5',
          50: '#EFF5EA',
        },
        // Safety Red
        danger: {
          900: '#5A0000',
          500: '#B20000',
          200: '#F0CCCC',
          50: '#FFF1F1',
        },
      },
      fontSize: {
        // rem values calculated with a base font of 16px
        caption: ['0.75rem', { letterSpacing: '-0.01em', lineHeight: '136%' }], // 12px - Caption
        'label-sm': ['0.625rem', { letterSpacing: '0.04em', lineHeight: '136%' }], // 10px - Small Label
        label: ['0.75rem', { letterSpacing: '0.04em', lineHeight: '136%' }], // 12px - Label
        overline: ['0.875rem', { letterSpacing: '0.04em', lineHeight: '136%' }], // 14px - Overline
        'p-xs': ['0.625rem', { letterSpacing: '0.0025em', lineHeight: '150%' }], // 10px - XSmall Paragraph
        'p-sm': ['0.75rem', { letterSpacing: '-0.01em', lineHeight: '150%' }], // 12px - Small Paragraph
        p: ['0.875rem', { letterSpacing: '0.0025em', lineHeight: '150%' }], // 14px - Paragraph
        'p-lg': ['1rem', { letterSpacing: '0em', lineHeight: '150%' }], // 16px - Large Paragraph
        code: ['1rem', { letterSpacing: '0.03em', lineHeight: '136%' }], // 16px - Code
        'code-sm': ['0.75rem', { letterSpacing: '0.03em', lineHeight: '136%' }], // 12px - Small Code
        // Headings
        logo: ['1.5rem', { letterSpacing: '0em', lineHeight: '100%' }], // 24px - Logo Application
        'h5-m': ['1.125rem', { letterSpacing: '0em', lineHeight: '136%' }], // 18px - Mobile Heading 5
        h5: ['1.3125rem', { letterSpacing: '0em', lineHeight: '136%' }], // 21px - Desktop Heading 5
        'h4-m': ['1.3125rem', { letterSpacing: '0em', lineHeight: '136%' }], // 21px - Mobile Heading 4
        h4: ['1.75rem', { letterSpacing: '0em', lineHeight: '136%' }], // 28px - Desktop Heading 4
        'h3-m': ['1.75rem', { letterSpacing: '0em', lineHeight: '136%' }], // 28px - Mobile Heading 3
        h3: ['2.375rem', { letterSpacing: '0em', lineHeight: '120%' }], // 38px - Desktop Heading 3
        'h2-m': ['2.375rem', { letterSpacing: '0em', lineHeight: '120%' }], // 38px - Mobile Heading 2
        h2: ['3.1875rem', { letterSpacing: '0em', lineHeight: '116%' }], // 51px - Desktop Heading 2
        'h1-m': ['3.1875rem', { letterSpacing: '0em', lineHeight: '116%' }], // 51px - Mobile Heading 1
        h1: ['4.1875rem', { letterSpacing: '0em', lineHeight: '116%' }], // 67px - Desktop Heading 1
        'icon-sm': ['12px', { lineHeight: '100%' }],
        'icon-md': ['16px', { lineHeight: '100%' }],
        'icon-lg': ['24px', { lineHeight: '100%' }],
        'icon-xl': ['36px', { lineHeight: '100%' }],
      },
      fontFamily: {
        body: ['Arial', ...defaultTheme.fontFamily.sans],
        variable: ['Arial', ...defaultTheme.fontFamily.serif],
        code: defaultTheme.fontFamily.mono,
        iconOutline: ['CohereIconOutline'],
        iconDefault: ['CohereIconDefault'],
      },
      fontWeight: {
        // Bolded fonts will always use Cohere Variable with the weight 525
        medium: '525',
      },
    },
  },
};
