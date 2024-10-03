### Changing the Color Scheme, Font, and Other Styles

1. **Modify Existing Theme:**
   - Update the color scheme in `src/interfaces/coral_web/src/themes/cohereTheme.js`:
     ```js
     primary: {
       ...
       600: '#E25D41',
       500: '#AE4359', // Changed from default color
       400: '#FF967E',
       ...
     },
     ```

2. **Add a New Theme:**
   - Create a new theme file in the `src/interfaces/coral_web/src/themes` folder.
   - Update `src/interfaces/coral_web/tailwind.config.js`:
     ```js
     module.exports = {
       presets: [require('./src/themes/yourTheme')],
       ...
     }
     ```

3. **Rebuild the Frontend:**
   - After making changes, rebuild the frontend to apply updates.

### Changing the Logo

1. **Set Environment Variable:**
   - In the `.env` file, set `NEXT_PUBLIC_HAS_CUSTOM_LOGO=true`.

2. **Modify Logo Component:**
   - Update the logo display in `src/interfaces/coral_web/src/components/Shared/Logo.tsx`.

### Changing the Favicon and Metadata

1. **Update Favicon:**
   - Replace `public/favicon.ico` with the new favicon file.

2. **Modify Metadata:**
   - Edit:
     - `src/interfaces/coral_web/src/components/Shared/WebManifestHead.tsx`
     - `src/interfaces/coral_web/src/components/Shared/GlobalHead/GlobalHead.tsx`
     - `src/interfaces/coral_web/public/site.webmanifest`

### Changing the Page Title

- Update the `title` property in `src/interfaces/coral_web/src/components/Layout.tsx`.

### Customizing Language

- Translate UI labels in `src/interfaces/coral_web/src/constants/strings.tsx`.
