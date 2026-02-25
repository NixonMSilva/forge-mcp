from config import TIMEOUT_INFO
from mcp_instance import mcp
from utils import forge_client, format_error


@mcp.tool()
async def get_loras() -> str:
    """
    List all LoRA models available in Forge.

    LoRAs are lightweight style/character adapters you can activate in your
    prompt with the syntax <lora:name:weight> (e.g. <lora:character_elf:0.8>).
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/loras")

    if response.status_code != 200:
        return format_error(response)

    loras = response.json()
    if not loras:
        return "No LoRAs found."

    lines = [f"  {l['name']}" for l in loras]
    return f"Available LoRAs ({len(loras)}):\n" + "\n".join(lines)


@mcp.tool()
async def get_samplers() -> str:
    """
    List all sampler algorithms available in Forge.

    The sampler controls how diffusion steps are performed. Different samplers
    trade speed vs quality. Recommended starters: 'Euler a', 'DPM++ 2M Karras'.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/samplers")

    if response.status_code != 200:
        return format_error(response)

    samplers = response.json()
    names = [s["name"] for s in samplers]
    return "Available samplers:\n  " + "\n  ".join(names)


@mcp.tool()
async def get_embeddings() -> str:
    """
    List all textual inversion embeddings (TI tokens) loaded in Forge.

    Embeddings are activated directly in prompts by their token name, e.g.
    'masterpiece, best quality, <embedding_name>'.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/embeddings")

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    loaded = list(data.get("loaded", {}).keys())
    skipped = list(data.get("skipped", {}).keys())

    parts = [f"Loaded embeddings ({len(loaded)}): {', '.join(loaded) or 'none'}"]
    if skipped:
        parts.append(f"Skipped (incompatible) ({len(skipped)}): {', '.join(skipped)}")
    return "\n".join(parts)


@mcp.tool()
async def get_upscalers() -> str:
    """
    List all upscaler models available in Forge for use with upscale_image().
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/upscalers")

    if response.status_code != 200:
        return format_error(response)

    upscalers = response.json()
    names = [u["name"] for u in upscalers]
    return "Available upscalers:\n  " + "\n  ".join(names)


@mcp.tool()
async def get_vaes() -> str:
    """
    List all VAE (Variational Autoencoder) models available in Forge.

    The VAE affects colour accuracy and fine detail. 'Automatic' uses the one
    baked into the checkpoint; swap it if colours look washed out or over-saturated.
    """
    async with forge_client(TIMEOUT_INFO) as client:
        response = await client.get("/sdapi/v1/sd-vae")

    if response.status_code != 200:
        return format_error(response)

    vaes = response.json()
    if not vaes:
        return "No VAEs found."

    names = [v["model_name"] for v in vaes]
    return "Available VAEs:\n  " + "\n  ".join(names)
