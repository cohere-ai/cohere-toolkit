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