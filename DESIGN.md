# DESIGN

## Visual Register

- Register: quiet operational SaaS for security and compliance work.
- Density: medium-high. Lists and tables should prioritize scanability, comparison, filters, and fast repeated actions over spacious editorial composition.
- Primary comparison products: GRC, compliance, and admin consoles with predictable navigation and clear state.
- Anti-references: landing-page heroes, nested presentation cards, decorative color blocks, one-off onboarding panels, and generic gradient-heavy AI dashboards.

## Typography

- UI font: use the app's existing font stack and Tailwind utilities. Do not add a new font dependency for fork-local work.
- Display font: avoid display typography inside operational views. Page titles can be prominent; panel and table headings should stay compact.
- Monospace font: use only for IDs, references, payload snippets, technical evidence, and code-like values.
- Type scale notes: do not scale font size with viewport width. Keep letter spacing at `0` unless using an existing uppercase utility. Long names, customer domains, and UUID-like references must wrap or truncate intentionally.

## Color

- Background: use the existing light/dark theme surfaces. Dark mode must be complete across page background, sidebar, tables, forms, dropdowns, and modals.
- Surface: prefer unframed sections, table rows, subtle borders, and narrow hierarchy strips. Use cards only for repeated objects, modals, and genuine tools.
- Text: maintain high contrast in both light and dark modes. Secondary text must remain readable; avoid low-opacity gray-on-dark combinations.
- Accent: use existing primary, success, warning, error, and surface tokens. Avoid introducing a new fork-only palette.
- Semantic colors: status and coverage colors must carry meaning consistently. Do not rely on color alone; include labels, icons, or table values.
- Avoid: purple-blue gradients as default surfaces, decorative blobs, tinted nested cards, and palettes dominated by a single hue.

## Layout And Components

- Navigation: keep the left sidebar predictable. New MSP features should live where operators expect them: domains under Organization, assertions and provider-operated controls under Operations.
- Forms: use existing form components and validation behavior. Domain parent selection should use the tree selector when hierarchy matters.
- Tables and lists: default to dense, sortable, filterable tables. For domain hierarchy, show parent path, child count, content type, and inspect/edit actions close to the data.
- Cards and panels: do not put cards inside cards. Do not use explanatory cards to compensate for missing workflow affordances.
- Modals and drawers: use for create/edit/confirm workflows only. Keep titles concrete and body copy short.
- Data visualization: use diagrams and hierarchy views when they help inspect structure or relationships. They should be inspectable, not decorative.

## Interaction States

- Loading: show compact inline loading states near the affected table, hierarchy, or form.
- Empty: state what is absent and provide the next useful action.
- Error: show the failed operation and recovery path. Background API failures should not silently degrade critical navigation.
- Success: confirm mutations succinctly and keep the user in context.
- Disabled: disabled controls need visible reason through label, tooltip, validation text, or nearby state.

## Motion

- Allowed: small transform/opacity transitions for menus, row affordances, and focus changes.
- Avoid: motion required to understand state, ornamental animation, or page-level transitions that slow repeated work.
- Reduced-motion behavior: all motion must remain optional and should respect reduced-motion settings where framework support exists.

## Accessibility And Responsive Rules

- Mobile: login, MFA, forms, tables, and domain hierarchy views must avoid horizontal overflow. Toolbars should wrap or collapse into familiar controls.
- Keyboard: tables, side navigation, modals, menus, and tree selectors must remain keyboard reachable with visible focus states.
- Contrast: dark mode must be verified visually for text, icons, borders, selected states, disabled states, and form controls.
- Text fitting: customer names, domain names, evidence references, and requirement names must not overlap actions or adjacent cells.

## Implementation Notes

- Existing design system: SvelteKit 2, Svelte 5, Tailwind 4, Skeleton/Skeleton Svelte, Bits UI, existing app components under `frontend/src/lib/components`.
- Icon library: Font Awesome is already used heavily. Use it before adding new icon dependencies.
- Localization: user-facing strings should use Paraglide message keys or `safeTranslate` where the existing dynamic table patterns require it. Keep locale catalogs complete.
- Assets: use the existing CISO Assistant logo and product assets. Do not create decorative SVG hero art for operator workflows.
- Verification commands: for narrow frontend work run `npm exec -- pnpm check` from `frontend` and `git diff --check` from the repo root. Use Playwright/browser proof for responsive, login, dark-mode, or layout-affecting changes.
