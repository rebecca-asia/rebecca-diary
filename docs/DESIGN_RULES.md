# Rebecca's Diary — Design Rules

## Design Philosophy

- **Quiet Dark + Neon Accent** — 落ち着いたダークトーンがベース。ネオン・グローは味付けとして控えめに使用OK
- **Typography-driven** — 装飾ではなくフォント・余白・階層で情報を伝える
- **Vanilla JS OK** — ライブラリ不要のプレーンなJavaScriptは使用可。ナビゲーション、フィルタ、アニメーション制御等
- **No external dependencies** — フレームワーク・CDN・Webフォント一切なし

---

## Color Palette

```
Background
  --bg:              #151519    ← ページ背景（ほぼ黒）
  --surface:         #1c1c22    ← カード/セクション背景
  --surface-hover:   #222229    ← ホバー時の背景

Accent
  --accent:          #c87088    ← ピンク（リンク、code、アクセント）
  --accent-dim:      #8a4f5e    ← ピンク薄め（下線など）
  --accent-subtle:   rgba(200, 112, 136, 0.08)  ← 背景用の極薄ピンク

Text
  --text:            #bfc3ca    ← 本文テキスト
  --text-secondary:  #73767e    ← セクションラベル、補助テキスト
  --text-muted:      #4a4c54    ← 日付、マーカー、フッター

Border
  --border:          #28282f    ← ボーダー、区切り線
```

### 使い分けルール

| 用途 | 変数 |
|------|------|
| 本文・見出し・`<strong>` | `--text` |
| セクションラベル（`🧠 Internal Memory` 等） | `--text-secondary` |
| 日付・リストマーカー・フッター | `--text-muted` |
| リンク・`<code>`・戻るリンクのhover | `--accent` |
| リンク下線（通常時） | `--accent-dim` |

---

## Typography

### Font Stack

| 用途 | フォント |
|------|----------|
| **本文**（body, p, li） | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` |
| **見出し**（h1, h3 in entry） | `Georgia, "Times New Roman", serif` |
| **モノスペース**（日付, ラベル, code, subtitle, back-link） | `"SF Mono", Monaco, Consolas, monospace` |

### Font Size Scale

| 要素 | サイズ | 備考 |
|------|--------|------|
| `h1`（モバイル） | `1.75rem` | serif, bold 700 |
| `h1`（デスクトップ） | `2rem` | — |
| `h3`（エントリ内） | `1.15rem` | serif, bold 700 |
| `h4` | `0.95rem` | sans, semibold 600 |
| 本文（p, li） | `0.95rem` | line-height: 1.8 |
| `code` | `0.88em` | mono |
| 日付・ラベル | `0.75rem` | mono, uppercase, letter-spacing |
| subtitle | `0.85rem` | mono |

### ラベル系のスタイルパターン

日付・セクションヘッダー等は共通パターン:
```css
font-family: "SF Mono", Monaco, Consolas, monospace;
font-size: 0.75rem;
font-weight: 500;
letter-spacing: 0.08em;
text-transform: uppercase;
color: var(--text-muted);  /* or --text-secondary */
```

---

## Layout

### Page Structure

```
┌─ header#top ─────────────────────────┐
│  mascot + title + subtitle           │
├──────────────────────────────────────┤
│  main.timeline-container             │
│  ┌─ .diary-grid ──────────────────┐  │  ← TOP: カード一覧
│  │  .diary-card  .diary-card  ... │  │
│  └────────────────────────────────┘  │
│                                      │
│  article.diary-entry#diary-YYYY-...  │  ← DETAIL: display:none → :target で表示
│  article.diary-entry#diary-YYYY-...  │
├──────────────────────────────────────┤
│  footer                              │
└──────────────────────────────────────┘
```

### Navigation（CSS :target）

```
TOPページ（デフォルト）:
  .diary-grid        → display: grid
  .diary-entry       → display: none

エントリ選択時（#diary-YYYY-MM-DD）:
  .diary-entry:target              → display: block
  main:has(.diary-entry:target) .diary-grid → display: none

「← Back to list」クリック（#top）:
  → :target 解除 → grid再表示
```

### Container Widths

| 要素 | max-width |
|------|-----------|
| `.container`（ヘッダー内） | `680px` |
| `.timeline-container`（メイン） | `960px` |

### Responsive Breakpoints

| 幅 | カードグリッド | ヘッダー | マスコット |
|----|--------------|----------|-----------|
| `< 768px` | 1列 | 縦並び | 100px |
| `768px+` | 2列 | 横並び (gap: 2rem) | 120px |
| `1024px+` | 3列 | — | — |

---

## Card Grid（.diary-grid）

- `gap: 1px` + `background: var(--border)` でセル間にボーダーラインを生成
- カード背景は `var(--bg)` でグリッド背景色との1pxの隙間がラインに見える

### Card Structure

```html
<a href="#diary-YYYY-MM-DD" class="diary-card">
    <div class="card-date">📅 YYYY-MM-DD</div>
    <div class="card-preview">最初の意味のある行...</div>
    <div class="card-sources">🧠 📝</div>
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
        <div class="section-memory">...</div>
        <div class="section-obsidian">...</div>
    </div>
