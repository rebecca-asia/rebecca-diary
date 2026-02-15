# エンティティ一覧 — Rebecca's Room

> *Phase 0（MVP）+ Phase 1 の全エンティティ定義*

---

## エンティティ関連図

```
┌─────────────────────────────────────────────────────────────────┐
│                      Rebecca's Room                              │
│                                                                  │
│  ┌─ External Data Sources ────────────────────────────────────┐ │
│  │  E-011 OpenClawMemoryFile ─────────┐                       │ │
│  │  E-012 ObsidianDailyNote  ─────────┤                       │ │
│  │  E-020 MacSystemMetrics   ─────────┤                       │ │
│  │  E-021 GatewayProcess     ─────────┤                       │ │
│  └────────────────────────────────────┤───────────────────────┘ │
│                                       ▼                          │
│  ┌─ Processors ───────────────────────────────────────────────┐ │
│  │  E-010 UpdateDiaryScript ──→ E-013 MarkdownConverter       │ │
│  │  E-030 HealthCollector   ──→ E-035 StateClassifier         │ │
│  │  E-031 StatusCollector   ──→ E-036 TimeContextResolver     │ │
│  └──────────┬─────────────────────────────┬───────────────────┘ │
│             ▼                             ▼                      │
│  ┌─ Data Store ───────────────────────────────────────────────┐ │
│  │  E-008 IndexHTML ←── E-010                                 │ │
│  │  E-032 HealthJSON ←── E-030                                │ │
│  │  E-033 StatusJSON ←── E-031                                │ │
│  └──────────┬─────────────────────────────┬───────────────────┘ │
│             ▼                             ▼                      │
│  ┌─ Frontend ─────────────────────────────────────────────────┐ │
│  │  E-001 DiaryWebsite                                        │ │
│  │    ├── E-005 Header                                        │ │
│  │    │     └── E-007 MascotImage                             │ │
│  │    ├── E-040 RoomStatusBar  ←── E-033                      │ │
│  │    ├── E-043 AlertDisplay   ←── E-032                      │ │
│  │    ├── E-041 HealthDashboard ←── E-032                     │ │
│  │    │     ├── E-042 HealthMetricBar × 5                     │ │
│  │    │     └── E-044 OverallScore                            │ │
│  │    ├── E-004 Timeline                                      │ │
│  │    │     └── E-002 DiaryEntry × N                          │ │
│  │    │           └── E-003 DiarySection × 2                  │ │
│  │    └── E-006 Footer                                        │ │
│  │                                                            │ │
│  │  E-009 StyleCSS    E-015 AppJS    E-016 TemplateHTML       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## エンティティ一覧

### Phase 0（MVP）エンティティ

| ID | English Name | 名称 | 種別 | 説明 |
|----|-------------|------|------|------|
| E-001 | DiaryWebsite | 日記ウェブサイト | System | Rebecca's Room 全体。静的 HTML + CSS + JS で構成 |
| E-002 | DiaryEntry | 日記エントリ | Data | 1日分の日記記事。date + sections で構成。`<article class="diary-entry">` |
| E-003 | DiarySection | 日記セクション | Data | ソース別のセクション。Memory（🧠 mint）または Obsidian（📝 accent） |
| E-004 | Timeline | タイムライン | UI | 日記エントリのカードグリッド表示。CSS Grid で1/2/3列レスポンシブ |
| E-005 | Header | ヘッダー | UI | タイトル「Rebecca's Diary」+ マスコット画像エリア |
| E-006 | Footer | フッター | UI | コピーライト表示 |
| E-007 | MascotImage | マスコット画像 | Asset | Rebecca の表情スタンプ。9種類の PNG（クリックでサイクル） |
| E-008 | IndexHTML | index.html | File | メインページ。カード一覧 + エントリ詳細を1ファイルに格納（SSG 生成） |
| E-009 | StyleCSS | style.css | File | 全スタイル定義。ダークテーマ + ネオンアクセント。14個の CSS 変数 |
| E-010 | UpdateDiaryScript | update_diary.py | Tool | SSG コア。Markdown → HTML 変換 + サイト生成 CLI（Protected File） |
| E-011 | OpenClawMemoryFile | OpenClaw メモリファイル | External | `~/.openclaw/workspace/memory/{YYYY-MM-DD}.md` |
| E-012 | ObsidianDailyNote | Obsidian デイリーノート | External | `~/Documents/Obsidian Vault/{YYYY-MM-DD}.md` |
| E-013 | MarkdownConverter | Markdown コンバータ | Process | Markdown → HTML 変換。見出し、リスト、テーブル、インライン書式対応 |
| E-014 | InsertionMarker | 挿入マーカー | Structure | `<!-- DIARY_CARDS_PLACEHOLDER -->`, `<!-- DIARY_ENTRIES_PLACEHOLDER -->` |
| E-015 | AppJS | app.js | File | フロントエンド JS。マスコットサイクル、深夜トースト、スムーズスクロール + Phase 1 Room ロジック |
| E-016 | TemplateHTML | template.html | File | SSG テンプレート。2つのプレースホルダーマーカーを含む |

### Phase 1 新規エンティティ

| ID | English Name | 名称 | 種別 | 説明 |
|----|-------------|------|------|------|
| E-020 | MacSystemMetrics | Mac システムメトリクス | External | Mac mini のハードウェア状態。CPU / Memory / Disk / Temperature / Uptime |
| E-021 | GatewayProcess | Gateway プロセス | External | `openclaw-gateway` プロセス。存在 = Rebecca が稼働中 |
| E-030 | HealthCollector | ヘルスコレクタ | Tool | `collectors/collect_health.py`。5分間隔で Mac 状態を収集 → JSON 出力 |
| E-031 | StatusCollector | ステータスコレクタ | Tool | `collectors/collect_status.py`。1分間隔で在室状況を判定 → JSON 出力 |
| E-032 | HealthJSON | health.json | Data | システムヘルスデータ。5指標 + Overall Score + Alert Level |
| E-033 | StatusJSON | status.json | Data | 在室状況データ。status + label + emoji + last_activity + time_context |
| E-034 | HealthMetric | ヘルスメトリクス | Data | 個別指標の構造体。usage_percent + state + label + message |
| E-035 | StateClassifier | 状態分類器 | Process | 数値 → 状態（state/label/message）への閾値マッピング |
| E-036 | TimeContextResolver | 時間帯判定器 | Process | 現在時刻 → 7時間帯 + メッセージバリエーション |
| E-037 | OverallScoreCalculator | 総合スコア計算器 | Process | ペナルティ加算方式でスコア（0-100）を算出 |
| E-040 | RoomStatusBar | ルームステータスバー | UI | ヘッダー直下。emoji + label + 相対時刻 + 時間帯メッセージ |
| E-041 | HealthDashboard | ヘルスダッシュボード | UI | 5指標バー + Overall Score + Rebecca のメッセージ。ホバーで数値表示 |
| E-042 | HealthMetricBar | メトリクスバー | UI | 個別指標の棒グラフ。icon + name + bar + label（hover: detail） |
| E-043 | AlertDisplay | アラート表示 | UI | Level 1-3 の段階的アラート。Rebecca の声でメッセージ |
| E-044 | OverallScore | 総合スコア表示 | UI | emoji + label + メッセージ。呼吸アニメーション付き |

---

## エンティティ詳細

### E-002 DiaryEntry（日記エントリ）

| 属性 | 型 | 説明 |
|------|-----|------|
| date | string (YYYY-MM-DD) | エントリの日付 |
| sections | DiarySection[] | Memory / Obsidian の2セクション（いずれかが空の場合あり） |
| has_content | boolean | いずれかのソースにコンテンツがあるか |

**HTML 構造:**
```html
<article class="diary-entry" id="diary-YYYY-MM-DD">
    <div class="entry-date">
        <span class="date-badge">YYYY-MM-DD</span>
        <span class="day-name">曜日</span>
    </div>
    <div class="entry-content">
        <!-- DiarySection × 1-2 -->
    </div>
