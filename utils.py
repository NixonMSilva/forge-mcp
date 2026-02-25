import base64
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import httpx

from config import (
    FORGE_API_PASSWORD,
    FORGE_API_USER,
    FORGE_URL,
    TIMEOUT_GENERATION,
)


@asynccontextmanager
async def forge_client(
    timeout: float = TIMEOUT_GENERATION,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Async context manager that yields a pre-configured httpx client.

    Automatically applies HTTP Basic Auth when FORGE_API_USER is set in
    the environment, so individual tools never handle credentials directly.
    """
    auth = (FORGE_API_USER, FORGE_API_PASSWORD) if FORGE_API_USER else None
    async with httpx.AsyncClient(
        base_url=FORGE_URL,
        auth=auth,
        timeout=timeout,
    ) as client:
        yield client


def encode_image(path: str) -> str:
    """Read an image file and return it as a base64 string."""
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")


def decode_and_save(b64: str, path: str) -> None:
    """Decode a base64 string and write it to *path*."""
    Path(path).write_bytes(base64.b64decode(b64))


def format_error(response: httpx.Response) -> str:
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    return f"Forge error {response.status_code}: {detail}"
