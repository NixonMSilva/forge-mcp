from pathlib import Path

from config import OUTPUT_DIR, TIMEOUT_GENERATION
from mcp_instance import mcp
from utils import decode_and_save, encode_image, forge_client, format_error


@mcp.tool()
async def txt2img(
    prompt: str,
    negative_prompt: str = "",
    steps: int = 20,
    cfg_scale: float = 7.0,
    width: int = 1024,
    height: int = 1024,
    sampler_name: str = "Euler a",
    seed: int = -1,
    batch_size: int = 1,
    save_path: str = "output.png",
) -> str:
    """
    Generate one or more images from a text prompt using Stable Diffusion Forge.

    Each image in the batch is saved as <save_path>, <save_path>_1.png, etc.
    Use seed=-1 for a random seed. Returns the seed(s) that were used so the
    result can be reproduced later. Images are saved inside the configured
    OUTPUT_DIR unless save_path is an absolute path.

    Args:
        prompt: Positive prompt describing the desired image.
        negative_prompt: Things to avoid in the image.
        steps: Number of diffusion steps (higher = more detail, slower).
        cfg_scale: Classifier-free guidance scale. Higher = more prompt-adherent.
        width: Image width in pixels.
        height: Image height in pixels.
        sampler_name: Sampler to use (e.g. 'Euler a', 'DPM++ 2M', 'DDIM').
        seed: RNG seed. Use -1 for random.
        batch_size: Number of images to generate in one request.
        save_path: Filename for the output PNG. Relative paths are placed inside
                   OUTPUT_DIR; absolute paths are used as-is.
    """
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "sampler_name": sampler_name,
        "seed": seed,
        "batch_size": batch_size,
    }

    async with forge_client(TIMEOUT_GENERATION) as client:
        response = await client.post("/sdapi/v1/txt2img", json=payload)

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    images = data.get("images", [])
    info = data.get("info", {})
    seeds = info.get("all_seeds", [seed] * len(images)) if isinstance(info, dict) else [seed]

    base = _resolve_path(save_path)
    saved = []
    for i, img_b64 in enumerate(images):
        out = base if i == 0 else base.with_stem(f"{base.stem}_{i}")
        decode_and_save(img_b64, str(out))
        saved.append(str(out))

    return (
        f"Generated {len(saved)} image(s).\n"
        f"Saved to: {', '.join(saved)}\n"
        f"Seeds used: {seeds}"
    )


@mcp.tool()
async def img2img(
    image_path: str,
    prompt: str,
    negative_prompt: str = "",
    denoising_strength: float = 0.6,
    steps: int = 20,
    cfg_scale: float = 7.0,
    width: int = 0,
    height: int = 0,
    sampler_name: str = "Euler a",
    seed: int = -1,
    save_path: str = "output_img2img.png",
) -> str:
    """
    Transform an existing image guided by a text prompt (image-to-image).

    Useful for restyling character art, adding details to maps, converting
    sketches to finished illustrations, or applying a new art style.

    Args:
        image_path: Path to the source image file (PNG/JPG).
        prompt: Positive prompt describing the desired result.
        negative_prompt: Things to avoid in the output.
        denoising_strength: How much to change the image. 0 = no change,
                            1 = ignore original. 0.4-0.7 is a good range.
        steps: Diffusion steps.
        cfg_scale: Prompt adherence strength.
        width: Output width. Use 0 to keep the source image size.
        height: Output height. Use 0 to keep the source image size.
        sampler_name: Sampler to use.
        seed: RNG seed (-1 for random).
        save_path: Filename for the output PNG. Relative paths land in OUTPUT_DIR.
    """
    b64 = encode_image(image_path)

    payload = {
        "init_images": [b64],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_name": sampler_name,
        "seed": seed,
    }
    if width:
        payload["width"] = width
    if height:
        payload["height"] = height

    async with forge_client(TIMEOUT_GENERATION) as client:
        response = await client.post("/sdapi/v1/img2img", json=payload)

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    images = data.get("images", [])
    info = data.get("info", {})
    used_seed = info.get("seed", seed) if isinstance(info, dict) else seed

    if not images:
        return "No images returned by Forge."

    out = _resolve_path(save_path)
    decode_and_save(images[0], str(out))
    return f"img2img complete. Saved to '{out}'. Seed: {used_seed}"


