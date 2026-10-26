#!/usr/bin/env python3
"""
IconMaker.py - slices one source image into app icons for iOS and Android.
Author: Vladislav Khodkevich

Install:          pip3 install pillow
Run:              python3 IconMaker.py icon.png
All options:      python3 IconMaker.py --help

SOURCE: a square PNG, ideally 1024x1024 or larger. No rounded corners and no
transparent edges: the artwork must fill the whole square. Rounding and masks
are applied by iOS / Android themselves.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw

# Script version: bump it on every update (shown by --version and in the output)
__version__ = "0.1.0"
__author__ = "Vladislav Khodkevich"

# iOS: (idiom, size in pt, scale)
IOS = [
    ("iphone", 20, 2), ("iphone", 20, 3), ("iphone", 29, 2), ("iphone", 29, 3),
    ("iphone", 40, 2), ("iphone", 40, 3), ("iphone", 60, 2), ("iphone", 60, 3),
    ("ipad", 20, 1), ("ipad", 20, 2), ("ipad", 29, 1), ("ipad", 29, 2),
    ("ipad", 40, 1), ("ipad", 40, 2), ("ipad", 76, 1), ("ipad", 76, 2),
    ("ipad", 83.5, 2),
    ("ios-marketing", 1024, 1),                      # App Store
]
# Apple Watch (optional, --watch flag), sizes in px
WATCH = [48, 55, 58, 80, 87, 88, 100, 172, 196, 216, 1024]

# Android
ADAPTIVE = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}  # 108dp
LEGACY = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}        # 48dp
PLAY_STORE = 512
SAFE = 66 / 108   # visible "safe zone" of an adaptive icon (66dp of 108dp)

ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""


def fit(img, px):
    return img.resize((px, px), Image.LANCZOS)


def flatten(img, bg):
    """Removes the alpha channel (the App Store rejects icons with transparency)."""
    base = Image.new("RGB", img.size, bg)
    base.paste(img, mask=img.getchannel("A"))
    return base


def mask(px, shape):
    big = px * 4
    m = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(m)
    if shape == "circle":
        d.ellipse((0, 0, big - 1, big - 1), fill=255)
    else:
        d.rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * 0.2), fill=255)
    return m.resize((px, px), Image.LANCZOS)


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def parse_color(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def px_of(pt, scale):
    return round(pt * scale)


def make_ios(src_rgb, out, watch):
    d = out / "ios" / "AppIcon.appiconset"
    images, done = [], set()
    for idiom, pt, scale in IOS:
        px = px_of(pt, scale)
        name = f"icon-{px}.png"
        if name not in done:
            save(fit(src_rgb, px), d / name)
            done.add(name)
        images.append({"filename": name, "idiom": idiom, "scale": f"{scale}x", "size": f"{pt:g}x{pt:g}"})
    (d / "Contents.json").write_text(
        json.dumps({"images": images, "info": {"author": "xcode", "version": 1}}, indent=2))
    n = len(done)
    if watch:
        for px in WATCH:
            save(fit(src_rgb, px), out / "ios" / "watchos" / f"watch-{px}.png")
        n += len(WATCH)
    return n


def make_android(src, src_rgb, out, fg_path, bg_path, bg_color):
    res = out / "android" / "res"
    n = 0
    # adaptive layers
    fg_src = Image.open(fg_path).convert("RGBA") if fg_path else None
    bg_src = Image.open(bg_path).convert("RGBA") if bg_path else None
    for dpi, px in ADAPTIVE.items():
        if fg_src:
            fg = fit(fg_src, px)
        else:   # whole icon inside the safe zone
            inner = round(px * SAFE)
            fg = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            fg.paste(fit(src, inner), ((px - inner) // 2, (px - inner) // 2))
        bg = fit(bg_src, px) if bg_src else Image.new("RGBA", (px, px), bg_color + (255,))
        save(fg, res / f"mipmap-{dpi}" / "ic_launcher_foreground.png")
        save(bg, res / f"mipmap-{dpi}" / "ic_launcher_background.png")
        n += 2
    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        (res / "mipmap-anydpi-v26").mkdir(parents=True, exist_ok=True)
        (res / "mipmap-anydpi-v26" / name).write_text(ADAPTIVE_XML)
    # legacy (Android < 8): rounded square and circle
    for dpi, px in LEGACY.items():
        for name, shape in (("ic_launcher.png", "rounded"), ("ic_launcher_round.png", "circle")):
            im = fit(src_rgb, px).convert("RGBA")
            im.putalpha(mask(px, shape))
            save(im, res / f"mipmap-{dpi}" / name)
            n += 1
    # Google Play: 512x512, plain square (Google applies the mask)
    save(fit(src, PLAY_STORE), out / "android" / "play_store" / "icon-512.png")
    return n + 1


def main():
    ap = argparse.ArgumentParser(description="Slice one image into iOS/Android app icons")
    ap.add_argument("--version", action="version", version=f"IconMaker {__version__} (author: {__author__})")
    ap.add_argument("source", help="square PNG, ideally >= 1024x1024")
    ap.add_argument("-o", "--out", default="icons_out", help="output folder (default: icons_out)")
    ap.add_argument("--platform", choices=["all", "ios", "android"], default="all")
    ap.add_argument("--bg", help="background color #RRGGBB: backing for the iOS icon and background of the Android adaptive icon. "
                                 "Default: the color of the image corner")
    ap.add_argument("--fg", help="(Android) your own foreground layer, PNG with transparency. "
                                 "The artwork must stay within the central 61%% (safe zone)")
    ap.add_argument("--bgimage", help="(Android) your own background layer instead of a solid color")
    ap.add_argument("--watch", action="store_true", help="also generate Apple Watch icons")
    a = ap.parse_args()

    print(f"IconMaker v{__version__} by {__author__}")
    src = Image.open(a.source).convert("RGBA")
    if src.width != src.height:
        sys.exit(f"Error: the image must be square, got {src.width}x{src.height}")
    if src.width < 1024:
        print(f"Warning: {src.width}px is smaller than 1024, the 1024 icon will be upscaled and blurry")

    if a.bg:
        bg = parse_color(a.bg)
    else:
        r, g, b, al = src.getpixel((3, 3))
        bg = (r, g, b) if al == 255 else (255, 255, 255)
    src_rgb = flatten(src, bg)
    out = Path(a.out)

    if a.platform in ("all", "ios"):
        print(f"iOS:     {make_ios(src_rgb, out, a.watch)} files -> {out / 'ios'}")
    if a.platform in ("all", "android"):
        print(f"Android: {make_android(src, src_rgb, out, a.fg, a.bgimage, bg)} files -> {out / 'android'}")
    print(f"Backing color: #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}")


if __name__ == "__main__":
    main()