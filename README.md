# Atelier Workbench · 砚纸精工 (T3 Code Theme)

A dual-mode (Dark + Light) editorial workbench theme for **[T3 Code](https://t3.codes)**, designed for long-form technical reading, bilingual CJK + Latin typography, and multi-device consistency (Desktop, Web, and Mobile Chrome Web).

## Design Highlights

- **Dual-Mode Warm Neutrals (Zero Harsh Glare)**
  - **Dark (`夜读胡桃炭墨`)**: Deep walnut charcoal (`#181614` / `#13110f`) paired with a 2560×1440 procedural micro-grain archival paper wallpaper (`atelier-workbench.webp`), 1px specular top borders, and warm terracotta accents (`#d48262`).
  - **Light (`白昼馆藏霜纸`)**: Museum ivory archival paper (`#f8f5ef`) with an embedded seamless SVG paper-fiber texture, deep ink text (`#1e1b18`), and cinnabar terracotta accents (`#b85636`).
- **Tri-Voice Bilingual Typography (Zero External Requests)**
  - **Headings & Blockquotes**: Embedded Latin subset of **Newsreader 500** (`WOFF2` base64) paired with `Noto Serif CJK SC` / `Source Han Serif SC` / `Songti SC`.
  - **Workbench Body & UI**: `Inter Variable` paired with `PingFang SC` / `HarmonyOS Sans SC` / `MiSans` / `Noto Sans CJK SC`, tuned with `line-height: 1.72`, `"palt" 1` CJK punctuation kerning, and `font-size-adjust: from-font`.
  - **Code & Tabular Figures**: Embedded **IBM Plex Mono 400** (`WOFF2` base64) with `tabular-nums`.
- **Verified Accessibility & T3 CSS Guard Compliance**
  - All core foreground/surface pairs are verified **WCAG AA (≥ 4.5:1)**, with alert/error surfaces verified **≥ 7.0:1**.
  - Strictly adheres to T3 Code's CSS guard (`< 50,000` chars, zero `@import`, zero remote `url()`, stable `data-*` selectors only).

## Installation

### Option 1: T3 Code CLI (Recommended for Server / Linux / macOS)
```bash
git clone https://github.com/haozhanxi-source/t3code-atelier-workbench.git
cd t3code-atelier-workbench
./sync-desktop.sh
t3 theme set atelier-workbench
```

### Option 2: Windows / macOS Desktop One-Click Sync
- **macOS / Linux**: Run `./sync-desktop.sh`
- **Windows (PowerShell)**: Run `.\sync-desktop.ps1`

Then open **Settings → Appearance** in T3 Code, select **`Atelier Workbench · 砚纸精工`**, and set appearance to **System** for automatic day/night switching.

### Option 3: Web / Mobile Chrome (`app.t3.codes`)
1. Open **Settings → Appearance → Add a theme**.
2. Choose `atelier-workbench.json` (or paste its JSON content into **Theme JSON**) and click **+ Add theme**.
3. Select **Atelier Workbench · 砚纸精工** and set appearance to **System**.

## Rebuild from Source

```bash
python3 scripts/build_theme.py
```

Requires Python 3.10+, `numpy`, and `Pillow` (only needed if regenerating the `.webp` wallpaper).

## License

- Theme, build scripts, and procedural wallpaper: [MIT License](./LICENSE)
- Embedded font subsets (`Newsreader`, `IBM Plex Mono`): SIL Open Font License 1.1