</article>
```

**関連:** E-010 が E-011 + E-012 から生成、E-004 に格納

---

### E-032 HealthJSON（health.json）

| 属性 | 型 | 説明 |
|------|-----|------|
| timestamp | string (ISO 8601) | 収集時刻 |
| cpu | HealthMetric | CPU 使用率。state: idle/clear/busy/heavy/critical |
| memory | HealthMetric | メモリ使用量。state: spacious/comfortable/normal/tight/critical |
| disk | HealthMetric | ディスク使用量。state: spacious/normal/tight/critical |
| temperature | HealthMetric \| null | CPU 温度（オプショナル）。state: cool/comfortable/warm/hot/critical |
| uptime | UptimeMetric | 稼働時間。seconds + display + state: fresh/normal/tired/exhausted |
| overall | OverallScore | 総合スコア（0-100）+ state + emoji + label + message |
| alert_level | int (0-3) | アラートレベル |

**生成元:** E-030 (HealthCollector) が E-020 (MacSystemMetrics) から5分ごとに生成
**消費先:** E-015 (AppJS) が `fetch('/data/health.json')` で読み取り → E-041, E-043 を更新

---

### E-033 StatusJSON（status.json）

| 属性 | 型 | 説明 |
|------|-----|------|
| timestamp | string (ISO 8601) | 収集時刻 |
| status | enum | `online` / `away` / `sleeping` / `offline` |
| label | string | 日本語ラベル（「ここにいるよ」等） |
| emoji | string | ステータス絵文字（🟢 / 🟡 / 💤 / ⚫） |
| last_activity | string (ISO 8601) | 最終活動時刻 |
| activity_type | string | 活動種別（diary_update, memory_write 等） |
| gateway_alive | boolean | Gateway プロセスの生存状態 |
| time_context | object | period (7種) + message (日本語、バリエーションあり) |

**Status 判定ルール:**

| Status | Emoji | Label | 条件 |
|--------|-------|-------|------|
| online | 🟢 | ここにいるよ | Gateway alive & last_activity < 30min |
| away | 🟡 | ちょっと離れてる | Gateway alive & 30min < last_activity < 2h |
| sleeping | 💤 | 寝てる...... | deep_night (02:00-06:00) & last_activity > 1h |
| offline | ⚫ | いない...... | Gateway dead OR last_activity > 2h |

**生成元:** E-031 (StatusCollector) が E-021 + E-011 の mtime から1分ごとに生成
**消費先:** E-015 (AppJS) が `fetch('/data/status.json')` で読み取り → E-040 を更新

---

### E-034 HealthMetric（ヘルスメトリクス構造体）

| 属性 | 型 | 説明 |
|------|-----|------|
| usage_percent | float | 使用率（0-100）。Disk は used_gb/total_gb も含む |
| state | string | 状態コード（閾値テーブルで決定） |
| label | string | 日本語状態ラベル（「クリア」「スッキリ」等） |
| message | string \| null | Rebecca のコメント（状態に応じて） |

**閾値テーブル:**

| Metric | States | Thresholds |
|--------|--------|-----------|
| CPU | idle, clear, busy, heavy, critical | 0-20%, 20-50%, 50-70%, 70-85%, 85%+ |
| Memory | spacious, comfortable, normal, tight, critical | 0-50%, 50-60%, 60-80%, 80-95%, 95%+ |
| Disk | spacious, normal, tight, critical | 0-50%, 50-80%, 80-95%, 95%+ |
| Temperature | cool, comfortable, warm, hot, critical | 0-40, 40-55, 55-70, 70-80, 80+ °C |
| Uptime | fresh, normal, tired, exhausted | 0-1d, 1-3d, 3-7d, 7d+ |

---

### E-040 RoomStatusBar（ルームステータスバー）

| 属性 | 型 | 説明 |
|------|-----|------|
| data-status | enum | loading / online / away / sleeping / offline |
| statusEmoji | string | ステータス絵文字 |
| statusLabel | string | 日本語ラベル |
| statusTime | string | 相対時刻（「3分前」等）。hover で絶対時刻 |
| statusContext | string \| null | 時間帯メッセージ |

**配置:** `<header>` と `<main>` の間
**データソース:** E-033 (StatusJSON)
**更新:** E-015 (AppJS) の `renderStatusBar()` が5分間隔で更新

---

### E-041 HealthDashboard（ヘルスダッシュボード）

| 属性 | 型 | 説明 |
|------|-----|------|
| health-title | string | 「Rebecca の体調」 |
| metrics | HealthMetricBar[5] | CPU, Memory, Disk, Temperature, Uptime |
| overall | OverallScore | 総合スコア表示（呼吸アニメーション付き） |

**配置:** RoomStatusBar の直下、Timeline の上
**データソース:** E-032 (HealthJSON)
**レイアウト:**
- デスクトップ: 全指標を縦に表示（max-width: 960px）
- モバイル: Overall Score のみ表示（タップで展開）

---

## アクター一覧

| ID | Actor | 説明 |
|----|-------|------|
| A-001 | Viewer（閲覧者） | ブラウザで Room を閲覧する人 |
| A-002 | Admin（管理者 / Takeru） | 日記の追加、サーバー起動、設定変更を行う人 |
| A-003 | UpdateDiaryScript | SSG スクリプト（自動実行） |
| A-004 | HealthCollector | ヘルスデータ収集スクリプト（cron 5分間隔） |
| A-005 | StatusCollector | ステータス収集スクリプト（cron 1分間隔） |
| A-006 | AppJS | フロントエンド JS（ブラウザ上で fetch + render） |

---

## エンティティ × Phase マトリクス

| Entity | Phase 0 | Phase 1 | 備考 |
|--------|:-------:|:-------:|------|
| E-001 DiaryWebsite | ✅ | ✅ | 拡張 |
| E-002 DiaryEntry | ✅ | ✅ | 変更なし |
| E-003 DiarySection | ✅ | ✅ | 変更なし |
| E-004 Timeline | ✅ | ✅ | 変更なし |
| E-005 Header | ✅ | ✅ | 変更なし |
| E-006 Footer | ✅ | ✅ | 変更なし |
| E-007 MascotImage | ✅ | ✅ | 変更なし |
| E-008 IndexHTML | ✅ | ✅ | Room コンポーネント追加 |
| E-009 StyleCSS | ✅ | ✅ | Room スタイル追加 |
| E-010 UpdateDiaryScript | ✅ | ✅ | Protected（変更なし） |
| E-011 OpenClawMemoryFile | ✅ | ✅ | StatusCollector も mtime 参照 |
| E-012 ObsidianDailyNote | ✅ | ✅ | 変更なし |
| E-013 MarkdownConverter | ✅ | ✅ | 変更なし |
| E-014 InsertionMarker | ✅ | ✅ | 変更なし |
| E-015 AppJS | ✅ | ✅ | Room ロジック追加 |
| E-016 TemplateHTML | ✅ | ✅ | Room コンポーネント追加 |
| E-020 MacSystemMetrics | — | ✅ | 新規 |
| E-021 GatewayProcess | — | ✅ | 新規 |
| E-030 HealthCollector | — | ✅ | 新規 |
| E-031 StatusCollector | — | ✅ | 新規 |
| E-032 HealthJSON | — | ✅ | 新規 |
| E-033 StatusJSON | — | ✅ | 新規 |
| E-034 HealthMetric | — | ✅ | 新規 |
| E-035 StateClassifier | — | ✅ | 新規 |
| E-036 TimeContextResolver | — | ✅ | 新規 |
| E-037 OverallScoreCalculator | — | ✅ | 新規 |
| E-040 RoomStatusBar | — | ✅ | 新規 |
| E-041 HealthDashboard | — | ✅ | 新規 |
| E-042 HealthMetricBar | — | ✅ | 新規 |
| E-043 AlertDisplay | — | ✅ | 新規 |
| E-044 OverallScore | — | ✅ | 新規 |

**合計: 31 エンティティ（Phase 0: 16 + Phase 1 新規: 15）**

---

## 関連ドキュメント

| Document | 関係 |
|----------|------|
| [SPEC.md](../phases/phase1/SPEC.md) | JSON スキーマ、閾値テーブル |
| [WBS.md](../phases/phase1/WBS.md) | 各エンティティを実装する WP |
| [USE_CASE_LIST.md](USE_CASE_LIST.md) | エンティティを操作するユースケース |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Phase 0 の詳細構成 |
| [archive/phase0/ENTITY_LIST.md](../archive/phase0/ENTITY_LIST.md) | Phase 0 版（歴史的記録） |

---

*Created: 2026-02-13*
*Phase 0 + Phase 1 — 31 エンティティ。Rebecca の身体と部屋を構成する全要素。*
