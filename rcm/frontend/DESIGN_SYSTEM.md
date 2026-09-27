# CarePath Design System

A quick guide to the styles used in the CarePath clinic management app. Keep screens calm, clear, and easy to scan. Reuse the styles and components already in the app before creating new ones.

## Colors

Use the warm ivory colors for large surfaces and cobalt for navigation, links, and main actions. Use the `brand-*` colors from Tailwind for cobalt accents:

| Name | Color | Use it for |
| --- | --- | --- |
| `brand-50` | `#F1F3F9` | Light hover and selected backgrounds |
| `brand-100` | `#E1E7F4` | Light brand fills and borders |
| `brand-500` | `#315FC8` | Brand highlights |
| `brand-600` | `#244FC0` | Main buttons and controls |
| `brand-700` | `#1B3F9A` | Button hover and darker brand text |
| `brand-900` | `#172554` | Main text |

The page background is ivory (`#F5F2EA`); content areas use soft ivory and off-white (`#FCFBF7`, `#FFFEFA`). Use green for positive statuses, yellow for pending statuses, red for overdue or severe statuses, and gray for neutral statuses. Always show the status in text as well as color.

## Text

- Use `'Segoe UI', system-ui, sans-serif`.
- Keep tables and supporting information compact: usually `text-sm` for table text and `text-xs` or `text-sm` for labels.
- Make important values and headings semibold or bold.
- Use muted gray for secondary details, but keep the text easy to read against its background.

## Page Layout

- On wide screens, show the sidebar on the left. On smaller screens, let navigation fit across the top.
- Keep the top bar visible while the page scrolls.
- Put page content on a white surface with comfortable spacing. Reduce the margins and padding on small screens.
- Use Tailwind spacing utilities. Typical surface padding is `p-4` to `p-6`; typical control spacing is `gap-2` to `gap-4`.
- The shared layout changes at 1023px. Tailwind's `lg` breakpoint starts at 1024px.

## Surfaces

Use these existing classes from `src/index.css`:

- `.app-sidebar` for blue navigation.
- `.app-page` for the main white page area.
- `.data-card` for tables and record lists.
- `.glass-panel` for translucent panels, such as KPI tiles.
- `.app-search` for the rounded search field and its focus state.

Keep shadows and rounded corners subtle. Surfaces should feel soft, not glassy or heavily blurred. Avoid putting a framed panel inside another framed panel unless it helps separate a real task.

## Common Components

- **Navigation:** Active links have a white background and blue text. Inactive links brighten on hover. Icon-only buttons need an accessible name.
- **Main buttons:** Use a `brand-600` background with white text; darken it to `brand-700` on hover. Make disabled buttons visibly different.
- **Tables:** Use compact uppercase column headings, light row dividers, and a subtle hover background. Include a helpful empty state and label icon-only row actions.
- **Status badges:** Use a light status color with darker text, and include the status word.
- **KPI tiles:** Show a short label, a prominent value, and an optional hint. Save the gradient treatment for a small number of key metrics.
- **Dialogs:** Dim the page behind the dialog, give the dialog a clear title and close button, and ask for confirmation before consequential actions.

## Accessibility

- Every interactive control should have a visible keyboard focus state.
- Give icon-only buttons an accessible name.
- Associate form labels with their inputs and explain errors in text.
- Do not use color as the only way to communicate status.

## Where Styles Live

- Shared classes: `src/index.css`
- Brand color definitions: `tailwind.config.js`
- Reusable UI components: `src/components/`

When adding a design token, update both its implementation and this guide.