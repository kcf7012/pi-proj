# 簡報範例：Plugin 開發介紹

> 這是一個最簡單的 learn2deck 範例，示範從 Markdown 產生 PPTX。

## 檔案結構

```
minimal-plugin/
├── outline.yaml    ← 簡報大綱（YAML 格式）
├── content.md      ← 簡報內容（Markdown 格式）
└── README.md       ← 本檔案
```

## 產生 PPTX

```bash
# 在 learn2deck 套件根目錄下
learn2deck build examples/minimal-plugin/content.md \
  -o examples/minimal-plugin/output.pptx --validate

# 或用 python -m 形式（不需安裝到 PATH）
python -m learn2deck build examples/minimal-plugin/content.md \
  -o examples/minimal-plugin/output.pptx --validate
```

## 預期結果

5 張投影片：

1. **封面** — Plugin 開發介紹
2. **Section Divider** — Part 1: 基礎概念
3. **Title Table** — Plugin vs 獨立配置
4. **Grid Cards** — 3 種 Plugin 元件
5. **Summary** — 下一步

## 為什麼用 Markdown？

- ✅ 版本控制友善（Git diff 清楚）
- ✅ 容易編輯（任何文字編輯器都行）
- ✅ 自動推斷 slide_type（不用寫複雜 YAML）
- ✅ 可重用（同一份 .md 可轉多種格式）
