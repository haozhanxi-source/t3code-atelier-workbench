#!/usr/bin/env python3
"""Build & validate the 'Atelier Workbench' (砚纸精工) dual-mode theme for T3 Code.

Design pillars (evolving Claude's Editorial Warmth into a precision bilingual workbench):
1. Tri-Voice Typography:
   - Embedded Newsreader 500 WOFF2 (zero remote URLs) + Noto Serif CJK SC / Songti SC for headings & quotes
   - Inter Variable + PingFang SC / HarmonyOS Sans SC / Noto Sans CJK SC for high-clarity workbench body
   - Embedded IBM Plex Mono 400 WOFF2 for code & tabular figures
2. Dual-Mode Warm Neutrals (WCAG AA contrast verified):
   - Dark (夜读胡桃炭墨): deep walnut charcoal (#181614) avoiding muddy mid-grey, layered with
     4K subtle warm grain wallpaper + 1px specular top borders.
   - Light (白昼馆藏霜纸): museum ivory archival paper (#f8f5ef) + deep ink (#1e1b18) + terracotta (#b85636).
3. Mobile-first + Desktop Precision:
   - ~72ch editorial reading measure on wide screens, tailored padding & scrolling for Z Fold7 Chrome Web.
"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import re
import shutil
import urllib.parse
import urllib.request
from typing import Any

import numpy as np
from PIL import Image

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
THEME_ID = "atelier-workbench"
OUT_DIR = REPO_ROOT
FONTS_DIR = OUT_DIR / "fonts"
T3_THEMES_DIR = pathlib.Path(os.environ.get("T3CODE_HOME", pathlib.Path.home() / ".t3")) / "userdata" / "themes"

MAX_THEME_CSS_CHARS = 50_000
FETCHES_BY_STRING_RE = re.compile(r"image-set\(|\bsrc\(", re.IGNORECASE)
URL_NOT_LOCAL_RE = re.compile(r'url\((?![ \t\n\f\r]*["\']?(?:data:|#))', re.IGNORECASE)
AT_IMPORT_RE = re.compile(r"@import", re.IGNORECASE)

GOOGLE_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
SUBSET_CHARS = "".join(chr(c) for c in range(0x20, 0x7F)) + "“”‘’—–…·•°±×÷©®™"


def _srgb_channel(c: int) -> float:
    v = c / 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    def lum(h: str) -> float:
        s = h.lstrip("#")
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return 0.2126 * _srgb_channel(r) + 0.7152 * _srgb_channel(g) + 0.0722 * _srgb_channel(b)

    la, lb = lum(hex_a), lum(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def fetch_subset_woff2(filename: str, family_spec: str) -> bytes:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    cached = FONTS_DIR / filename
    if cached.is_file() and cached.stat().st_size > 1024:
        raw = cached.read_bytes()
        if raw[:4] == b"wOF2":
            return raw

    q = urllib.parse.quote(SUBSET_CHARS)
    css_url = f"https://fonts.googleapis.com/css2?family={family_spec}&text={q}&display=swap"
    css = urllib.request.urlopen(
        urllib.request.Request(css_url, headers={"User-Agent": GOOGLE_UA}),
        timeout=20,
    ).read().decode("utf-8")
    m = re.search(r"url\((https://[^)]+)\)", css)
    if not m:
        raise RuntimeError(f"Could not find WOFF2 URL for {family_spec}")
    raw = urllib.request.urlopen(
        urllib.request.Request(m.group(1), headers={"User-Agent": GOOGLE_UA}),
        timeout=20,
    ).read()
    if raw[:4] != b"wOF2":
        raise RuntimeError(f"Downloaded font for {family_spec} is not WOFF2 (magic={raw[:4]!r})")
    cached.write_bytes(raw)
    return raw


def generate_walnut_paper_wallpaper(output_path: pathlib.Path, width: int = 2560, height: int = 1440) -> None:
    """Generate a 2.5K/4K-grade dark walnut archival paper wallpaper with warm lamp diffusion & fine grain."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261123)

    y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    x = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]

    # Base deep walnut charcoal gradient (#1a1715 top-left -> #151311 bottom-right)
    base_r = 24.5 - 3.5 * y - 1.5 * x
    base_g = 22.0 - 3.2 * y - 1.4 * x
    base_b = 20.0 - 3.0 * y - 1.2 * x

    # Soft desk-lamp terracotta/amber ambient diffusion in upper-right corner (very restrained)
    d1 = ((x - 0.86) / 0.56) ** 2 + ((y - 0.04) / 0.44) ** 2
    lamp = np.exp(-d1 * 1.45)
    base_r += lamp * 15.5
    base_g += lamp * 9.0
    base_b += lamp * 6.0

    # Subtle bronze/sage secondary balance glow in lower-left
    d2 = ((x - 0.14) / 0.55) ** 2 + ((y - 0.96) / 0.48) ** 2
    glow2 = np.exp(-d2 * 1.6)
    base_r += glow2 * 5.0
    base_g += glow2 * 5.8
    base_b += glow2 * 5.2

    # Gentle editorial vignette for focus
    dv = ((x - 0.5) * 1.15) ** 2 + ((y - 0.5) * 1.15) ** 2
    vignette = np.clip(1.0 - dv * 0.22, 0.80, 1.0)
    base_r *= vignette
    base_g *= vignette
    base_b *= vignette

    # Fine archival cotton-paper fiber + film micro-grain (eliminates 8-bit gradient banding on OLED)
    fine_grain = rng.normal(0.0, 1.85, size=(height, width)).astype(np.float32)
    # Faint horizontal laid-paper fiber texture (low-frequency)
    h_fibers = rng.normal(0.0, 0.55, size=(height, 1)).astype(np.float32)
    tex = fine_grain + h_fibers

    rgb = np.stack(
        [
            np.clip(base_r + tex, 0, 255),
            np.clip(base_g + tex * 0.96, 0, 255),
            np.clip(base_b + tex * 0.92, 0, 255),
        ],
        axis=-1,
    ).astype(np.uint8)

    img = Image.fromarray(rgb, mode="RGB")
    img.save(output_path, format="WEBP", quality=96, method=6)


