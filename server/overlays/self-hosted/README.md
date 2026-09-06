# Self-hosted overlay

Opt-in compose overlay for running mem0/server with:

- AWS Bedrock as the LLM provider (mounts `~/.aws` for SSO creds)
- A local Ollama sidecar with NVIDIA GPU passthrough as the embedder provider
- `restart: unless-stopped` on every service so the stack auto-starts after host reboot

The base `server/docker-compose.yaml` is upstream-pristine. This overlay is **not** auto-merged — opt in by passing it explicitly to compose.

## Use

From `server/`:

```bash
docker compose \
  -f docker-compose.yaml \
  -f overlays/self-hosted/docker-compose.override.yaml \
  up -d
```

Or via `COMPOSE_FILE`:

```bash
cd server
export COMPOSE_FILE=docker-compose.yaml:overlays/self-hosted/docker-compose.override.yaml
docker compose up -d
```

## Required server `.env`

Pair this overlay with these settings (in `server/.env`):

```
MEM0_DEFAULT_LLM_PROVIDER=aws_bedrock
MEM0_DEFAULT_LLM_MODEL=us.anthropic.claude-sonnet-4-6
AWS_PROFILE=<your-bedrock-profile>
AWS_REGION=us-west-2

MEM0_DEFAULT_EMBEDDER_PROVIDER=ollama
MEM0_DEFAULT_EMBEDDER_MODEL=bge-m3
MEM0_DEFAULT_EMBEDDING_DIMS=1024
```

These keys are consumed by the patched `server/main.py` (`_llm_default_config()` / `_embedder_default_config()`).

## Pulling the embedder model

After the stack is up:

```bash
docker compose exec ollama ollama pull bge-m3
```

(First memory write also auto-pulls if not present, but pre-pulling makes the first request fast.)

## To opt out of any single piece

Edit or delete blocks in `docker-compose.override.yaml`. For example, drop the `ollama` service block to use a different embedder, or remove the `${HOME}/.aws` mount if you authenticate via IRSA / instance profile.
