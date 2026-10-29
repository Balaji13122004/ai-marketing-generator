import math
import os
import random
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageColor


# Mandatory FS-7 Dimensions
DIMENSIONS_MAP = {
    "tile": (864, 770),
    "banner": (1024, 500),
    "timeline_card": (784, 500),
}


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Parse hex color string (e.g. #3377FF) to RGBA tuple with alpha."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    try:
        r, g, b = ImageColor.getrgb(f"#{hex_color}")
        return (r, g, b, alpha)
    except Exception:
        return (51, 119, 255, alpha)


def get_font(size: int, bold: bool = False):
    """Load a system font if available, otherwise return default."""
    windir = os.environ.get("WINDIR", "C:\\Windows")
    font_candidates = []
    if bold:
        font_candidates = [
            os.path.join(windir, "Fonts", "segoeuib.ttf"),
            os.path.join(windir, "Fonts", "arialbd.ttf"),
            os.path.join(windir, "Fonts", "calibrib.ttf"),
        ]
    else:
        font_candidates = [
            os.path.join(windir, "Fonts", "segoeui.ttf"),
            os.path.join(windir, "Fonts", "arial.ttf"),
            os.path.join(windir, "Fonts", "calibri.ttf"),
        ]
    for p in font_candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def resolve_dimensions(
    image_type: str,
    custom_width: Optional[float] = None,
    custom_height: Optional[float] = None,
    custom_unit: str = "px",
) -> Tuple[int, int]:
    """
    Resolve dimensions according to FS-7 rules:
    - Fixed types: Tile (864x770), Banner (1024x500), Timeline Card (784x500)
    - Custom: converts px, cm, ft using fixed 96 DPI:
        px = cm / 2.54 * 96
        px = ft * 12 / 2.54 * 96
    - Caps output at 4000x4000 and minimum 64x64.
    """
    normalized_type = (image_type or "banner").strip().lower().replace(" ", "_").replace("-", "_")
    if normalized_type in DIMENSIONS_MAP:
        return DIMENSIONS_MAP[normalized_type]

    # Custom handling
    w_px = 1024
    h_px = 500
    try:
        w_val = float(custom_width) if custom_width is not None else 1024.0
        h_val = float(custom_height) if custom_height is not None else 500.0
        unit = (custom_unit or "px").strip().lower()

        if unit == "cm":
            w_px = round(w_val / 2.54 * 96)
            h_px = round(h_val / 2.54 * 96)
        elif unit in ("ft", "feet"):
            w_px = round(w_val * 12 / 2.54 * 96)
            h_px = round(h_val * 12 / 2.54 * 96)
        else:  # default 'px'
            w_px = round(w_val)
            h_px = round(h_val)
    except Exception:
        w_px, h_px = 1024, 500

    # Validation clamps
    w_px = max(64, min(4000, w_px))
    h_px = max(64, min(4000, h_px))
    return (w_px, h_px)


def smart_resize_and_crop(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize and crop an image to target dimensions without distortion (center cover crop).
    """
    img = img.convert("RGBA")
    src_w, src_h = img.size

    # Scale factor to cover target
    scale = max(target_width / src_w, target_height / src_h)
    new_w = max(1, int(math.ceil(src_w * scale)))
    new_h = max(1, int(math.ceil(src_h * scale)))

    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_w - target_width) // 2
    top = (new_h - target_height) // 2
    cropped = resized.crop((left, top, left + target_width, top + target_height))
    return cropped


# -------------------------------------------------------------
# Parametric Template Functions
# -------------------------------------------------------------

def template_diagonal_swoosh(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: Dynamic diagonal accent geometric swoosh and brand pill."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Diagonal accent band on bottom-right corner
    swoosh_h = int(h * 0.40)
    primary_rgba = hex_to_rgba(accent_color, 210)
    secondary_rgba = hex_to_rgba("#FFFFFF", 60)

    # Lower diagonal triangle
    poly_primary = [(int(w * 0.45), h), (w, int(h * 0.35)), (w, h)]
    draw.polygon(poly_primary, fill=primary_rgba)

    # Thin accent highlight border
    poly_accent_line = [(int(w * 0.42), h), (w, int(h * 0.32)), (w, int(h * 0.35)), (int(w * 0.45), h)]
    draw.polygon(poly_accent_line, fill=secondary_rgba)

    # Subtle dot matrix inside the swoosh
    dot_rgba = hex_to_rgba("#FFFFFF", 90)
    for dx in range(int(w * 0.70), w - 20, 24):
        for dy in range(int(h * 0.60), h - 20, 24):
            draw.ellipse([dx, dy, dx + 4, dy + 4], fill=dot_rgba)

    # Brand badge pill in upper-left
    badge_label = app_name or "CAMPAIGN"
    font_bold = get_font(max(14, int(h * 0.035)), bold=True)
    draw.rounded_rectangle([24, 24, 24 + len(badge_label) * 11 + 30, 24 + 32], radius=16, fill=hex_to_rgba("#000000", 170), outline=hex_to_rgba(accent_color, 240), width=2)
    draw.text((38, 30), badge_label.upper(), fill=(255, 255, 255, 240), font=font_bold)

    # Headline text in bottom-left if provided
    if headline_text:
        head_font = get_font(max(16, int(h * 0.045)), bold=True)
        txt = headline_text[:40] + ("..." if len(headline_text) > 40 else "")
        draw.rounded_rectangle([24, h - 58, 24 + len(txt) * 10 + 24, h - 18], radius=8, fill=hex_to_rgba("#000000", 160))
        draw.text((34, h - 52), txt, fill=(255, 255, 255, 245), font=head_font)

    return Image.alpha_composite(photo, overlay)


def template_dot_grid_corner(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: High-tech dot matrix grid, framing corners and lower info band."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top-right 6x6 dot grid
    grid_start_x = w - 160
    grid_start_y = 24
    dot_color = hex_to_rgba(accent_color, 190)
    for row in range(5):
        for col in range(6):
            cx = grid_start_x + col * 22
            cy = grid_start_y + row * 22
            draw.ellipse([cx, cy, cx + 5, cy + 5], fill=dot_color)

    # Corner framing brackets
    bracket_len = 36
    bracket_rgba = hex_to_rgba(accent_color, 240)
    draw.line([(24, 24), (24 + bracket_len, 24)], fill=bracket_rgba, width=3)
    draw.line([(24, 24), (24, 24 + bracket_len)], fill=bracket_rgba, width=3)

    # Bottom bar with gradient look
    bar_h = max(44, int(h * 0.12))
    draw.rectangle([0, h - bar_h, w, h], fill=hex_to_rgba("#111827", 215))
    draw.rectangle([0, h - bar_h, w, h - bar_h + 3], fill=hex_to_rgba(accent_color, 255))

    # App tag & headline
    brand_text = (app_name or "SPOTLIGHT").upper()
    font_bold = get_font(max(13, int(h * 0.032)), bold=True)
    draw.text((24, h - bar_h + 12), brand_text, fill=hex_to_rgba(accent_color, 255), font=font_bold)

    sub_text = headline_text[:50] if headline_text else "AI Marketing Creative"
    font_normal = get_font(max(12, int(h * 0.028)), bold=False)
    draw.text((24 + len(brand_text) * 11 + 20, h - bar_h + 13), f"•  {sub_text}", fill=(240, 240, 240, 220), font=font_normal)

    return Image.alpha_composite(photo, overlay)


def template_color_band_bottom(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: Bold lower third accent banner with modern typography zone."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Lower 28% gradient-style band
    band_h = max(70, int(h * 0.26))
    top_y = h - band_h

    # Semi-transparent dark backing
    draw.rectangle([0, top_y, w, h], fill=hex_to_rgba("#0F172A", 225))
    # Vibrant accent stripe
    draw.rectangle([0, top_y, w, top_y + 4], fill=hex_to_rgba(accent_color, 255))

    # Decorative angled tag on the right
    tag_w = int(w * 0.28)
    draw.polygon([(w - tag_w, top_y), (w, top_y), (w, h), (w - tag_w + 30, h)], fill=hex_to_rgba(accent_color, 180))

    # Modern Brand & headline text
    brand_font = get_font(max(14, int(h * 0.036)), bold=True)
    draw.text((28, top_y + 12), (app_name or "FEATURED").upper(), fill=hex_to_rgba(accent_color, 255), font=brand_font)

    text_to_show = headline_text[:65] if headline_text else "Crafted with AI Image Generator"
    head_font = get_font(max(16, int(h * 0.042)), bold=False)
    draw.text((28, top_y + 36), text_to_show, fill=(255, 255, 255, 240), font=head_font)

    return Image.alpha_composite(photo, overlay)


def template_framing_border(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: Sleek double-line framing border with floating pill badge."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    inset = 18
    # Outer thin border
    draw.rectangle([inset, inset, w - inset, h - inset], outline=hex_to_rgba("#FFFFFF", 80), width=1)
    # Inner border with accent color
    draw.rectangle([inset + 6, inset + 6, w - inset - 6, h - inset - 6], outline=hex_to_rgba(accent_color, 170), width=2)

    # Accent corner tabs
    c_len = 20
    draw.line([(inset + 3, inset + 3), (inset + 3 + c_len, inset + 3)], fill=hex_to_rgba(accent_color, 255), width=3)
    draw.line([(inset + 3, inset + 3), (inset + 3, inset + 3 + c_len)], fill=hex_to_rgba(accent_color, 255), width=3)

    draw.line([(w - inset - 3, h - inset - 3), (w - inset - 3 - c_len, h - inset - 3)], fill=hex_to_rgba(accent_color, 255), width=3)
    draw.line([(w - inset - 3, h - inset - 3), (w - inset - 3, h - inset - 3 - c_len)], fill=hex_to_rgba(accent_color, 255), width=3)

    # Floating top-left badge
    brand_font = get_font(max(13, int(h * 0.032)), bold=True)
    tag_text = app_name or "BRANDED CONTENT"
    draw.rounded_rectangle([inset + 16, inset + 16, inset + 16 + len(tag_text) * 10 + 26, inset + 16 + 28], radius=14, fill=hex_to_rgba("#1E293B", 200), outline=hex_to_rgba(accent_color, 220), width=1)
    draw.ellipse([inset + 24, inset + 25, inset + 32, inset + 33], fill=hex_to_rgba(accent_color, 255))
    draw.text((inset + 38, inset + 20), tag_text.upper(), fill=(255, 255, 255, 230), font=brand_font)

    return Image.alpha_composite(photo, overlay)


def template_gradient_fade(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: Elegant vertical vignette gradient with typography card."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Side accent bar on the left
    stripe_w = max(8, int(w * 0.015))
    draw.rectangle([0, 0, stripe_w, h], fill=hex_to_rgba(accent_color, 255))

    # Bottom left subtle dark gradient backing
    card_w = min(int(w * 0.65), 520)
    card_h = max(65, int(h * 0.22))
    card_x = stripe_w + 16
    card_y = h - card_h - 16

    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=12, fill=hex_to_rgba("#0B132B", 200), outline=hex_to_rgba("#FFFFFF", 40), width=1)

    brand_font = get_font(max(12, int(h * 0.03)), bold=True)
    draw.text((card_x + 16, card_y + 12), (app_name or "CREATIVE").upper(), fill=hex_to_rgba(accent_color, 255), font=brand_font)

    txt = headline_text[:55] if headline_text else "High-Impact Visual Asset"
    head_font = get_font(max(14, int(h * 0.036)), bold=False)
    draw.text((card_x + 16, card_y + 32), txt, fill=(245, 245, 245, 240), font=head_font)

    return Image.alpha_composite(photo, overlay)


def template_duotone_accent(
    photo: Image.Image,
    accent_color: str = "#3377FF",
    pattern_style: str = "default",
    headline_text: str = "",
    app_name: str = "",
) -> Image.Image:
    """Parametric Template: Modern side ribbon with chevron/geometric accents."""
    w, h = photo.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Vertical side ribbon
    ribbon_w = max(40, int(w * 0.06))
    draw.rectangle([0, 0, ribbon_w, h], fill=hex_to_rgba(accent_color, 190))
    draw.line([(ribbon_w, 0), (ribbon_w, h)], fill=hex_to_rgba("#FFFFFF", 120), width=2)

    # Modern chevron accents down the ribbon
    step = 40
    for y in range(30, h - 30, step):
        pts = [(12, y), (ribbon_w // 2, y + 8), (ribbon_w - 12, y)]
        draw.line(pts, fill=(255, 255, 255, 140), width=2)

    # Bottom pill badge
    badge_label = app_name or "PROMO"
    font_bold = get_font(max(13, int(h * 0.032)), bold=True)
    draw.rounded_rectangle([ribbon_w + 16, h - 48, ribbon_w + 16 + len(badge_label) * 11 + 24, h - 16], radius=8, fill=hex_to_rgba("#000000", 190), outline=hex_to_rgba(accent_color, 230), width=1)
    draw.text((ribbon_w + 26, h - 42), badge_label.upper(), fill=(255, 255, 255, 240), font=font_bold)

    return Image.alpha_composite(photo, overlay)


# Registered templates map
TEMPLATES = {
    "diagonal_swoosh": template_diagonal_swoosh,
    "dot_grid_corner": template_dot_grid_corner,
    "color_band_bottom": template_color_band_bottom,
    "framing_border": template_framing_border,
    "gradient_fade": template_gradient_fade,
    "duotone_accent": template_duotone_accent,
}

TEMPLATE_KEYS = list(TEMPLATES.keys())


def apply_template(
    photo: Image.Image,
    target_width: int,
    target_height: int,
    template_name: Optional[str] = None,
    accent_color: str = "#3377FF",
    headline_text: str = "",
    app_name: str = "",
) -> Tuple[Image.Image, str]:
    """
    Resizes/crops photo to exact target dimensions and applies the chosen (or selected) parametric template.
    Returns: (composited_image, template_name_used)
    """
    # 1. Resize and crop cleanly to exact target pixel dimensions
    fitted_photo = smart_resize_and_crop(photo, target_width, target_height)

    # 2. Pick template
    if not template_name or template_name not in TEMPLATES:
        template_name = random.choice(TEMPLATE_KEYS)

    renderer = TEMPLATES[template_name]
    composited = renderer(
        fitted_photo,
        accent_color=accent_color,
        headline_text=headline_text,
        app_name=app_name,
    )
    return composited.convert("RGB"), template_name
