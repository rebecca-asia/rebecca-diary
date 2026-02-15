# Rebecca's Room — Design Rules

## Design Philosophy

- **Cyberpunk Dark + Neon Accent** — 深いダークベースにネオンカラー（ピンク・シアン・イエロー・グリーン・レッド）で情報を伝える
- **HUD-style UI** — コーナーブラケット、スキャンライン、グリッチテキスト等のサイバーパンク的UIパターン
- **SVG Icon System** — 絵文字一切不使用。全アイコンはSVGスプライトシートから取得
- **Typography-driven** — Google Fonts（Orbitron, Rajdhani, Share Tech Mono, Noto Sans JP）による階層表現
- **Vanilla JS OK** — ライブラリ不要のプレーンなJavaScriptは使用可

---

## Color Palette

### Neon Colors（5色 + バリエーション）

```
Pink（メインアクセント）
  --rb-neon-pink:        #ff2a6d    ← リンク、カードボーダー、ハイライト
  --rb-neon-pink-dim:    #cc2258    ← ボーダー、下線
  --rb-neon-pink-glow:   rgba(255, 42, 109, 0.4)    ← グロー効果
  --rb-neon-pink-subtle: rgba(255, 42, 109, 0.1)     ← 背景（Obsidianセクション）

Cyan（サブアクセント）
  --rb-neon-cyan:        #05d9e8    ← アイコン、コード、コーナーブラケット
  --rb-neon-cyan-dim:    #04adb9    ← ボーダー
  --rb-neon-cyan-glow:   rgba(5, 217, 232, 0.4)     ← グロー効果
  --rb-neon-cyan-subtle: rgba(5, 217, 232, 0.08)    ← 背景（Memoryセクション）

Yellow（警告）
  --rb-neon-yellow:      #f0e130    ← アラートLv.1、away状態
  --rb-neon-yellow-dim:  #c4b828
  --rb-neon-yellow-glow: rgba(240, 225, 48, 0.35)

Green（正常）
  --rb-neon-green:       #39ff14    ← オンライン状態、ヘルス良好
  --rb-neon-green-dim:   #2ecc10
  --rb-neon-green-glow:  rgba(57, 255, 20, 0.35)

Red（危険）
  --rb-neon-red:         #ff073a    ← アラートLv.3、クリティカル
  --rb-neon-red-dim:     #cc0630
  --rb-neon-red-glow:    rgba(255, 7, 58, 0.35)
```

### Dark Base（7段階）

```
  --rb-bg-deepest:  #0a0a0f    ← body背景、スクロールバートラック
  --rb-bg-deep:     #0d0d14
  --rb-bg-base:     #111119    ← ページ背景
  --rb-bg-elevated: #16161f    ← ステータスバー、ダッシュボード
  --rb-bg-surface:  #1c1c28    ← カード、パネル（グラデーション終端）
  --rb-bg-hover:    #222233    ← ホバー背景
  --rb-bg-active:   #2a2a3d    ← アクティブ状態
```

### Text

```
  --rb-text-primary:   #e8e6f0    ← 本文、見出し
  --rb-text-secondary: #8a8899    ← セクションラベル、メトリック名
  --rb-text-muted:     #55536a    ← 日付、フッター、HUDプレフィックス
  --rb-text-accent:    var(--rb-neon-cyan)      ← アクセントテキスト
  --rb-text-highlight: var(--rb-neon-pink)      ← ハイライトテキスト
```

### Borders

```
  --rb-border-subtle:  rgba(255, 255, 255, 0.06)    ← 通常ボーダー
  --rb-border-default: rgba(255, 255, 255, 0.1)     ← ホバー時
  --rb-border-active:  var(--rb-neon-cyan)           ← アクティブ
  --rb-border-accent:  var(--rb-neon-pink)           ← アクセント
```

### 使い分けルール