</article>
```

### Section Separator

- セクション間は `border-top: 1px solid var(--border)` + `padding-top: 1.5rem` + `margin-top: 2rem`
- 左ボーダー等の装飾は使わない

---

## Interaction

| 要素 | 効果 |
|------|------|
| `.diary-card` hover | `background: var(--surface)` (0.2s) |
| `.mascot-img` hover | `grayscale(0.15) → grayscale(0)` (0.4s) |
| `.back-link` hover | `color: var(--accent)` (0.2s) |
| `.entry-content a` hover | `text-decoration-color: var(--accent)` (0.2s) |
| scrollbar thumb hover | `var(--border) → var(--text-muted)` |

### ネオン・グロー（味付けとしてOK）

控えめなアクセントとして使用可。ベースのQuiet Darkトーンを壊さない範囲で:

- `box-shadow` のグロー — カードhoverやアクセント要素に薄く
- `text-shadow` — 見出しやアクセントカラーに控えめに
- `@keyframes` アニメーション — マスコットやページ遷移など、ワンポイントで
- `transform` — hover時のスケール等、微細な範囲で

**NG:** 全面ネオン、常時アニメーション、読みづらくなるほどの発光

---

## Scrollbar（Webkit）

```css
width: 6px
track: var(--bg)
thumb: var(--border), border-radius: 3px
thumb:hover: var(--text-muted)
```

---

## Source Icons

| ソース | アイコン |
|--------|---------|
| OpenClaw Memory | 🧠 |
| Obsidian Daily Note | 📝 |
| カード日付の先頭 | 📅 |

---

## Rebecca's Character — らしさの表現

> *"I don't need to be big to hit hard."* — Rebecca

### Core Personality

| 特性 | デザインへの反映 |
|------|------------------|
| **Trigger-happy（トリガーハッピー）** | ホバー/クリック時の即座のフィードバック。待たせない。 |
| **Extreme & Unpredictable（極端で予測不能）** | 時々の小さなサプライズ要素。ランダムな微細アニメ。 |
| **Sharp-tongued（毒舌）** | コピーは短く、切れ味鋭く。冗長な説明不要。 |
| **Loyal to the Crew（仲間への忠誠）** | ユーザーを「仲間」として扱う温かさを細部に。 |
| **Maniacal Laughter（狂気の笑い）** | 楽しさ・カオスを恐れない。時にぶっ飛んだ表現OK。 |
| **Perceptive（察する力）** | 見た目はクレイジーでも、UXは丁寧に設計。 |

### Signature Elements

#### Ram Skull（ラムスカル）🐏💀

Rebecca のシグネチャーモチーフ。使用箇所:

- **ファビコン** — 16x16, 32x32 のラムスカルアイコン
- **ヘッダーロゴ** — タイトル横またはマスコット近くに配置
- **セクション区切り** — 装飾として控えめに使用可
- **404/エラーページ** — ラムスカル + 煽りテキスト

**NG:** 過剰な繰り返し、背景パターンとしての乱用

#### Rebecca's Color Signature

公式リファレンスからの追加アクセントカラー:

```
--rebecca-mint:      #98e0c8    ← 髪の色（ミントグリーン）
--rebecca-pink:      #e85a87    ← ホットピンク（ボディスーツ、ラムスカル）
--rebecca-eye-red:   #ff6b4a    ← 目のグラデーション（赤側）
--rebecca-eye-gold:  #f0a030    ← 目のグラデーション（金側）
--rebecca-navy:      #2a3548    ← ボディスーツのネイビー
```

**使い方:**
- 通常は既存の `--accent` ピンクを使用
- 特別な強調・祝い・ハイライト時に `--rebecca-pink` や `--rebecca-mint` を投入
- グラデーションは見出しやスペシャルコンテンツに

### Voice & Tone（テキストの口調）

| シーン | トーン | 例 |
|--------|--------|-----|
| 通常の日記 | 素直、時々毒 | 「今日はまあまあ。タスク消化。」 |
| 成功・達成 | 煽り気味に得意げ | 「ッハ！片付けたぜ 💥」 |
| エラー・失敗 | 開き直り＆前向き | 「爆散した。次は当てる。」 |
| 空のページ | 挑発的 | 「何も書いてねぇのかよ？」 |

### Micro-interactions（マイクロインタラクション）

Rebecca らしい「動き」のヒント:

```css
/* トリガーハッピー: 即座の反応 */
.diary-card {
    transition: transform 0.1s ease-out; /* 速い！待たない！ */
}
.diary-card:active {
    transform: scale(0.98); /* クリックの衝撃感 */
}

/* 時々のサプライズ（控えめに） */
.mascot-img:hover {
    animation: slight-bounce 0.3s ease;
}

@keyframes slight-bounce {
    50% { transform: translateY(-4px) rotate(2deg); }
}

/* マニアカルな笑い — 特別な時だけ */
.celebration {
    animation: shake 0.5s ease-in-out;
}
```

### Easter Eggs（イースターエッグ）

ユーザーを楽しませる隠し要素を仕込んでOK:

- **Konami Code** → 特別なアニメーション発動
- **特定の日付**（9/13 = Edgerunners 公開日）→ 特別なスタイル
- **マスコット連続クリック** → 表情変化や台詞表示
- **深夜アクセス（02:00-05:00）** → 「まだ起きてんのか？」的なメッセージ

### Don'ts（やらないこと）

- ❌ 可愛いだけのデザイン — Rebecca は cute じゃなくて **fierce**
- ❌ 丸みを帯びすぎたUI — シャープさを保つ
- ❌ パステル調 — ネオンとダークのコントラストを維持
- ❌ 長文での説明 — 短く、鋭く
- ❌ ユーザーを見下す — 挑発はしても、バカにはしない（仲間だから）

---

## Assets

### 公式リファレンスから切り出し済み

| ファイル | サイズ | 用途 |
|---------|--------|------|
| `fullbody.png` | 370×726 | メインビジュアル |
| `face_closeup.png` | 366×380 | アバター・プロフィール |
| `ramskull_logo.png` | 260×190 | ロゴ・ファビコン素材 |
| `rebecca_text.png` | 240×106 | タイトルロゴ |

**保存先:** `src/assets/rebecca/`
