#!/usr/bin/env bash
# One-click sync of Atelier Workbench theme + 4K wallpaper to local macOS/Linux T3 Code Desktop
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${T3CODE_HOME:-$HOME/.t3}/userdata/themes"
mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/atelier-workbench.json" "$TARGET_DIR/atelier-workbench.json"
cp "$SCRIPT_DIR/atelier-workbench.webp" "$TARGET_DIR/atelier-workbench.webp"
echo "Installed Atelier Workbench theme to $TARGET_DIR"
echo "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"