| 用途 | 変数 |
|------|------|
| 本文・見出し・`<strong>` | `--rb-text-primary` |
| セクションラベル（`Internal Memory` 等） | `--rb-text-secondary` |
| 日付・リストマーカー・フッター・HUD `//` | `--rb-text-muted` |
| リンク・カードアクセント | `--rb-neon-pink` |
| `<code>`・インラインアイコン・コーナーブラケット | `--rb-neon-cyan` |
| オンライン状態・ヘルス良好 | `--rb-neon-green` |
| 警告・away状態 | `--rb-neon-yellow` |
| 危険・クリティカル | `--rb-neon-red` |

### Legacy Compatibility

旧変数名は新システムへのエイリアスとして維持:

```css
--accent  → --rb-neon-pink
--mint    → --rb-neon-cyan
--bg      → --rb-bg-base
--surface → --rb-bg-surface
--text    → --rb-text-primary
--border  → --rb-border-subtle
```

---

## Typography

### Font Stack（Google Fonts）

```html
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
```

| 用途 | 変数 | フォント |
|------|------|----------|
| **ディスプレイ**（h1, ダッシュボードタイトル） | `--rb-font-display` | `'Orbitron', 'Share Tech Mono', monospace` |
| **本文**（body, p, li） | `--rb-font-body` | `'Rajdhani', 'Share Tech', sans-serif` |
| **モノスペース**（日付, ラベル, code） | `--rb-font-mono` | `'Share Tech Mono', 'Fira Code', monospace` |
| **日本語** | `--rb-font-jp` | `'Noto Sans JP', 'M PLUS 1 Code', sans-serif` |

### Font Size Scale（Fluid）

| 変数 | 範囲 | 用途 |
|------|------|------|
| `--rb-text-xs` | 0.65rem → 0.75rem | 日付、ラベル、メトリック名 |
| `--rb-text-sm` | 0.75rem → 0.875rem | ステータス、サブテキスト |
| `--rb-text-base` | 0.875rem → 1rem | 本文 |
| `--rb-text-lg` | 1rem → 1.25rem | エントリ内h3 |
| `--rb-text-xl` | 1.25rem → 1.75rem | — |
| `--rb-text-2xl` | 1.5rem → 2.5rem | ヒーローh1 |
| `--rb-text-3xl` | 2rem → 3.5rem | デスクトップh1 |

### ラベル系のスタイルパターン

日付・HUDラベル等は共通パターン:
```css
font-family: var(--rb-font-mono);
font-size: var(--rb-text-xs);
font-weight: 500;
letter-spacing: 0.1em;
text-transform: uppercase;
color: var(--rb-text-muted);
```