def build_palettes() -> tuple[dict[str, str], dict[str, str]]:
    """Return WCAG-verified (dark_colors, light_colors) covering all T3 Code roles."""
    dark = {
        "canvas": "#181614",
        "chrome": "#141210",
        "toolbar": "#181614",
        "toolbarForeground": "#ebe5db",
        "toolbarBorder": "#2c2824",
        "toolbarControl": "#23201c",
        "toolbarControlForeground": "#d8d0c4",
        "toolbarControlHover": "#2d2924",
        "surface": "#211e1b",
        "surfaceRaised": "#292521",
        "surfaceOverlay": "#2e2924",
        "text": "#ebe5db",
        "textMuted": "#9e9589",
        "border": "#2e2a25",
        "input": "#24211d",
        "focus": "#d48262",
        "accent": "#d48262",
        "accentForeground": "#181310",
        "secondary": "#282420",
        "secondaryForeground": "#e5ded3",
        "muted": "#23201c",
        "mutedForeground": "#9e9589",
        "placeholder": "#7d756b",
        "secondaryLabel": "#b6ada0",
        "iconMuted": "#968d81",
        "error": "#ffa6a0",
        "errorForeground": "#ffc2bc",
        "errorSurface": "#331e1d",
        "warning": "#d9a559",
        "warningForeground": "#f2c987",
        "warningSurface": "#33281a",
        "update": "#7aa88f",
        "updateForeground": "#a9d6bd",
        "updateSurface": "#1d2b23",
        "accentSurface": "#34241e",
        "accentSurfaceForeground": "#f0c4b1",
        "messageSurface": "#24211d",
        "messageForeground": "#efe9df",
        "messageAction": "#2b2722",
        "messageActionForeground": "#d8d0c4",
        "messageActionHover": "#36302a",
        "codeBackground": "#13110f",
        "codeForeground": "#e5dacb",
        "searchMatchBackground": "#423322",
        "searchMatchForeground": "#f4e6d2",
        "searchMatchActiveBackground": "#d48262",
        "searchMatchActiveForeground": "#181310",
        "sidebar": "#13110f",
        "sidebarForeground": "#ded7cc",
        "sidebarMutedForeground": "#8e8579",
        "sidebarControlSurface": "#1f1c19",
        "sidebarRowHover": "#1e1b18",
        "sidebarRowActive": "#27231f",
        "sidebarRowSelected": "#2b2520",
        "sidebarBorder": "#26221e",
        "terminalBackground": "#12100e",
        "terminalForeground": "#e5ded3",
        "terminalCursor": "#d48262",
        "terminalSelection": "#3d2c24",
        "terminalScrollbar": "#38332d",
        "terminalScrollbarHover": "#574f46",
    }

    light = {
        "canvas": "#f8f5ef",
        "chrome": "#f1ece2",
        "toolbar": "#f8f5ef",
        "toolbarForeground": "#1e1b18",
        "toolbarBorder": "#e3dbcd",
        "toolbarControl": "#efeae0",
        "toolbarControlForeground": "#3a342d",
        "toolbarControlHover": "#e6dfd2",
        "surface": "#fffdf9",
        "surfaceRaised": "#ffffff",
        "surfaceOverlay": "#fffdf8",
        "text": "#1e1b18",
        "textMuted": "#655c52",
        "border": "#e2dacb",
        "input": "#fffdf9",
        "focus": "#b85636",
        "accent": "#b85636",
        "accentForeground": "#fffaf5",
        "secondary": "#efe9de",
        "secondaryForeground": "#27231e",
        "muted": "#f0eae0",
        "mutedForeground": "#655c52",
        "placeholder": "#857b6f",
        "secondaryLabel": "#544c43",
        "iconMuted": "#6f655a",
        "error": "#8e2e2b",
        "errorForeground": "#842c29",
        "errorSurface": "#f9e7e6",
        "warning": "#9f6b1f",
        "warningForeground": "#74470a",
        "warningSurface": "#f8efe0",
        "update": "#3d7a5b",
        "updateForeground": "#245a40",
        "updateSurface": "#e6f2ec",
        "accentSurface": "#f6e7e0",
        "accentSurfaceForeground": "#7f341c",
        "messageSurface": "#fffdf9",
        "messageForeground": "#1e1b18",
        "messageAction": "#efeae0",
        "messageActionForeground": "#3a342d",
        "messageActionHover": "#e5ddd0",
        "codeBackground": "#f1ebe0",
        "codeForeground": "#2a251f",
        "searchMatchBackground": "#f3dfbe",
        "searchMatchForeground": "#2b2113",
        "searchMatchActiveBackground": "#b85636",
        "searchMatchActiveForeground": "#fffaf5",
        "sidebar": "#f1ece2",
        "sidebarForeground": "#292520",
        "sidebarMutedForeground": "#6b6257",
        "sidebarControlSurface": "#e8e1d4",
        "sidebarRowHover": "#e8e1d5",
        "sidebarRowActive": "#fffdf9",
        "sidebarRowSelected": "#fffdf9",
        "sidebarBorder": "#e0d7c7",
        "terminalBackground": "#f3eee4",
        "terminalForeground": "#231f1b",
        "terminalCursor": "#b85636",
        "terminalSelection": "#ecd6cb",
        "terminalScrollbar": "#d3c8b7",
        "terminalScrollbarHover": "#b3a591",
    }

    # Verify key contrast ratios (WCAG AA >= 4.5 for normal text)
    checks = [
        ("dark text/canvas", dark["text"], dark["canvas"], 4.5),
        ("dark textMuted/canvas", dark["textMuted"], dark["canvas"], 4.5),
        ("dark accentFg/accent", dark["accentForeground"], dark["accent"], 4.5),
        ("dark msgFg/msgSurface", dark["messageForeground"], dark["messageSurface"], 4.5),
        ("dark codeFg/codeBg", dark["codeForeground"], dark["codeBackground"], 4.5),
        ("light text/canvas", light["text"], light["canvas"], 4.5),
        ("light textMuted/canvas", light["textMuted"], light["canvas"], 4.5),
        ("light accentFg/accent", light["accentForeground"], light["accent"], 4.5),
        ("light msgFg/msgSurface", light["messageForeground"], light["messageSurface"], 4.5),
        ("light codeFg/codeBg", light["codeForeground"], light["codeBackground"], 4.5),
    ]
    # T3 uses every "*Foreground" role as TEXT drawn on its paired surface (not on the solid accent colour),
    # e.g. the red error alert. Verify all such pairs so alert/toast text can never go unreadable again.
    surface_pairs = [
        ("errorForeground", "errorSurface"),
        ("warningForeground", "warningSurface"),
        ("updateForeground", "updateSurface"),
        ("accentSurfaceForeground", "accentSurface"),
        ("secondaryForeground", "secondary"),
        ("mutedForeground", "muted"),
        ("sidebarForeground", "sidebar"),
        ("toolbarForeground", "toolbar"),
        ("toolbarControlForeground", "toolbarControl"),
        ("messageActionForeground", "messageAction"),
        ("searchMatchForeground", "searchMatchBackground"),
        ("searchMatchActiveForeground", "searchMatchActiveBackground"),
        ("terminalForeground", "terminalBackground"),
    ]
    for mode, pal in (("dark", dark), ("light", light)):
        for fg_key, bg_key in surface_pairs:
            checks.append((f"{mode} {fg_key}/{bg_key}", pal[fg_key], pal[bg_key], 4.5))
    # Give compact error labels and details additional contrast.
    for appearance, palette in (("dark", dark), ("light", light)):
        for foreground, background in (
            ("error", "canvas"),
            ("error", "surfaceRaised"),
            ("errorForeground", "errorSurface"),
        ):
            checks.append((f"{appearance} {foreground}/{background}", palette[foreground], palette[background], 7))
    for label, fg, bg, minimum in checks:
        ratio = contrast_ratio(fg, bg)
        if ratio < minimum:
            raise ValueError(f"Contrast check failed for {label}: {ratio:.2f} < {minimum}")
    return dark, light


