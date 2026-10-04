"""
RetailIQ - Product Image Module

Real, unbranded product photos for the shoes/bags/cosmetics demo dataset,
matched by base product type (e.g. any "... RUNNING SNEAKERS" description
matches the running_sneakers.jpg photo, regardless of its color variant).

This is intentionally separate from product_icons.py: images are only
available for product types we have a real photo for (currently the
shoes/bags/cosmetics catalog). Any other dataset's products - or any
product type not in IMAGE_FILENAME_MAP - simply has no image here, and
the app falls back to the emoji icon system automatically.
"""

import base64
import functools
import os

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "product_images", "shoes_bags_cosmetics",
)

# Base product type (as it appears in the description, e.g. "OLIVE RUNNING
# SNEAKERS" contains "RUNNING SNEAKERS") -> image filename. Ordered so more
# specific names are checked before shorter ones that could be substrings
# of each other (none currently overlap, but keep this ordering habit).
IMAGE_FILENAME_MAP = {
    # Shoes
    "RUNNING SNEAKERS": "running_sneakers.jpg",
    "HIGH-TOP SNEAKERS": "high_top_sneakers.jpg",
    "CANVAS SNEAKERS": "canvas_sneakers.jpg",
    "SLIP-ON SNEAKERS": "slip_on_sneakers.jpg",
    "LEATHER LOAFERS": "leather_loafers.jpg",
    "ANKLE BOOTS": "ankle_boots.jpg",
    "CHELSEA BOOTS": "chelsea_boots.jpg",
    "COMBAT BOOTS": "combat_boots.jpg",
    "STRAPPY SANDALS": "strappy_sandals.jpg",
    "FLIP FLOPS": "flip_flops.jpg",
    "FORMAL OXFORDS": "formal_oxfords.jpg",
    "ESPADRILLES": "espadrilles.jpg",
    "PLATFORM HEELS": "platform_heels.jpg",
    "BALLET FLATS": "ballet_flats.jpg",
    # Bags
    "TOTE BAG": "tote_bag.jpg",
    "CANVAS BACKPACK": "canvas_backpack.jpg",
    "LEATHER BACKPACK": "leather_backpack.jpg",
    "CROSSBODY BAG": "crossbody_bag.jpg",
    "EVENING CLUTCH": "evening_clutch.jpg",
    "LAPTOP BAG": "laptop_bag.jpg",
    "WEEKEND DUFFEL": "weekend_duffel.jpg",
    "MESSENGER BAG": "messenger_bag.jpg",
    "MINI HANDBAG": "mini_handbag.jpg",
    "TRAVEL SUITCASE": "travel_suitcase.jpg",
    "BUCKET BAG": "bucket_bag.jpg",
    "SLING BAG": "sling_bag.jpg",
    "CARD WALLET": "card_wallet.jpg",
    # Cosmetics
    "MATTE LIPSTICK": "matte_lipstick.jpg",
    "LIQUID FOUNDATION": "liquid_foundation.jpg",
    "EYESHADOW PALETTE": "eyeshadow_palette.jpg",
    "VOLUMIZING MASCARA": "volumizing_mascara.jpg",
    "HYDRATING FACE SERUM": "hydrating_face_serum.jpg",
    "COMPACT POWDER": "compact_powder.jpg",
    "LIP GLOSS": "lip_gloss.jpg",
    "NAIL POLISH SET": "nail_polish_set.jpg",
    "MAKEUP BRUSH SET": "makeup_brush_set.jpg",
    "SETTING SPRAY": "setting_spray.jpg",
    "ROSE PERFUME": "rose_perfume.jpg",
    "BB CREAM": "bb_cream.jpg",
    "HIGHLIGHTER PALETTE": "highlighter_palette.jpg",
    "MICELLAR WATER": "micellar_water.jpg",
    "LIP LINER": "lip_liner.jpg",
}


@functools.lru_cache(maxsize=64)
def _load_b64(filename: str):
    path = os.path.join(_ASSETS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def get_image_b64_for_description(description: str):
    """Return a base64-encoded JPEG string for a product description, or
    None if no real photo exists for this product type (caller should
    fall back to the icon system in that case)."""
    if not description or not isinstance(description, str):
        return None

    text = description.upper()
    for base_name, filename in IMAGE_FILENAME_MAP.items():
        if base_name in text:
            return _load_b64(filename)
    return None
