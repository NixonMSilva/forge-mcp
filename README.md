# Forge Painter — MCP Server

An MCP server for [SD WebUI Forge (Neo Branch)](https://github.com/lllyasviel/stable-diffusion-webui-forge) that exposes image generation tools to Claude Desktop and other MCP-compatible clients.

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

## Compatibility

This server targets **SD WebUI Forge Neo** and is developed and tested against it. That said, Forge Neo's API is a superset of the standard AUTOMATIC1111 API, so **sd-webui-automatic1111 (legacy A1111) may work** if you point the server URL at your A1111 instance.

> **Untested.** No compatibility testing has been done against legacy A1111. Core tools (`txt2img`, `img2img`, `inpaint`, `get_models`, `get_samplers`, etc.) map to standard `/sdapi/v1/` endpoints and are likely to work. Tools that rely on forge-specific extensions may not behave correctly or may return errors. Use at your own risk and open an issue if you encounter problems.

---

## Installation

### Option A — Download from Releases (recommended)

**Prerequisites:**

- SD WebUI Forge Neo running locally (default: `http://127.0.0.1:7860`)
- [`uv`](https://github.com/astral-sh/uv) installed and on your `PATH`

Download the latest `forge-painter.mcpb` from the [Releases page](../../releases/latest), then drag it into Claude Desktop (or double-click it). Claude Desktop will prompt for your Forge URL and optional credentials, then handle the rest automatically — no Python installation required.

| Prompt | Default | Description |
|---|---|---|
| Forge URL | `http://127.0.0.1:7860` | URL of your Forge Neo (or A1111) instance |
| API Username | _(blank)_ | Only needed if Forge was launched with `--api-auth` |
| API Password | _(blank)_ | Only needed if Forge was launched with `--api-auth` |
| Output Directory | `Documents/forge-painter` | Folder where generated images will be saved |

---

### Option B — Manual setup (development)

**Prerequisites:**

- Python 3.10+
- SD WebUI Forge Neo running locally (default: `http://127.0.0.1:7860`)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and edit as needed:

```powershell
copy .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `FORGE_URL` | `http://127.0.0.1:7860` | Forge Neo (or A1111) instance URL |
| `FORGE_API_USER` | _(blank)_ | Username if Forge was launched with `--api-auth` |
| `FORGE_API_PASSWORD` | _(blank)_ | Password if Forge was launched with `--api-auth` |
| `OUTPUT_DIR` | `outputs` | Directory where generated images are saved |
| `TIMEOUT_GENERATION` | `300` | Seconds to wait for txt2img/img2img/inpaint |
| `TIMEOUT_MODEL_SWITCH` | `120` | Seconds to wait for a checkpoint switch |

Then register the server in `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "forge-painter": {
      "command": "C:\\path\\to\\forge-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\forge-mcp\\server.py"],
      "cwd": "C:\\path\\to\\forge-mcp"
    }
  }
}
```

Restart Claude Desktop. **Forge Painter** will appear in the MCP tools panel.

---

### Building the .mcpb yourself

One-time prerequisites:

```powershell
pip install uv
npm install -g @anthropic-ai/mcpb
```

Build and sign:

```powershell
mcpb validate manifest.json
mcpb pack . forge-painter.mcpb
$env:PATH += ";C:\Program Files\Git\usr\bin"  # provides openssl
mcpb sign forge-painter.mcpb --self-signed    # claude might not open the .mcpb when signed, do at your own peril
```

To publish a new release: bump `version` in `manifest.json` and `pyproject.toml`, rerun the build commands above, and attach the updated `.mcpb` as an asset to a new GitHub Release.

---

## Troubleshooting

- If the Forge URL is unreachable, tools return errors but the server itself still loads.
- For the `.mcpb` option, `uv` must be on your `PATH` when Claude Desktop launches the server.