def build_theme_css(newsreader_b64: str, ibm_mono_b64: str) -> str:
    """Build custom T3 Code theme CSS adhering strictly to stable hooks and CSS guard."""
    # Base64-encoded seamless inline SVG archival paper texture for Light Mode (avoids inner url(%23n))
    light_svg_raw = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>"
        "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='2' "
        "stitchTiles='stitch'/></filter>"
        "<rect width='100%' height='100%' filter='url(#n)' opacity='0.03'/>"
        "</svg>"
    )
    light_paper_svg = "data:image/svg+xml;base64," + base64.b64encode(light_svg_raw.encode("utf-8")).decode("ascii")
    dark_svg_raw = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>"
        "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' "
        "stitchTiles='stitch'/></filter>"
        "<rect width='100%' height='100%' filter='url(#n)' opacity='0.04'/>"
        "</svg>"
    )
    dark_paper_svg = "data:image/svg+xml;base64," + base64.b64encode(dark_svg_raw.encode("utf-8")).decode("ascii")

    css = f"""/* Atelier Workbench · 砚纸精工 (Dual-Mode Editorial Workbench) */
@font-face {{
  font-family: "Atelier Newsreader";
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url("data:font/woff2;base64,{newsreader_b64}") format("woff2");
}}
@font-face {{
  font-family: "Atelier Plex Mono";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("data:font/woff2;base64,{ibm_mono_b64}") format("woff2");
}}

:root {{
  --atelier-serif: "Atelier Newsreader", "Newsreader", Georgia,
    "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "STSong", serif;
  --atelier-sans: "Inter Variable", "Inter", -apple-system, BlinkMacSystemFont,
    "PingFang SC", "HarmonyOS Sans SC", "MiSans", "Noto Sans CJK SC", "Microsoft YaHei UI", sans-serif;
  --atelier-mono: "Atelier Plex Mono", "IBM Plex Mono", "Maple Mono",
    "JetBrains Mono", "SF Mono", ui-monospace, monospace;
  --font-sans: var(--atelier-sans);
  --font-mono: var(--atelier-mono);
  font-synthesis-weight: none;
}}

/* Refined 1.5px architectural icon stroke */
svg.lucide {{
  stroke-width: 1.5 !important;
  stroke-linecap: round;
  stroke-linejoin: round;
}}

/* ===================== DARK MODE: 夜读胡桃炭墨 ===================== */
.dark [data-workspace-area="conversation"] {{
  background-color: #181614 !important;
  background-image:
    var(--theme-background-image, radial-gradient(920px 480px at 86% 2%, rgba(212, 130, 98, 0.085), transparent 62%)),
    radial-gradient(680px 420px at 14% 98%, rgba(122, 168, 143, 0.04), transparent 60%),
    url("{dark_paper_svg}") !important;
  background-position: center center, center center, 0 0 !important;
  background-size: cover, cover, 180px 180px !important;
  background-repeat: no-repeat, no-repeat, repeat !important;
}}

.dark [data-slot="sidebar-inner"] {{
  background: linear-gradient(180deg, rgba(20, 18, 16, 0.96) 0%, rgba(17, 15, 13, 0.98) 100%) !important;
  border-right: 1px solid rgba(238, 226, 210, 0.08) !important;
}}

.dark [data-chat-header] {{
  background: rgba(24, 22, 20, 0.78) !important;
  backdrop-filter: blur(16px) saturate(125%) !important;
  -webkit-backdrop-filter: blur(16px) saturate(125%) !important;
  border-bottom: 1px solid rgba(238, 226, 210, 0.075) !important;
}}

.dark [data-thread-item] {{
  border-radius: 8px !important;
  transition: background-color 140ms ease, color 140ms ease, box-shadow 140ms ease;
}}

.dark [data-thread-item][data-active="true"],
.dark [data-thread-item][aria-current="page"] {{
  background: rgba(212, 130, 98, 0.11) !important;
  box-shadow: inset 2px 0 0 #d48262, inset 0 1px 0 rgba(255, 244, 230, 0.06) !important;
}}

.dark [data-user-message-bubble] {{
  background: linear-gradient(180deg, rgba(41, 37, 33, 0.92) 0%, rgba(33, 30, 27, 0.94) 100%) !important;
  border: 1px solid rgba(238, 226, 210, 0.12) !important;
  box-shadow: inset 0 1px 0 rgba(255, 245, 232, 0.07), 0 4px 16px rgba(0, 0, 0, 0.22) !important;
  border-radius: 13px !important;
}}

.dark [data-slot="composer-host"] {{
  background: rgba(34, 30, 26, 0.90) !important;
  backdrop-filter: blur(18px) saturate(130%) !important;
  -webkit-backdrop-filter: blur(18px) saturate(130%) !important;
  border: 1px solid rgba(238, 226, 210, 0.15) !important;
  box-shadow: inset 0 1px 0 rgba(255, 244, 230, 0.08), 0 10px 30px rgba(0, 0, 0, 0.34) !important;
  border-radius: 15px !important;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}}

.dark [data-slot="composer-host"]:focus-within {{
  border-color: rgba(212, 130, 98, 0.52) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 244, 230, 0.09),
    0 0 0 3px rgba(212, 130, 98, 0.14),
    0 12px 32px rgba(0, 0, 0, 0.38) !important;
}}

.dark .chat-markdown-codeblock {{
  background: rgba(18, 16, 14, 0.92) !important;
  border: 1px solid rgba(238, 226, 210, 0.11) !important;
  border-left: 2px solid rgba(212, 130, 98, 0.50) !important;
  border-radius: 10px !important;
  box-shadow: inset 0 1px 0 rgba(255, 244, 230, 0.04) !important;
}}

.dark .chat-markdown blockquote {{
  border-left: 2px solid #d48262 !important;
  background: rgba(212, 130, 98, 0.06) !important;
  color: #cfc5b8 !important;
}}

.dark [data-slot="dialog-popup"],
.dark [data-slot="popover-popup"],
.dark [data-slot="menu-popup"] {{
  background: rgba(34, 30, 26, 0.96) !important;
  backdrop-filter: blur(18px) !important;
  border: 1px solid rgba(238, 226, 210, 0.14) !important;
  box-shadow: inset 0 1px 0 rgba(255, 244, 230, 0.07), 0 18px 42px rgba(0, 0, 0, 0.48) !important;
}}

/* ===================== LIGHT MODE: 白昼馆藏霜纸 ===================== */
:root:not(.dark) [data-workspace-area="conversation"] {{
  background-color: #f8f5ef !important;
  background-image:
    radial-gradient(900px 440px at 88% -6%, rgba(184, 86, 54, 0.055), transparent 62%),
    radial-gradient(720px 380px at 12% 106%, rgba(61, 122, 91, 0.04), transparent 62%),
    url("{light_paper_svg}") !important;
  background-repeat: no-repeat, no-repeat, repeat !important;
}}

:root:not(.dark) [data-slot="sidebar-inner"] {{
  background: linear-gradient(180deg, #f2ede3 0%, #ede7dc 100%) !important;
  border-right: 1px solid #dfd7c8 !important;
}}

:root:not(.dark) [data-chat-header] {{
  background: rgba(248, 245, 239, 0.84) !important;
  backdrop-filter: blur(16px) saturate(115%) !important;
  -webkit-backdrop-filter: blur(16px) saturate(115%) !important;
  border-bottom: 1px solid #e3dbcd !important;
}}

:root:not(.dark) [data-thread-item] {{
  border-radius: 8px !important;
  transition: background-color 140ms ease, box-shadow 140ms ease;
}}

:root:not(.dark) [data-thread-item][data-active="true"],
:root:not(.dark) [data-thread-item][aria-current="page"] {{
  background: #fffdf9 !important;
  box-shadow: inset 2px 0 0 #b85636, 0 1px 3px rgba(45, 34, 22, 0.06) !important;
}}

:root:not(.dark) [data-user-message-bubble] {{
  background: #fffdf9 !important;
  border: 1px solid #dfd6c6 !important;
  box-shadow: 0 1px 3px rgba(55, 42, 28, 0.055), inset 0 1px 0 #ffffff !important;
  border-radius: 13px !important;
}}

:root:not(.dark) [data-slot="composer-host"] {{
  background: rgba(255, 253, 249, 0.94) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid #d9cfbe !important;
  box-shadow: 0 8px 26px rgba(48, 36, 22, 0.08), inset 0 1px 0 #ffffff !important;
  border-radius: 15px !important;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}}

:root:not(.dark) [data-slot="composer-host"]:focus-within {{
  border-color: rgba(184, 86, 54, 0.55) !important;
  box-shadow: 0 0 0 3px rgba(184, 86, 54, 0.12), 0 10px 28px rgba(48, 36, 22, 0.10) !important;
}}

:root:not(.dark) .chat-markdown-codeblock {{
  background: #f2ece1 !important;
  border: 1px solid #ded5c4 !important;
  border-left: 2px solid rgba(184, 86, 54, 0.55) !important;
  border-radius: 10px !important;
}}

:root:not(.dark) .chat-markdown blockquote {{
  border-left: 2px solid #b85636 !important;
  background: rgba(184, 86, 54, 0.05) !important;
  color: #4f463d !important;
}}

:root:not(.dark) [data-slot="dialog-popup"],
:root:not(.dark) [data-slot="popover-popup"],
:root:not(.dark) [data-slot="menu-popup"] {{
  background: rgba(255, 253, 249, 0.97) !important;
  border: 1px solid #dfd6c6 !important;
  box-shadow: 0 14px 36px rgba(48, 36, 22, 0.12) !important;
}}

/* ===================== TRI-VOICE BILINGUAL TYPOGRAPHY ===================== */
body,
[data-slot="sidebar"],
[data-chat-header],
.composer-tiptap {{
  font-family: var(--atelier-sans) !important;
  font-feature-settings: "kern" 1, "cv02" 1, "cv03" 1;
}}

.chat-markdown {{
  font-family: var(--atelier-sans) !important;
  line-height: 1.72 !important;
  letter-spacing: 0.01em;
  font-feature-settings: "palt" 1, "kern" 1;
  font-size-adjust: from-font;
  overflow-wrap: break-word;
  text-wrap: pretty;
}}

@supports not (font-size-adjust: from-font) {{
  .chat-markdown {{
    line-height: 1.76 !important;
  }}
}}

/* Editorial serif voice for headings & blockquotes */
.chat-markdown h1,
.chat-markdown h2,
.chat-markdown h3 {{
  font-family: var(--atelier-serif) !important;
  font-weight: 500 !important;
  letter-spacing: -0.01em !important;
  line-height: 1.32 !important;
  text-wrap: balance;
  margin-top: 1.45em !important;
  margin-bottom: 0.48em !important;
}}

.chat-markdown h1 {{
  font-size: 1.42rem !important;
}}

.chat-markdown h2 {{
  font-size: 1.22rem !important;
}}

.chat-markdown h3 {{
  font-size: 1.06rem !important;
}}

.chat-markdown p {{
  margin-bottom: 0.85em !important;
}}

.chat-markdown blockquote {{
  font-family: var(--atelier-serif) !important;
  font-style: italic;
  line-height: 1.68 !important;
  padding: 0.45em 0.95em !important;
  border-radius: 0 8px 8px 0 !important;
  margin: 0.95em 0 !important;
}}

/* Keep the final paragraph flush with the sent message bubble's padding. */
[data-user-message-bubble] .chat-markdown {{
  line-height: 1.55 !important;
}}

[data-user-message-bubble] .chat-markdown > p:last-child {{
  margin-block-end: 0 !important;
}}

/* Precision monospace voice for code & inline tokens */
.chat-markdown code,
.chat-markdown pre,
.chat-markdown-codeblock code,
.chat-markdown-codeblock pre {{
  font-family: var(--atelier-mono) !important;
  font-variant-numeric: tabular-nums;
}}

.chat-markdown :not(pre) > code {{
  font-size: 0.86em !important;
  padding: 0.12em 0.42em !important;
  border-radius: 5px !important;
}}

/* Work / tool-call blocks stay calm & low-noise */
[data-timeline-row-kind="work"] {{
  opacity: 0.92;
  transition: opacity 150ms ease;
}}
[data-timeline-row-kind="work"]:hover {{
  opacity: 1;
}}

/* Hairline scrollbars */
::-webkit-scrollbar {{
  width: 6px;
  height: 6px;
}}
::-webkit-scrollbar-track {{
  background: transparent;
}}
::-webkit-scrollbar-thumb {{
  border-radius: 999px;
  background: rgba(158, 149, 137, 0.28);
}}
::-webkit-scrollbar-thumb:hover {{
  background: rgba(212, 130, 98, 0.55);
}}
[data-slot="scroll-area-thumb"] {{
  border-radius: 999px !important;
}}

/* Mobile & Z Fold7 narrow cover-screen ergonomics */
@media (max-width: 640px) {{
  .chat-markdown {{
    line-height: 1.74 !important;
    letter-spacing: 0.012em;
  }}
  [data-user-message-bubble] {{
    border-radius: 12px !important;
  }}
  [data-slot="composer-host"] {{
    border-radius: 13px !important;
  }}
  .chat-markdown-codeblock {{
    border-radius: 8px !important;
    -webkit-overflow-scrolling: touch;
  }}
}}

@media (forced-colors: active) {{
  [data-user-message-bubble],
  [data-slot="composer-host"],
  .chat-markdown-codeblock {{
    border: 1px solid CanvasText !important;
  }}
}}
"""
    return css


