# CISO Assistant MTG fork guide

This active fork contains Django backend, Svelte frontend, CLI/integration tooling, and framework libraries. Read [CONTRIBUTING.md](CONTRIBUTING.md), [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md), and the affected area's README. Preserve upstream licensing, contribution/CLA requirements, domain isolation, RBAC, and auditability alongside MTG changes.

## Development and checks

Backend checks use `uv run pytest` in `backend/` per CONTRIBUTING. In `frontend/`, MTG CI uses `pnpm install --frozen-lockfile` then `pnpm run test:ci`; package scripts also provide `pnpm run check`, `pnpm run lint`, and `pnpm run build`. Use the pinned pnpm/Node requirements from the manifest and workflow. For browser changes, select the documented Playwright/E2E or accessibility checks rather than treating unit tests as browser proof. Add regressions for new functionality and bug fixes.

Preserve migration checks, permission boundaries, tenant/domain ownership, framework import semantics, and secret handling. Never use production GRC records or access tokens as test fixtures. Security reports follow SECURITY.md rather than public issues.

## Build and deployment boundaries

[documentation/mtg-fork-operations.md](documentation/mtg-fork-operations.md) prohibits image builds and dependency installation on the shared Azure/Bifrost VM; MTG images build in GitHub Actions and deployments are pull-only with backup/rollback. Preserve that safeguard.

That document describes an Azure/Compose lane, while current infra guidance places CISO compute on Talos with Azure PostgreSQL retained. Confirm the exact live target and consult `bifrost-infra`'s CISO runbook before any operation; do not execute the historical VM helper by default. The README also warns against deploying main directly: use reviewed stable tags or published images. Source approval, image publication, deployment, migrations, and runtime proof are separate gates. Read back the selected image, health, and affected user flow after an authorized release.