@mcp.tool()
async def inpaint(
    image_path: str,
    mask_path: str,
    prompt: str,
    negative_prompt: str = "",
    denoising_strength: float = 0.75,
    steps: int = 20,
    cfg_scale: float = 7.0,
    sampler_name: str = "Euler a",
    mask_blur: int = 4,
    inpainting_fill: int = 1,
    seed: int = -1,
    save_path: str = "output_inpaint.png",
) -> str:
    """
    Inpaint (fill or redraw) a masked region of an existing image.

    Paint the area to be replaced pure white in the mask image; the rest
    should be pure black. Great for fixing anatomy, swapping costume pieces,
    adding/removing props, or retouching TTRPG character portraits.

    Args:
        image_path: Path to the source image.
        mask_path: Path to the mask image (white = repaint, black = keep).
        prompt: What to paint in the masked area.
        negative_prompt: Things to avoid.
        denoising_strength: Strength of inpainting (0.5-0.85 recommended).
        steps: Diffusion steps.
        cfg_scale: Prompt adherence strength.
        sampler_name: Sampler to use.
        mask_blur: Blur radius applied to mask edges for smoother blending.
        inpainting_fill: Fill mode for the masked area before diffusion.
                         0=fill, 1=original, 2=latent noise, 3=latent nothing.
        seed: RNG seed (-1 for random).
        save_path: Filename for the output PNG. Relative paths land in OUTPUT_DIR.
    """
    img_b64 = encode_image(image_path)
    mask_b64 = encode_image(mask_path)

    payload = {
        "init_images": [img_b64],
        "mask": mask_b64,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_name": sampler_name,
        "mask_blur": mask_blur,
        "inpainting_fill": inpainting_fill,
        "inpaint_full_res": True,
        "seed": seed,
    }

    async with forge_client(TIMEOUT_GENERATION) as client:
        response = await client.post("/sdapi/v1/img2img", json=payload)

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    images = data.get("images", [])

    if not images:
        return "No images returned by Forge."

    out = _resolve_path(save_path)
    decode_and_save(images[0], str(out))
    return f"Inpainting complete. Saved to '{out}'."


@mcp.tool()
async def upscale_image(
    image_path: str,
    upscaling_resize: float = 2.0,
    upscaler: str = "R-ESRGAN 4x+",
    save_path: str = "output_upscaled.png",
) -> str:
    """
    Upscale an image using a super-resolution model available in Forge.

    Ideal for taking a draft character portrait or map tile and making it
    print-ready without re-generating from scratch.

    Args:
        image_path: Path to the image to upscale.
        upscaling_resize: Multiplier for the output size (e.g. 2.0 = 2x, 4.0 = 4x).
        upscaler: Name of the upscaler model. Common choices:
                  'R-ESRGAN 4x+', 'R-ESRGAN 4x+ Anime6B',
                  'Lanczos', 'Nearest', 'LDSR', '4x-UltraSharp'.
        save_path: Filename for the output PNG. Relative paths land in OUTPUT_DIR.
    """
    b64 = encode_image(image_path)

    payload = {
        "image": b64,
        "upscaling_resize": upscaling_resize,
        "upscaler_1": upscaler,
    }

    async with forge_client(TIMEOUT_GENERATION) as client:
        response = await client.post("/sdapi/v1/extra-single-image", json=payload)

    if response.status_code != 200:
        return format_error(response)

    data = response.json()
    img_b64 = data.get("image")
    if not img_b64:
        return "Forge returned no image data."

    out = _resolve_path(save_path)
    decode_and_save(img_b64, str(out))
    return f"Upscaled {upscaling_resize}x using '{upscaler}'. Saved to '{out}'."


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_path(save_path: str) -> Path:
    """Return an absolute Path, placing relative paths inside OUTPUT_DIR."""
    p = Path(save_path)
    return p if p.is_absolute() else OUTPUT_DIR / p