def validate_css_guard(css: str) -> None:
    if len(css) > MAX_THEME_CSS_CHARS:
        raise ValueError(f"Theme CSS length {len(css)} exceeds T3 limit {MAX_THEME_CSS_CHARS}")
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", css)
    if AT_IMPORT_RE.search(stripped):
        raise ValueError("CSS guard violation: @import detected")
    if FETCHES_BY_STRING_RE.search(stripped):
        raise ValueError("CSS guard violation: image-set() or src() detected")
    if URL_NOT_LOCAL_RE.search(stripped):
        raise ValueError("CSS guard violation: non-local url() detected")


def write_desktop_sync_helpers() -> None:
    sh_script = """#!/usr/bin/env bash
# One-click sync of Atelier Workbench theme + 4K wallpaper to local macOS/Linux T3 Code Desktop
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${T3CODE_HOME:-$HOME/.t3}/userdata/themes"
mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/atelier-workbench.json" "$TARGET_DIR/atelier-workbench.json"
cp "$SCRIPT_DIR/atelier-workbench.webp" "$TARGET_DIR/atelier-workbench.webp"
echo "Installed Atelier Workbench theme to $TARGET_DIR"
echo "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"
"""
    sh_path = OUT_DIR / "sync-desktop.sh"
    sh_path.write_text(sh_script, encoding="utf-8")
    sh_path.chmod(0o755)

    ps_script = r"""# One-click sync of Atelier Workbench theme + 4K wallpaper to Windows T3 Code Desktop
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$T3Home = if ($env:T3CODE_HOME) { $env:T3CODE_HOME } else { Join-Path $HOME ".t3" }
$TargetDir = Join-Path $T3Home "userdata\themes"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.json") (Join-Path $TargetDir "atelier-workbench.json")
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.webp") (Join-Path $TargetDir "atelier-workbench.webp")
Write-Host "Installed Atelier Workbench theme to $TargetDir"
Write-Host "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"
"""
    (OUT_DIR / "sync-desktop.ps1").write_text(ps_script, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    install = "--install" in __import__("sys").argv
    if install:
        T3_THEMES_DIR.mkdir(parents=True, exist_ok=True)

    newsreader_raw = fetch_subset_woff2("newsreader-500-latin.woff2", "Newsreader:opsz,wght@18,500")
    ibm_mono_raw = fetch_subset_woff2("ibm-plex-mono-400-latin.woff2", "IBM+Plex+Mono:wght@400")

    newsreader_b64 = base64.b64encode(newsreader_raw).decode("ascii")
    ibm_mono_b64 = base64.b64encode(ibm_mono_raw).decode("ascii")

    wallpaper_repo = OUT_DIR / f"{THEME_ID}.webp"
    generate_walnut_paper_wallpaper(wallpaper_repo)
    if install:
        shutil.copy2(wallpaper_repo, T3_THEMES_DIR / f"{THEME_ID}.webp")

    dark_colors, light_colors = build_palettes()
    css = build_theme_css(newsreader_b64, ibm_mono_b64)
    validate_css_guard(css)

    theme_doc: dict[str, Any] = {
        "version": 1,
        "id": THEME_ID,
        "name": "Atelier Workbench · 砚纸精工",
        "appearance": "dark",
        "canvas": dark_colors["canvas"],
        "accent": dark_colors["accent"],
        "colors": dark_colors,
        "variants": {
            "light": light_colors,
        },
        "css": css,
    }

    theme_json_path = OUT_DIR / f"{THEME_ID}.json"
    theme_json_path.write_text(json.dumps(theme_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_desktop_sync_helpers()

    wp_kb = round(wallpaper_repo.stat().st_size / 1024, 1)
    print(f"Built {THEME_ID} successfully:")
    print(f"  CSS chars       : {len(css)} / {MAX_THEME_CSS_CHARS}")
    print(f"  Newsreader WOFF2: {len(newsreader_raw)} bytes (embedded)")
    print(f"  IBM Plex Mono   : {len(ibm_mono_raw)} bytes (embedded)")
    print(f"  4K Wallpaper    : {wp_kb} KiB -> {wallpaper_repo}")
    print(f"  Theme JSON      : {theme_json_path}")


if __name__ == "__main__":
    main()
