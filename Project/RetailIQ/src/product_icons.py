"""
RetailIQ - Product Icon Module

The dataset has no product photos, only free-text Descriptions
(e.g. "WHITE HANGING HEART T-LIGHT HOLDER"). This module maps keywords
found in a Description to a representative emoji icon, so product
listings are easier to visually scan than a plain text table -
without inventing images that don't exist in the data.
"""

import re

# Ordered so more specific keywords are checked before generic ones.
KEYWORD_ICONS = [
    ("CHRISTMAS", "🎄"), ("XMAS", "🎄"), ("SANTA", "🎅"),
    ("HEART", "❤️"), ("LOVE", "💕"),

    # Shoes
    ("SNEAKER", "👟"), ("TRAINER", "👟"), ("RUNNING SHOE", "👟"),
    ("BOOT", "🥾"), ("SANDAL", "👡"), ("HEEL", "👠"), ("LOAFER", "👞"),
    ("OXFORD", "👞"), ("SLIP-ON", "👟"), ("SLIPPER", "🥿"), ("FLIP FLOP", "🩴"),
    ("CANVAS SHOE", "👟"),

    # Bags
    ("BACKPACK", "🎒"), ("TOTE", "👜"), ("CROSSBODY", "👜"),
    ("CLUTCH", "👛"), ("HANDBAG", "👜"), ("DUFFEL", "🎒"),
    ("MESSENGER BAG", "👜"), ("LAPTOP BAG", "💼"), ("TRAVEL BAG", "🧳"),
    ("SUITCASE", "🧳"),

    # Cosmetics
    ("LIPSTICK", "💄"), ("LIP GLOSS", "💋"), ("LIP LINER", "💄"),
    ("FOUNDATION", "🧴"), ("CONCEALER", "🧴"), ("SERUM", "🧴"),
    ("MOISTURIZER", "🧴"), ("SUNSCREEN", "🧴"),
    ("EYESHADOW", "🎨"), ("MASCARA", "👁️"), ("EYELINER", "👁️"),
    ("BLUSH", "🌸"), ("BRONZER", "🌸"), ("COMPACT POWDER", "🎨"),
    ("NAIL POLISH", "💅"), ("MAKEUP BRUSH", "🖌️"), ("SETTING SPRAY", "🧴"),
    ("PERFUME", "🌺"), ("FRAGRANCE", "🌺"),

    ("CANDLE", "🕯️"), ("LIGHT", "💡"), ("LANTERN", "🏮"),
    ("MUG", "☕"), ("CUP", "☕"), ("TEA", "🍵"),
    ("BAG", "👜"), ("PURSE", "👛"),
    ("BOX", "📦"), ("STORAGE", "📦"), ("TIN", "🥫"),
    ("CARD", "🎴"), ("GIFT", "🎁"), ("WRAP", "🎁"),
    ("BOTTLE", "🍾"),
    ("CLOCK", "🕐"), ("WATCH", "⌚"),
    ("FRAME", "🖼️"), ("MIRROR", "🪞"), ("PICTURE", "🖼️"),
    ("PLATE", "🍽️"), ("BOWL", "🥣"), ("KITCHEN", "🍳"),
    ("GARDEN", "🌿"), ("FLOWER", "🌸"), ("PLANT", "🪴"),
    ("BIRD", "🐦"), ("CAT", "🐱"), ("DOG", "🐶"), ("ANIMAL", "🐾"),
    ("BAKING", "🧁"), ("CAKE", "🎂"),
    ("NECKLACE", "📿"), ("JEWEL", "💍"), ("RING", "💍"),
    ("KEY", "🔑"),
    ("BOOK", "📔"), ("NOTEBOOK", "📔"), ("PAPER", "📄"),
    ("UMBRELLA", "☂️"),
    ("STAR", "⭐"),
    ("BALL", "🎾"), ("TOY", "🧸"), ("GAME", "🎲"),
    ("PARTY", "🎉"), ("BALLOON", "🎈"),
    ("BUNTING", "🎏"), ("FLAG", "🚩"),
    ("APRON", "🥻"),
    ("SIGN", "🪧"), ("HOOK", "🪝"),
    ("GLASS", "🥂"),
    ("BASKET", "🧺"),
    ("WALLET", "👛"),
]

DEFAULT_ICON = "🛍️"

_cache = {}


def get_icon_for_description(description):
    """Return a single representative emoji for a product Description."""

    if description is None:
        return DEFAULT_ICON

    text = str(description).upper()

    if text in _cache:
        return _cache[text]

    icon = DEFAULT_ICON
    for keyword, emoji in KEYWORD_ICONS:
        if re.search(rf"\b{re.escape(keyword)}", text):
            icon = emoji
            break

    _cache[text] = icon
    return icon
