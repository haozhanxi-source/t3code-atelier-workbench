#!/usr/bin/env bash
# One-click sync of Atelier Workbench theme + 4K wallpaper to local macOS/Linux T3 Code Desktop.
# Pass --install-fonts to also install official open-source Noto Serif CJK SC (Regular + Medium) for CJK headings.
set -euo pipefail

INSTALL_FONTS=0
for arg in "$@"; do
  case "$arg" in
    --install-fonts) INSTALL_FONTS=1 ;;
    *) echo "Unknown option: $arg (supported: --install-fonts)" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${T3CODE_HOME:-$HOME/.t3}/userdata/themes"
mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/atelier-workbench.json" "$TARGET_DIR/atelier-workbench.json"
cp "$SCRIPT_DIR/atelier-workbench.webp" "$TARGET_DIR/atelier-workbench.webp"
rm -f "$TARGET_DIR/atelier-workbench.png"
echo "Installed Atelier Workbench theme to $TARGET_DIR"

if [ "$INSTALL_FONTS" -eq 1 ]; then
  if [ "$(uname -s)" = "Darwin" ]; then
    FONT_DIR="$HOME/Library/Fonts"
  else
    FONT_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/NotoSerifCJKsc"
  fi
  mkdir -p "$FONT_DIR"
  BASE_URL="https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/OTF/SimplifiedChinese"

  install_verified_font() {
    local fname="$1"
    local expected="$2"
    local tmp_file
    tmp_file="$(mktemp)"
    curl -fsSL -o "$tmp_file" "$BASE_URL/$fname"
    local actual
    if command -v sha256sum >/dev/null 2>&1; then
      actual="$(sha256sum "$tmp_file" | awk '{print $1}')"
    else
      actual="$(shasum -a 256 "$tmp_file" | awk '{print $1}')"
    fi
    if [ "$actual" != "$expected" ]; then
      rm -f "$tmp_file"
      echo "SHA-256 mismatch for $fname (expected $expected, got $actual)" >&2
      exit 1
    fi
    mv -f "$tmp_file" "$FONT_DIR/$fname"
    echo "Installed $fname to $FONT_DIR"
  }

  install_verified_font "NotoSerifCJKsc-Regular.otf" "2a2eae2628df83556c54018c41e20fa532c1b862c5256ae8b3f23feb918d12ca"
  install_verified_font "NotoSerifCJKsc-Medium.otf" "19322be2ecf5dd2abd546db7a86cc83c286026cbd28593583bfcfd721e48c9fe"
  if command -v fc-cache >/dev/null 2>&1; then
    fc-cache -f "$FONT_DIR" >/dev/null 2>&1 || true
  fi
  echo "Restart T3 Code (or your browser) to pick up newly installed fonts."
fi

echo "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"

