# CISO Assistant Docs

This branch hosts the static CISO Assistant documentation site with Astro Starlight.

The source corpus stays in `docs/` so upstream GitBook exports remain easy to refresh. The Starlight build copies and normalizes the source into `src/content/docs/` at build time.

## Local development

```powershell
npm install
npm run dev
```

## Static build

```powershell
npm run build
```

## Azure Static Web Apps

`staticwebapp.config.json` requires authenticated access and redirects anonymous users to Entra ID sign-in. The deploy workflow expects this repository secret:

```text
AZURE_STATIC_WEB_APPS_API_TOKEN_CISO_DOCS
```