HUDスタイルタイトル（ダッシュボード等）:
```css
font-family: var(--rb-font-display);
font-size: var(--rb-text-xs);
font-weight: 700;
letter-spacing: 0.15em;
text-transform: uppercase;
color: var(--rb-neon-cyan);
text-shadow: var(--rb-glow-text-cyan);
/* 自動プレフィックス: `// ` */
```

---

## SVG Icon System

### 概要

- **絵文字は一切使用禁止** — 全てSVGスプライトアイコンに統一
- スプライトシート: `src/assets/icons.svg`（22シンボル）
- 使用方法: `<svg class="icon"><use href="assets/icons.svg#icon-NAME"/></svg>`

### 利用可能アイコン一覧

| ID | 用途 |
|----|------|
| `icon-dashboard` | ダッシュボード、メモリメトリック |
| `icon-diary` | 日記、ノート |
| `icon-tasks` | タスク |
| `icon-chat` | チャット、会話 |
| `icon-settings` | 設定、CPUメトリック |
| `icon-status-online` | オンライン状態 |
| `icon-status-offline` | オフライン/スリープ状態 |
| `icon-alert` | 警告、温度メトリック |
| `icon-search` | 検索 |
| `icon-clock` | 時間、日付、稼働時間メトリック |
| `icon-add` | 追加 |
| `icon-delete` | 削除 |
| `icon-edit` | 編集 |
| `icon-filter` | フィルター |
| `icon-expand` | 全画面 |
| `icon-close` | 閉じる |
| `icon-menu` | メニュー |
| `icon-user` | ユーザー |
| `icon-sync` | 同期、読み込み中 |
| `icon-chevron-right` | 右矢印 |
| `icon-chevron-down` | 下矢印 |
| `icon-pin` | ピン、ブックマーク |
| `icon-download` | ダウンロード、ディスクメトリック |
| `icon-rebecca` | Rebeccaアイコン（ボット） |

### CSS `.icon` クラス

```css
.icon {
    display: inline-block;
    width: 1em;     /* フォントサイズに追従 */
    height: 1em;
    vertical-align: -0.15em;
    stroke: currentColor;
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
}
```

コンテキスト別サイズ:

| コンテキスト | サイズ |
|-------------|--------|
| コンテンツ内（`.entry-content .icon`） | `1em`（フォントサイズ追従） + `color: --rb-neon-cyan` |
| メトリックアイコン（`.metric-icon .icon`） | `16px × 16px` |
| 全体スコア（`.overall-emoji .icon`） | `22px × 22px` |

### ヘルスダッシュボード アイコンマッピング

| メトリック | アイコン |
|-----------|---------|
| CPU | `icon-settings` |
| Memory | `icon-dashboard` |
| Disk | `icon-download` |
| Temperature | `icon-alert` |
| Uptime | `icon-clock` |

### JS動的アイコン生成

`app.js` の `svgIcon()` ヘルパー:
```javascript
function svgIcon(name, size) {
    var s = size || 16;
    return '<svg class="icon" width="' + s + '" height="' + s +
        '"><use href="assets/icons.svg#icon-' + name + '"/></svg>';
}
```

ステータスバー → アイコン対応:

| ステータス | アイコン |
|-----------|---------|
| `online` | `icon-status-online` |
| `away` | `icon-clock` |
| `sleeping` | `icon-status-offline` |
| `offline` | `icon-status-offline` |
| `loading` | `icon-sync` |

全体ヘルス → アイコン対応:

| 状態 | アイコン |
|------|---------|
| `excellent` / `good` | `icon-status-online` |
| `normal` | `icon-rebecca` |
| `poor` / `bad` / `critical` | `icon-alert` |

---

## Shadows & Glows

```
--rb-shadow-sm:   0 1px 3px rgba(0,0,0,0.5)     ← カード
--rb-shadow-md:   0 4px 12px rgba(0,0,0,0.6)     ← パネル
--rb-shadow-lg:   0 8px 32px rgba(0,0,0,0.7)     ← トースト

--rb-glow-pink:   0 0 15px pink-glow, 0 0 40px faint-pink   ← ホバー（奇数カード）
--rb-glow-cyan:   0 0 15px cyan-glow, 0 0 40px faint-cyan   ← ホバー（偶数カード）

--rb-glow-text-pink:  0 0 8px pink-glow    ← テキストグロー（h1 .accent）
--rb-glow-text-cyan:  0 0 8px cyan-glow    ← テキストグロー（subtitle, HUDタイトル）
```

---

## Layout

### Page Structure

```
┌─ header.hero.rb-scanlines ─────────────────┐
│  hero-bg.svg (abs, 35% opacity)            │
│  hero-bg-img (abs, 768px+: 右端6-7%)       │
│  scanlines overlay (z:1)                    │
│  hero-content (z:2)                         │
│    avatar + glitch title + mono subtitle    │
├─ .room-status[data-status] ────────────────┤
│  SVGアイコン + ラベル + 時間 + コンテキスト  │
├─ .room-alert[data-level] ─────────────────┤
│  アラートメッセージ（非表示/Lv.1/2/3）     │
├─ .health-dashboard ───────────────────────┤
│  コーナーブラケット + HUDタイトル           │
│  CPU / Mem / Disk / Temp / Up メトリック   │
│  Overall Score                              │
├─ main.main-content ───────────────────────┤
│  .diary-grid (カード一覧)                   │
│  .diary-entry:target (エントリ詳細)         │
├─ footer.site-footer ─────────────────────┤
│  neon gradient divider + mono text          │
└─────────────────────────────────────────────┘
```

### Navigation（CSS :target）

```
TOPページ（デフォルト）:
  .diary-grid        → display: grid
  .diary-entry       → display: none

