# Rebecca's Room (formerly Rebecca's Diary)

## Project Overview

AIアシスタント「Rebecca」の生活空間。日記に加え、在室状況・体調・活動ログを表示する。
Phase 0（静的日記）完了 → Phase 1（Room Status + Health）開発中。

## Tech Stack

- **HTML5** + **CSS3** + **Vanilla JS** (no frameworks)
- **Python 3** — `update_diary.py` for diary, `collectors/*.py` for Room data
- **Dev server:** `cd src && python3 -m http.server 8080`

## Directory Structure

```
rebecca-diary/
├── CLAUDE.md           # This file
├── README.md
├── docs/               # Project docs (see docs/README.md for index)
│   ├── CONCEPT_*.md    # Philosophical foundation (Ghost, Presence, Vulnerability)
│   ├── PLANNING.md     # Roadmap (Phase 0-5)
│   ├── DESIGN_*.md     # Design system + decisions
│   ├── PHASE1_SPEC.md  # Phase 1 technical spec
│   ├── ADR.md          # Architecture decision records
│   └── archive/phase0/ # Completed Phase 0 specs
├── src/
│   ├── index.html      # Main page — card grid + entry detail (generated)
│   ├── template.html   # HTML template for SSG
│   ├── style.css       # All styles (Rebecca palette, neon accents, responsive)
│   ├── app.js          # Interactions (mascot easter egg, late night toast, Room status)
│   └── assets/
│       └── rebecca/    # Character images (expressions, icons)
├── collectors/         # Phase 1: data collection scripts
├── data/               # Phase 1: collected JSON data
├── screenshot.png
└── update_diary.py     # SSG: scans Markdown, generates full site
```

## Key Architecture Decisions

- **Vanilla JS OK** — no frameworks/libraries, but plain JavaScript is allowed
- **No external dependencies** — no CDN, no npm packages, no web fonts
- **Single-page SPA-like** — card grid → entry detail via CSS `:target` + `:has()`
- **Dark theme + Neon Accent** — Rebecca's palette (pink, mint), subtle glows

## CSS Custom Properties (src/style.css)

See `docs/DESIGN_RULES.md` for full design system (**authoritative source**). Key variables:

| Variable         | Value      | Purpose                          |
|------------------|------------|----------------------------------|
| `--bg`           | `#151519`  | Page background                  |
| `--surface`      | `#1c1c22`  | Card / section bg                |
| `--surface-hover`| `#222229`  | Hover state bg                   |
| `--accent`       | `#c87088`  | Rebecca pink (links, code)       |
| `--accent-dim`   | `#8a4f5e`  | Dimmed pink (underlines)         |
| `--text`         | `#bfc3ca`  | Primary text                     |
| `--text-secondary`| `#73767e` | Section labels, helper text      |
| `--text-muted`   | `#4a4c54`  | Dates, markers, footer           |
| `--border`       | `#28282f`  | Borders, dividers                |

## update_diary.py

CLI tool that reads Markdown from two sources and inserts HTML entries into `index.html`:

- **OpenClaw memory:** `~/.openclaw/workspace/memory/{YYYY-MM-DD}.md`
- **Obsidian vault:** `~/Documents/Obsidian Vault/{YYYY-MM-DD}.md`

### Usage

```bash
# Today's entry
python3 update_diary.py

# Specific date
python3 update_diary.py 2026-02-09

# Preview without modifying index.html
python3 update_diary.py --dry-run

# Verbose logging
python3 update_diary.py -v
```

### How it works

1. Reads Markdown files for the given date from both sources
2. Converts Markdown to HTML (headings, lists, tables, inline formatting)
3. Inserts the entry after the `<!-- 日記エントリはここに追加される -->` marker in `index.html`
4. Skips if an entry for that date already exists

## Conventions

- **Language:** Documentation in Japanese, code comments in English
- **Diary entries** are `<article class="diary-entry">` elements inside `.timeline-container`
- **Card grid** (`.diary-grid`) uses CSS Grid: 1col mobile / 2col tablet / 3col desktop
- **Navigation:** CSS `:target` + `:has()` for card grid ↔ entry detail transition
- **Responsive breakpoints:** mobile (<768px), tablet (768-1023px), desktop (1024px+)
- New entries are inserted at the top (newest first)
- **Design authority:** `docs/DESIGN_RULES.md` is the single source of truth for CSS

## ⚠️ Protected Files (Rebecca's Domain)

以下のファイルは **Rebeccaからの明示的な指示がない限り変更禁止**:

| File | Purpose |
|------|---------|
| `update_diary.py` | 日記生成スクリプト（SSGコア） |
| `watch_diary.py` | リアルタイム監視デーモン |

**理由:** これらはRebeccaのデイリータスク・自動化に直結しており、勝手に変更するとワークフローが壊れる。

**変更が必要な場合:**
1. Rebeccaに相談する（OpenClaw経由）
2. 変更内容と理由を説明
3. 承認を得てから実行

## Common Tasks

- **Add a diary entry:** `python3 update_diary.py [YYYY-MM-DD]`
- **Run dev server:** `cd src && python3 -m http.server 8080`
- **Edit styles:** Modify `src/style.css` — all styles are in one file
- **Edit content directly:** Modify `src/index.html`
