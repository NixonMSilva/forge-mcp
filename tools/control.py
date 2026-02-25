from config import TIMEOUT_CONTROL
from mcp_instance import mcp
from utils import forge_client, format_error


@mcp.tool()
async def get_progress() -> str:
    """
    Check the progress of the currently running generation in Forge.

    Returns the completion percentage and estimated time remaining.
    Returns 'idle' if nothing is generating.
    """
    async with forge_client(TIMEOUT_CONTROL) as client:
        response = await client.get("/sdapi/v1/progress")

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    progress = data.get("progress", 0)

    if progress == 0 and not data.get("state", {}).get("job_count"):
        return "Forge is idle — no generation in progress."

    eta = data.get("eta_relative", 0)
    job = data.get("state", {}).get("job", "unknown")
    return (
        f"Generation in progress: {progress * 100:.1f}% complete\n"
        f"Current job: {job}\n"
        f"ETA: {eta:.1f}s"
    )


@mcp.tool()
async def interrupt_generation() -> str:
    """
    Interrupt (cancel) the currently running generation in Forge immediately.

    Use this if a generation is taking too long or if you submitted the wrong
    prompt and want to stop it before it finishes.
    """
    async with forge_client(TIMEOUT_CONTROL) as client:
        response = await client.post("/sdapi/v1/interrupt")

    if response.status_code != 200:
        return format_error(response)

    return "Generation interrupted."
