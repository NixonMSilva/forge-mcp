import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Forge connection
# ---------------------------------------------------------------------------

FORGE_URL: str = os.getenv("FORGE_URL", "http://127.0.0.1:7860")

# Credentials for Forge's --api-auth flag (leave blank if auth is disabled).
FORGE_API_USER: str = os.getenv("FORGE_API_USER", "")
FORGE_API_PASSWORD: str = os.getenv("FORGE_API_PASSWORD", "")

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

# Default to an absolute path next to this file so the save location is
# predictable regardless of what working directory the server is launched from
# (e.g. when running via a .mcpb bundle with uv).
_default_output = str(Path(__file__).parent / "outputs")
OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", _default_output))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Timeouts (seconds)
# ---------------------------------------------------------------------------

# Long-running generation requests (txt2img, img2img, inpaint, upscale).
TIMEOUT_GENERATION: float = float(os.getenv("TIMEOUT_GENERATION", "300"))

# Model / checkpoint switching — can be slow for large models.
TIMEOUT_MODEL_SWITCH: float = float(os.getenv("TIMEOUT_MODEL_SWITCH", "120"))

# Lightweight informational requests (listing models, samplers, etc.).
TIMEOUT_INFO: float = float(os.getenv("TIMEOUT_INFO", "30"))

# Fire-and-forget control requests (interrupt, progress check).
TIMEOUT_CONTROL: float = float(os.getenv("TIMEOUT_CONTROL", "10"))
