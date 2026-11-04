"""Builds the website's class images and the Battle Bundles banner.

    python3 tools/grade-art.py

Reads Cameron's originals from ~/Documents/BattleTown Art (never changed)
and writes graded copies into assets/img/. The grade is a "cinematic
shader" pass: contrast curve, saturation, warm/teal split tone, bloom
on bright lights, a light leak in the class accent colour, vignette and
sharpening. Re-run after swapping a pick below.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.expanduser("~/Documents/BattleTown Art")
OUT = os.path.join(SITE, "assets", "img")
FONT = os.path.join(SITE, "assets", "fonts", "lilita-one-latin.woff2")

# Class -> (index of the shot in IG POSTS/<Class>/ sorted by name, accent colour).
PICKS = {
    "acrobat": (3, "#E0499E"), "alchemist": (0, "#9ACD32"), "assassin": (3, "#C77DFF"),
    "berserker": (3, "#FF3B3B"), "duelist": (5, "#FFFFFF"), "frostborn": (4, "#7FD4F5"),
    "geomancer": (3, "#A855F7"), "guardian": (3, "#B87333"), "knight": (3, "#55FFFF"),
    "lancer": (3, "#D3D47B"), "necromancer": (3, "#9AE69A"), "poseidon": (2, "#39C6A3"),
    "pyromancer": (3, "#FF8C42"), "ranger": (3, "#5FAE5D"), "stormcaller": (1, "#5C7CFA"),
    "warden": (3, "#C9812E"),
}


def hex_rgb(colour):
    colour = colour.lstrip("#")
    return np.array([int(colour[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255


def crop_16_9(im):
    w, h = im.size
    target = int(w * 9 / 16)
    if target <= h:
        top = (h - target) // 2
        return im.crop((0, top, w, top + target))
    width = int(h * 16 / 9)
    left = (w - width) // 2
    return im.crop((left, 0, left + width, h))


def grade(im, accent):
    """The cinematic pass. im is RGB; returns RGB."""
    a = np.asarray(im).astype(np.float32) / 255
    h, w, _ = a.shape

    # Lift the image a touch, then an S-curve for contrast.
    a = np.clip(a * 1.06 + 0.01, 0, 1)
    s = a * a * (3 - 2 * a)
    a = a * 0.6 + s * 0.4

    # Saturation.
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    a = lum + (a - lum) * 1.28

    # Split tone: teal in the shadows, warm gold in the highlights.
    a += (1 - lum) * np.array([-0.015, 0.01, 0.035], dtype=np.float32)
    a += lum * np.array([0.05, 0.025, -0.03], dtype=np.float32)
    a = np.clip(a, 0, 1)

    # Bloom: blur the bright parts and add them back as glow.
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    bright = np.clip((lum - 0.55) / 0.45, 0, 1) * a
    glow_small = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(w / 160))).astype(np.float32) / 255
    glow_big = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(w / 40))).astype(np.float32) / 255
    glow = glow_small * 0.55 + glow_big * 0.7
    a = 1 - (1 - a) * (1 - np.clip(glow, 0, 1))

    # Light leak in the class accent, falling from the top centre.
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    leak = np.exp(-(((xx - w * 0.5) / (w * 0.42)) ** 2 + ((yy + h * 0.1) / (h * 0.6)) ** 2))[..., None]
    a = 1 - (1 - a) * (1 - leak * hex_rgb(accent) * 0.32)

    # Vignette.
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)[..., None]
    a *= 1 - 0.5 * np.clip(r - 0.35, 0, 1) ** 1.4

    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))


def classes():
    os.makedirs(os.path.join(OUT, "classes"), exist_ok=True)
    for cid, (index, accent) in PICKS.items():
        folder = os.path.join(ART, "IG POSTS", cid.capitalize())
        name = sorted(f for f in os.listdir(folder) if f.endswith(".png"))[index]
        im = crop_16_9(Image.open(os.path.join(folder, name)).convert("RGB"))
        graded = grade(im.resize((1920, 1080), Image.LANCZOS), accent)
        graded.resize((1600, 900), Image.LANCZOS).save(os.path.join(OUT, "classes", cid + ".webp"), quality=82, method=6)
        graded.resize((480, 270), Image.LANCZOS).save(os.path.join(OUT, "classes", cid + "-thumb.webp"), quality=78, method=6)
        print("graded", cid)


def gold_title(text, size, width):
    """Gold block lettering with a stepped extrusion, as an RGBA image."""
    font = ImageFont.truetype(FONT, size)
    box = font.getbbox(text)
    tw, th = box[2] - box[0], box[3] - box[1]
    depth = max(6, size // 9)
    pad = size // 2
    canvas = Image.new("RGBA", (tw + pad * 2, th + pad * 2 + depth), (0, 0, 0, 0))
    ox, oy = pad - box[0], pad - box[1]

    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=font, fill=255)

    # Glow behind everything.
    glow = Image.new("RGBA", canvas.size, (255, 190, 60, 0))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(size / 5)).point(lambda v: int(v * 0.8)))
    canvas = Image.alpha_composite(canvas, glow)

    # Dark outline so the title reads on any background.
    outline = Image.new("RGBA", canvas.size, (30, 16, 2, 255))
    canvas.paste(outline, (0, 0), mask.filter(ImageFilter.MaxFilter(9)))

    # Extrusion: dark brown copies stepping down.
    for step in range(depth, 0, -1):
        shade = Image.new("RGBA", canvas.size, (60 + step * 5, 32 + step * 3, 4, 255))
        shifted = Image.new("L", canvas.size, 0)
        shifted.paste(mask.filter(ImageFilter.MaxFilter(5)), (0, step))
        canvas.paste(shade, (0, 0), shifted)

    # Gradient face.
    face = np.zeros((canvas.size[1], canvas.size[0], 4), dtype=np.uint8)
    t = np.linspace(0, 1, canvas.size[1])[:, None]
    top, mid, bottom = np.array([255, 240, 184]), np.array([255, 205, 80]), np.array([185, 120, 26])
    colour = np.where(t < 0.5, top + (mid - top) * (t / 0.5), mid + (bottom - mid) * ((t - 0.5) / 0.5))
    face[..., :3] = colour[:, None, :].astype(np.uint8)
    face[..., 3] = np.asarray(mask)
    canvas = Image.alpha_composite(canvas, Image.fromarray(face))

    scale = min(1, width / canvas.size[0])
    return canvas.resize((int(canvas.size[0] * scale), int(canvas.size[1] * scale)), Image.LANCZOS)


def bundles_banner():
    """Battle Bundles banner (16:7): the Deals hall blurred into bokeh, the
    Winterfest bundle art feathered into the middle, and a new gold title."""
    width, height = 1600, 700
    base = Image.open(os.path.join(ART, "DEALS", "CATEGORY - DEALS.png")).convert("RGB")
    base = crop_to(base, width, height).filter(ImageFilter.GaussianBlur(16))
    base = Image.fromarray((np.asarray(base).astype(np.float32) * 0.7).astype(np.uint8))
    back = grade(base, "#F5B82E").convert("RGBA")

    # Winterfest art, feathered at the edges so it melts into the hall.
    piece = crop_to(Image.open(os.path.join(ART, "DEALS", "Winterfest.png")).convert("RGB"), 1000, 470)
    feather = Image.new("L", piece.size, 0)
    ImageDraw.Draw(feather).rounded_rectangle([40, 30, piece.width - 40, piece.height - 30], 60, fill=255)
    piece = piece.convert("RGBA")
    piece.putalpha(feather.filter(ImageFilter.GaussianBlur(28)))
    back.alpha_composite(piece, ((width - piece.width) // 2, height - piece.height - 10))

    title = gold_title("BATTLE BUNDLES", 190, 1440)
    back.alpha_composite(title, ((width - title.width) // 2, 10))
    back.convert("RGB").save(os.path.join(OUT, "art", "cat-bundles.webp"), quality=86, method=6)
    print("built cat-bundles")


def crop_to(im, width, height):
    """Scale to cover width x height, then centre-crop."""
    scale = max(width / im.width, height / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - width) // 2, (im.height - height) // 2
    return im.crop((left, top, left + width, top + height))


def social_card():
    """1200x630 link preview: a graded Class Hall, the logo exactly as drawn, the title and address."""
    from PIL import ImageChops
    width, height = 1200, 630
    back = crop_to(Image.open(os.path.join(OUT, "classes", "knight.webp")).convert("RGB"), width, height)
    a = np.asarray(back).astype(np.float32)
    ramp = np.linspace(0.25, 0.85, width)[None, :, None]
    back = Image.fromarray((a * ramp).astype(np.uint8)).convert("RGBA")

    # The logo has a black background; "lighter" keeps every logo pixel as drawn.
    logo = Image.open(os.path.expanduser("~/Documents/BattleTown-Plugin/assets/battletown-logo-4k-transparent.png")).convert("RGB").resize((430, 430), Image.LANCZOS)
    region = back.crop((40, 100, 470, 530)).convert("RGB")
    back.paste(ImageChops.lighter(region, logo), (40, 100))

    title = gold_title("BATTLETOWN", 120, 680)
    back.alpha_composite(title, (480, 140))
    font = ImageFont.truetype(FONT, 40)
    draw = ImageDraw.Draw(back)
    draw.text((510, 330), "16 CLASSES · 4 GAME MODES", font=font, fill=(244, 239, 228, 255))
    draw.text((510, 385), "BUILD YOUR OWN MAPS", font=font, fill=(244, 239, 228, 255))
    draw.rounded_rectangle([505, 455, 1125, 525], 14, outline=(245, 184, 46, 255), width=4, fill=(10, 10, 14, 230))
    draw.text((530, 466), "play.battletown.store", font=ImageFont.truetype(FONT, 44), fill=(255, 212, 92, 255))
    back.convert("RGB").save(os.path.join(OUT, "social-card.jpg"), quality=88)
    print("built social-card")


def favicon():
    icon = Image.open(os.path.join(OUT, "icon-192.png")).convert("RGBA")
    icon.save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    print("built favicon.ico")


if __name__ == "__main__":
    classes()
    bundles_banner()
    social_card()
    favicon()