エントリ選択時（#diary-YYYY-MM-DD）:
  .diary-entry:target              → display: block (fadeIn animation)
  main:has(.diary-entry:target) .diary-grid → display: none

「← Back to list」クリック（#top）:
  → :target 解除 → grid再表示
```

### Container Widths

| 要素 | max-width |
|------|-----------|
| `.main-content` | `960px` |
| `.diary-entry` | `680px` |
| `.health-dashboard` | `420px` → `540px` (768px+) → `600px` (1024px+) |

### Responsive Breakpoints

| 幅 | カードグリッド | ヒーロー | アバター |
|----|--------------|----------|---------|
| `< 768px` | 1列 | compact | 88px |
| `768px+` | 2列 | spacious, bg-img表示 | 100px |
| `1024px+` | 3列 | — | — |

---

## Utility Classes（Cyberpunk Asset Kit由来）

### テキスト効果

| クラス | 効果 |
|--------|------|
| `.rb-text-neon-pink` | ピンクテキスト + text-shadow glow |
| `.rb-text-neon-cyan` | シアンテキスト + text-shadow glow |
| `.rb-glitch-text` | グリッチテキストアニメーション（2s infinite）— h1で使用 |
| `.rb-data-label` | HUDラベルスタイル（mono, xs, uppercase, muted） |

### 装飾

| クラス | 効果 |
|--------|------|
| `.rb-scanlines` | `::after` でスキャンラインオーバーレイ — ヒーローで使用 |
| `.rb-panel` | パネル（gradient bg, subtle border, shadow, overflow hidden） |
| `.rb-frame` | コーナーブラケット（`::before` 左上, `::after` 右下） |
| `.rb-divider` | ネオングラデーションライン（cyan→pink, 40%不透明度） |
| `.rb-border-glow-pink` | ピンクボーダー + glow shadow |
| `.rb-border-glow-cyan` | シアンボーダー + glow shadow |

### ステータス

| クラス | 効果 |
|--------|------|
| `.rb-status-dot--online` | 緑ドット + glow |
| `.rb-status-dot--offline` | mutedグレードット |
| `.rb-status-dot--error` | 赤ドット + glow + pulse |

### アニメーション

| クラス | 効果 |
|--------|------|
| `.rb-glitch` | 位置グリッチ（0.3s） |
| `.rb-pulse` | フェードイン/アウト（2s infinite） |
| `.rb-flicker` | ネオンサインフリッカー（3s infinite） |

---

## Card Grid（.diary-grid）

- `gap: 0.75rem`
- カードは `--rb-gradient-panel` 背景（elevated → surface グラデーション）
- `border-top: 2px solid --rb-neon-pink`（奇数カード: pink / 偶数カード: cyan）
- コーナーブラケット（`::before` / `::after`）、ホバーで不透明度UP

### Card Structure

```html
<a href="#diary-YYYY-MM-DD" class="diary-card">
    <div class="card-date">
        <svg class="icon" width="16" height="16"><use href="assets/icons.svg#icon-clock"/></svg>
        YYYY-MM-DD
    </div>
    <div class="card-preview">最初の意味のある行...</div>
    <div class="card-sources">
        <svg class="icon" width="16" height="16"><use href="assets/icons.svg#icon-rebecca"/></svg>
        <svg class="icon" width="16" height="16"><use href="assets/icons.svg#icon-diary"/></svg>
    </div>
