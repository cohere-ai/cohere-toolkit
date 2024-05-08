# Theming and customization

## Changing the color scheme, font and other styles

To change the color scheme of the Coral frontend, there are a few options:

- Modify the `src/interfaces/coral_web/src/themes/cohereTheme.js` with a new color scheme. For example, to change the primary color scheme:

```js
primary: {
  ...
  600: '#E25D41',
  500: '#AE4359', // Changed from default color
  400: '#FF967E',
  ...
},
```

- Add a new theme to the `src/interfaces/coral_web/src/themes` folder and update the `src/interfaces/coral_web/tailwind.config.js` to include the new theme:

```js
module.exports = {
  presets: [require('./src/themes/yourTheme')],
  ...
}
```

Similarly, you can change the font, font size, and other styles in the theme file or add a new theme file.

After updating the theme, you will need to rebuild the frontend to see the changes.

## Changing the logo in the upper left corner

To change the logo in the upper left corner of the frontend, do the following:

1. Set the `NEXT_PUBLIC_HAS_CUSTOM_LOGO` environment variable to `true` in the `.env` file.

2. Modify the function in `src/interfaces/coral_web/src/components/Shared/Logo.tsx` to display the updated logo.

The default function displays the `/images/logo.png` file in the `public` folder if it exists and the `NEXT_PUBLIC_HAS_CUSTOM_LOGO` environment variable is set to `true`.

## Changing the favicon and other metadata

- To update the favicon, replace the existing file at `public/favicon.ico` with your new favicon file.
- To modify the metadata, edit the following files:
  - `src/interfaces/coral_web/src/components/Shared/WebManifestHead.tsx`
  - `src/interfaces/coral_web/src/components/Shared/GlobalHead/GlobalHead.tsx`
  - `src/interfaces/coral_web/public/site.webmanifest`

## Changing the page title

To update the page title, alter the `title` property in the file located at `src/interfaces/coral_web/src/components/Layout.tsx` to reflect your new title.
