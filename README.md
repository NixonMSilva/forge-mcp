# Forge Painter — MCP Server

An MCP server for [SD WebUI Forge Neo](https://github.com/lllyasviel/stable-diffusion-webui-forge) that exposes image generation tools to Claude Desktop and other MCP-compatible clients.

## Tools

| Tool | Description |
|---|---|
| `txt2img` | Generate an image from a text prompt |
| `img2img` | Generate an image from a prompt + input image |
| `inpaint` | Inpaint a masked region of an image |
| `upscale_image` | Upscale an image |
| `get_models` / `set_model` / `get_current_model` / `refresh_models` | Manage checkpoints |
| `get_loras` / `get_samplers` / `get_embeddings` / `get_upscalers` / `get_vaes` | List available assets |
| `get_progress` / `interrupt_generation` | Monitor and control active jobs |

## Prerequisites

- Python 3.10+
- SD WebUI Forge Neo running locally (default: `http://127.0.0.1:7860`)

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and edit as needed:

```powershell
copy .env.example .env
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `FORGE_URL` | `http://127.0.0.1:7860` | Forge Neo instance URL |
| `FORGE_API_USER` | _(blank)_ | Username if Forge was launched with `--api-auth` |
| `FORGE_API_PASSWORD` | _(blank)_ | Password if Forge was launched with `--api-auth` |
| `OUTPUT_DIR` | `outputs` | Directory where generated images are saved |
| `TIMEOUT_GENERATION` | `300` | Seconds to wait for txt2img/img2img/inpaint |
| `TIMEOUT_MODEL_SWITCH` | `120` | Seconds to wait for a checkpoint switch |

---

## Deployment

There are two ways to connect this server to Claude Desktop.

### Option A — Manual config (development)

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "forge-painter": {
      "command": "f:\\Projects\\Forge-MCP\\.venv\\Scripts\\python.exe",
      "args": ["f:\\Projects\\Forge-MCP\\server.py"],
      "cwd": "f:\\Projects\\Forge-MCP"
    }
  }
}
```

Restart Claude Desktop. The **Forge Painter** server will appear in the MCP tools panel.

### Option B — MCPB bundle (portable, one-click install)

Download the latest `forge-painter.mcpb` from the [Releases page](../../releases/latest), then drag it into Claude Desktop (or double-click it). Claude Desktop will prompt for your Forge URL and optional credentials.

**To build the bundle yourself:**

One-time prerequisites:

```powershell
pip install uv
npm install -g @anthropic-ai/mcpb
```

Build and sign:

```powershell
cd f:\Projects\Forge-MCP

mcpb validate manifest.json
mcpb pack . forge-painter.mcpb
$env:PATH += ";C:\Program Files\Git\usr\bin"  # provides openssl
mcpb sign forge-painter.mcpb --self-signed
```

**Rebuild after changes:** bump `version` in `manifest.json` and `pyproject.toml`, then rerun the build commands above and publish a new GitHub Release with the updated `.mcpb` as an asset.

---

## Troubleshooting

- MCP server logs: `%APPDATA%\Claude\logs\`
- If `FORGE_URL` is unreachable, tools return errors but the server itself still loads.
- For the MCPB option, `uv` must be on your `PATH` when Claude Desktop launches the server.