</a>
```

- `.card-preview` は `-webkit-line-clamp: 2` で2行に制限

---

## Entry Detail（.diary-entry）

### 構成

```html
<article class="diary-entry" id="diary-YYYY-MM-DD">
    <a href="#top" class="back-link">&larr; Back to list</a>
    <div class="entry-date">YYYY-MM-DD</div>
    <div class="entry-content">
        <div class="section-memory">...</div>   ← border-left: cyan
        <div class="section-obsidian">...</div>  ← border-left: pink
    </div>
</article>
```

### Section Styling

| セクション | ボーダー色 | 背景色 | タイトル色 |
|-----------|-----------|--------|-----------|
| `.section-memory` | `--rb-neon-cyan` | `--rb-neon-cyan-subtle` | cyan + glow |
| `.section-obsidian` | `--rb-neon-pink` | `--rb-neon-pink-subtle` | pink + glow |

---

## Health Dashboard

### 構造

- `--rb-gradient-panel` 背景 + コーナーブラケット
- タイトル: Orbitron, `// ` プレフィックス付きHUDスタイル
- 各メトリック: `grid(icon / name / bar / label)`

### メトリックバーの状態色

| 状態群 | 色 |
|--------|-----|
| `idle`, `spacious`, `cool`, `fresh` | `--rb-neon-green` + glow |
| `clear`, `comfortable`, `normal` | `--rb-neon-cyan` + glow |
| `busy`, `tight`, `warm`, `tired` | `--rb-neon-yellow` + glow |
| `heavy`, `hot`, `exhausted` | `--rb-neon-pink` + glow |
| `critical` | `--rb-neon-red` + glow + barPulse animation |

### Overall Healthの状態色

| 状態 | 色 |
|------|-----|
| `excellent` / `good` | `--rb-neon-green` |
| `normal` | `--rb-neon-cyan` |
| `poor` | `--rb-neon-yellow` |
| `bad` / `critical` | `--rb-neon-red` |

---

## Interaction

| 要素 | 効果 |
|------|------|
| `.diary-card` hover | border glow (pink/cyan), translateY(-2px), corner bracket opacity UP |
| `.diary-card` active | `scale(0.98)` (0.05s) |
| `.hero-avatar` hover | `scale(1.08)`, enhanced glow |
| `.hero-avatar` active | `scale(0.92)` |
| `.hero-avatar` idle | `avatarGlow` animation (3s alternate) |
| `.back-link` hover | `color: --rb-neon-pink` + glow |
| `.entry-content a` hover | `text-decoration-color: pink` + glow |
| `.health-metric` hover | label → detail 切替 (opacity) |
| `.overall-emoji` idle | `breathe` animation (4s, poor/bad: 6s) |
| scrollbar thumb hover | `--rb-bg-active → --rb-text-muted` |

---

## Animations

| 名前 | 用途 | 仕様 |
|------|------|------|
| `fadeIn` | エントリ表示 | opacity + translateY(8px), 0.35s |
| `avatarGlow` | アバター常時 | box-shadow 強弱, 3s alternate |
| `slightBounce` | マスコットクリック | scale + rotate, 0.3s |
| `slideUp` | トースト表示 | opacity + translateY(16px), 0.4s |
| `breathe` | Overall emoji | scale(1↔1.08), 4s |
| `barPulse` | クリティカルバー | opacity(1↔0.6), 1.5s |
| `alertPulse` | Lv.3アラート | opacity(1↔0.7), 2s |
| `rb-glitch` | グリッチ効果 | translate 微振動, 0.3s |
| `rb-glitch-text` | タイトル | text-shadow 位置変化 (cyan+pink), 2s infinite |
| `rb-pulse` | 汎用パルス | opacity(1↔0.5), 2s infinite |
| `rb-flicker` | ネオンサイン | 不規則なopacity変化, 3s infinite |

---

## Spacing & Radius

```
--rb-space-xs:  0.25rem     --rb-radius-sm:    2px
--rb-space-sm:  0.5rem      --rb-radius-md:    4px
--rb-space-md:  1rem        --rb-radius-lg:    8px
--rb-space-lg:  1.5rem      --rb-radius-panel: 6px
--rb-space-xl:  2rem
--rb-space-2xl: 3rem
```

