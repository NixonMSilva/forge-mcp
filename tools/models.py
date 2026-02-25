from config import TIMEOUT_INFO, TIMEOUT_MODEL_SWITCH
from mcp_instance import mcp
from utils import forge_client, format_error


@mcp.tool()
async def get_models() -> str:
    """
    List all Stable Diffusion checkpoints (models) available in Forge.

    Returns the model title and filename for each checkpoint so you can
    pick the right one for your art style before generating.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/sd-models")

    if response.status_code != 200:
        return format_error(response)

    models = response.json()
    if not models:
        return "No models found."

    lines = [f"  [{i+1}] {m['title']}  ({m['filename']})" for i, m in enumerate(models)]
    return "Available models:\n" + "\n".join(lines)


@mcp.tool()
async def set_model(model_title: str) -> str:
    """
    Switch the active Stable Diffusion checkpoint in Forge.

    Use get_models() first to see the exact title string to pass here.
    Model switching can take 10-60 seconds depending on model size.

    Args:
        model_title: The exact title of the model as returned by get_models().
    """
    payload = {"sd_model_checkpoint": model_title}

    async with forge_client(TIMEOUT_MODEL_SWITCH) as client:
        response = await client.post("/sdapi/v1/options", json=payload)

    if response.status_code != 200:
        return format_error(response)

    return f"Model switched to '{model_title}'. Give Forge a moment to load it before generating."


@mcp.tool()
async def get_current_model() -> str:
    """
    Return the name of the checkpoint that is currently loaded in Forge.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/options")

    if response.status_code != 200:
        return format_error(response)

    opts = response.json()
    return f"Current model: {opts.get('sd_model_checkpoint', 'unknown')}"


@mcp.tool()
async def refresh_models() -> str:
    """
    Tell Forge to scan the models folder and reload the list of available
    checkpoints, LoRAs and embeddings.

    Run this after copying new model files into the Forge models directory
    so they appear in get_models(), get_loras(), etc. without restarting Forge.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        r_ckpt = await client.post("/sdapi/v1/refresh-checkpoints")
        r_lora = await client.post("/sdapi/v1/refresh-loras")

    results = []
    results.append(
        "Checkpoints refreshed." if r_ckpt.status_code == 200 else format_error(r_ckpt)
    )
    results.append(
        "LoRAs refreshed." if r_lora.status_code == 200 else format_error(r_lora)
    )
    return "\n".join(results)
