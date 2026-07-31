from pathlib import Path

import customtkinter as ctk
from PIL import Image

from db_admin.db import LOGOS_DIR


def load_thumbnail(path: str | Path | None, size: tuple[int, int] = (96, 96)) -> ctk.CTkImage | None:
    """Load an image file as a CTkImage, returning None if the file is missing/unreadable."""
    if not path:
        return None
    file_path = Path(path)
    if not file_path.is_absolute():
        from db_admin.db import REPO_ROOT

        file_path = REPO_ROOT / file_path
    if not file_path.exists():
        return None
    try:
        image = Image.open(file_path)
        image.load()
    except Exception:
        return None
    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def save_logo(icao: str, source_path: str) -> Path:
    """Validate `source_path` as an image, re-encode it as PNG, and save it to
    data/logos/{icao}.png, overwriting any existing logo for that airline."""
    image = Image.open(source_path)
    image.load()
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")

    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    dest = LOGOS_DIR / f"{icao}.png"
    image.save(dest, format="PNG")
    return dest


def delete_logo(icao: str) -> None:
    dest = LOGOS_DIR / f"{icao}.png"
    if dest.exists():
        dest.unlink()