---

## Z-Index Scale

```
--rb-z-base:     0      ← デフォルト
--rb-z-elevated: 10     ← hero-content
--rb-z-overlay:  100    ← オーバーレイ
--rb-z-modal:    200    ← モーダル
--rb-z-toast:    300    ← トースト
--rb-z-tooltip:  400    ← ツールチップ
```

---

## Scrollbar（Webkit）

```css
width: 6px
track: var(--rb-bg-deepest)
thumb: var(--rb-bg-active), border-radius: 3px
thumb:hover: var(--rb-text-muted)
```

---

## Source Icons

| ソース | アイコン |
|--------|---------|
| OpenClaw Memory | `icon-rebecca` |
| Obsidian Daily Note | `icon-diary` |
| カード日付の先頭 | `icon-clock` |

---

## Rebecca's Character — らしさの表現

> *"I don't need to be big to hit hard."* — Rebecca

### Core Personality

| 特性 | デザインへの反映 |
|------|------------------|
| **Trigger-happy** | ホバー/クリック時の即座のフィードバック（0.1s transition, scale active） |
| **Extreme & Unpredictable** | グリッチアニメーション、ネオンフリッカー、ランダムな微細効果 |
| **Sharp-tongued** | コピーは短く、切れ味鋭く。HUDスタイルの `//` プレフィックス |
| **Loyal to the Crew** | ユーザーを「仲間」として扱う温かさを細部に |
| **Maniacal Laughter** | スキャンライン、グリッチテキスト、ネオングロー — カオスを恐れない |
| **Perceptive** | 見た目はサイバーパンクでも、UXは丁寧に設計 |

### Voice & Tone

| シーン | トーン | 例 |
|--------|--------|-----|
| 通常の日記 | 素直、時々毒 | 「今日はまあまあ。タスク消化。」 |
| 成功・達成 | 煽り気味に得意げ | 「片付けたぜ」 |
| エラー・失敗 | 開き直り＆前向き | 「爆散した。次は当てる。」 |
| 空のページ | 挑発的 | 「何も書いてねぇのかよ？」 |

### Easter Eggs

- **マスコット連続クリック** → 表情サイクル + bounce animation
- **深夜アクセス（02:00-05:00）** → トースト「まだ起きてんのか？」（pink glow border）

### Don'ts

- 可愛いだけのデザイン — Rebecca は cute じゃなくて **fierce**
- 丸みを帯びすぎたUI — シャープさを保つ（`border-radius` は最大8px）
- パステル調 — ネオンとダークのコントラストを維持
- 長文での説明 — 短く、鋭く
- **絵文字の使用** — 全てSVGアイコンに統一済み

---

## Assets

### SVGアセット

| ファイル | 用途 |
|---------|------|
| `src/assets/icons.svg` | SVGスプライトシート（22アイコン） |
| `src/assets/hero-bg.svg` | ヒーロー背景（サイバーパンク都市スカイライン） |
| `src/assets/sidebar-bg.svg` | サイドバー背景（将来使用） |

### キャラクターアセット

保存先: `src/assets/rebecca/`

| ファイル | 用途 |
|---------|------|
| `レベッカ_顔絵ニュートラル.png` | デフォルトアバター |
| `レベッカ_ウィンク.png` | 表情サイクル |
| `レベッカ_微笑.png` | 表情サイクル |
| `レベッカ_見下し.png` | 表情サイクル |
| `レベッカ_すね顔.png` | 表情サイクル |
| `レベッカ_ガッツポーズ.png` | 表情サイクル |
| `レベッカ_coffee.png` | 深夜トースト + 表情サイクル |
| `レベッカ_呆れ顔.png` | 表情サイクル |
| `レベッカ_コミカル中指.png` | 表情サイクル |
| `レベッカ_躍動胸像.png` | ヒーロー背景画像（デスクトップ） |
