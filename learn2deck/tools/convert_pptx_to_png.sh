#!/usr/bin/env bash
# Phase 9 視覺驗證加速工具：批次把新舊 .pptx 轉成 PNG 方便比對
#
# 用法：
#   chmod +x convert_pptx_to_png.sh
#   ./convert_pptx_to_png.sh
#
# 前提：已安裝 libreoffice + poppler-utils
#   sudo apt install -y libreoffice poppler-utils
#
# 產出：
#   /tmp/old_png/00-overview_pptx_slide_01.png ... slide_NN.png
#   /tmp/new_png/00-claude-code-plugins-series_pptx_slide_01.png ... slide_NN.png

set -e

OLD_DIR="/home/elan/pi-proj"
NEW_DIR="/tmp"
OLD_OUT="/tmp/old_png"
NEW_OUT="/tmp/new_png"
PDF_TMP="/tmp/_pdf_tmp"

mkdir -p "$OLD_OUT" "$NEW_OUT" "$PDF_TMP"

# 8 對檔案（OLD 檔名, NEW 檔名）
pairs=(
  "00-overview.pptx|new_00-claude-code-plugins-series.pptx"
  "01-plugin-marketplaces.pptx|new_01-plugin-marketplaces.pptx"
  "02-plugins.pptx|new_02-plugins.pptx"
  "03-plugins-reference.pptx|new_03-plugins-reference.pptx"
  "04-skills.pptx|new_04-skills.pptx"
  "05-subagents.pptx|new_05-subagents.pptx"
  "06-hooks.pptx|new_06-hooks.pptx"
  "07-discover-plugins.pptx|new_07-discover-plugins.pptx"
)

echo "=== Phase 9 視覺驗證：批次轉檔 ==="
echo "OLD_DIR: $OLD_DIR"
echo "NEW_DIR: $NEW_DIR"
echo ""

# 檢查 LibreOffice 是否安裝
if ! command -v libreoffice &> /dev/null; then
    echo "❌ 找不到 libreoffice，請先安裝："
    echo "   sudo apt install -y libreoffice poppler-utils"
    exit 1
fi

if ! command -v pdftoppm &> /dev/null; then
    echo "❌ 找不到 pdftoppm，請先安裝："
    echo "   sudo apt install -y poppler-utils"
    exit 1
fi

echo "✓ libreoffice: $(libreoffice --version | head -1)"
echo "✓ pdftoppm: $(pdftoppm -v 2>&1 | head -1)"
echo ""

# 先把新檔重新產出（保險起見）
echo "=== 重產 8 份新 PPTX ==="
cd /home/elan/pi-proj/learn2deck
for md in ../0?-*.md; do
    base=$(basename "$md" .md)
    /home/elan/pi-proj/.pptx-venv/bin/learn2deck build "$md" \
        -o "$NEW_DIR/new_${base}.pptx" --validate 2>&1 | tail -1
done
echo ""

# 批次轉檔
echo "=== 轉檔 PPTX → PDF → PNG ==="
for pair in "${pairs[@]}"; do
    old="${pair%|*}"
    new="${pair#*|}"

    old_base="${old%.pptx}"        # 00-overview
    new_base="${new%.pptx}"        # new_00-claude-code-plugins-series

    # OLD
    if [[ -f "$OLD_DIR/$old" ]]; then
        echo "→ OLD: $old"
        libreoffice --headless --convert-to pdf \
            --outdir "$PDF_TMP/old" "$OLD_DIR/$old" > /dev/null 2>&1
        pdftoppm -png -r 100 "$PDF_TMP/old/$old" \
            "$OLD_OUT/${old_base}_pptx_slide" > /dev/null 2>&1
    else
        echo "⚠ 找不到 OLD: $OLD_DIR/$old"
    fi

    # NEW
    if [[ -f "$NEW_DIR/$new" ]]; then
        echo "→ NEW: $new"
        libreoffice --headless --convert-to pdf \
            --outdir "$PDF_TMP/new" "$NEW_DIR/$new" > /dev/null 2>&1
        pdftoppm -png -r 100 "$PDF_TMP/new/$new" \
            "$NEW_OUT/${new_base}_pptx_slide" > /dev/null 2>&1
    else
        echo "⚠ 找不到 NEW: $NEW_DIR/$new"
    fi
    echo ""
done

# 統計
echo "=== 產出統計 ==="
old_count=$(ls "$OLD_OUT"/*.png 2>/dev/null | wc -l)
new_count=$(ls "$NEW_OUT"/*.png 2>/dev/null | wc -l)
echo "OLD PNG: $old_count 張  → $OLD_OUT"
echo "NEW PNG: $new_count 張  → $NEW_OUT"
echo ""

# 清理暫存 PDF
rm -rf "$PDF_TMP"

echo "=== 完成！==="
echo ""
echo "並排比對建議："
echo "  # 用圖片瀏覽器開啟兩個資料夾"
echo "  xdg-open $OLD_OUT  # GNOME"
echo "  xdg-open $NEW_OUT  # KDE"
echo ""
echo "  # 或用 sxiv / feh / eog 等"
echo ""
echo "逐檔對照表："
for pair in "${pairs[@]}"; do
    old="${pair%|*}"
    new="${pair#*|}"
    old_base="${old%.pptx}"
    new_base="${new%.pptx}"
    old_n=$(ls "$OLD_OUT/${old_base}_pptx_slide"-*.png 2>/dev/null | wc -l)
    new_n=$(ls "$NEW_OUT/${new_base}_pptx_slide"-*.png 2>/dev/null | wc -l)
    printf "  %-30s OLD=%2d  NEW=%2d  Δ=%+d\n" "$old_base" "$old_n" "$new_n" "$((new_n - old_n))"
done
