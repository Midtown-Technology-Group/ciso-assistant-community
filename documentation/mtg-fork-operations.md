# MTG Fork Operations

This fork carries MTG-specific operational changes on top of upstream CISO Assistant.
Treat the Azure CISO Assistant deployment as an app host, not a build host.

## Build Rule

Do not build images on the shared Azure/Bifrost VM.

Allowed on the VM:

- `docker pull`
- `docker compose up -d frontend`
- health checks
- compose backup and rollback

Not allowed on the VM:

- `docker build`
- package manager installs for application builds
- source checkout builds
- dependency resolution as part of deploy

## Image Build

Use GitHub Actions workflow `MTG Build Frontend Image`.

The workflow builds `frontend/Dockerfile` and pushes:

- `ghcr.io/midtown-technology-group/mtg-ciso-assistant-frontend:mtg-<short-sha>`
- `ghcr.io/midtown-technology-group/mtg-ciso-assistant-frontend:sha-<full-sha>`
- `ghcr.io/midtown-technology-group/mtg-ciso-assistant-frontend:mtg-main` on `main`

The image build includes OCI labels, SBOM, and provenance.

## Pull-Only Deploy

Use:

```bash
tools/mtg/deploy-ciso-frontend-pull-only.sh IMAGE /opt/ciso-assistant-poc
```

The deploy helper:

- refuses untagged images
- pulls the image or verifies a local image exists
- backs up `/opt/ciso-assistant-poc/docker-compose.yml`
- updates only the `frontend` service image
- recreates only the frontend service
- prints the rollback backup path

## Azure Verification

After deploy, verify:

```bash
curl -sS -H 'Host: ciso.midtowntg.com' http://127.0.0.1:8100/api/health/
docker inspect bifrost-api-1 --format 'bifrost_api={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{end}}'
docker inspect ciso-poc-backend --format 'ciso_backend={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{end}}'
docker inspect ciso-poc-frontend --format 'ciso_frontend={{.State.Status}} image={{.Config.Image}}'
```

For feature-specific verification, inspect the running frontend image contents or use a browser
against `https://ciso.midtowntg.com/`.

## Rollback

Restore the most recent compose backup and recreate the frontend service:

```bash
cd /opt/ciso-assistant-poc
cp docker-compose.yml.bak-<timestamp> docker-compose.yml
docker compose up -d frontend
```
