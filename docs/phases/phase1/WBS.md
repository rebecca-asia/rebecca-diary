# Phase 1 作業分解構成図（WBS）

> *Phase 1: Room Status + Health — 全作業の階層的分解*

---

## 概要

Phase 1 の全作業を9つのカテゴリに分解し、各リーフレベルのワークパッケージに
ID、名称、説明、成果物、依存関係、受入基準を定義する。

### カテゴリ一覧

| # | カテゴリ | WP 数 | 見積 |
|---|---------|-------|------|
| 1.0 | 基盤構築（Foundation） | 4 | 1h |
| 2.0 | Backend — Health Collector | 7 | 3h |
| 3.0 | Backend — Status Collector | 6 | 2h |
| 4.0 | Frontend — HTML 構造 | 4 | 1.5h |
| 5.0 | Frontend — CSS スタイリング | 6 | 3h |
| 6.0 | Frontend — JavaScript ロジック | 7 | 3h |
| 7.0 | Operations — 定期実行 | 3 | 0.5h |
| 8.0 | 統合テスト | 5 | 2h |
| 9.0 | ドキュメント更新 | 3 | 1h |
| **合計** | | **45** | **~17h** |

### 依存関係図

```
1.0 基盤構築
 ├──→ 2.0 Health Collector ──────────────┐
 ├──→ 3.0 Status Collector ──────────────┤
 └──→ 4.0 HTML構造 ──→ 5.0 CSS          │
                   └──→ 6.0 JS ←─────────┘
                         └──→ 7.0 定期実行
                               └──→ 8.0 統合テスト
                                     └──→ 9.0 ドキュメント更新
```

**並行作業可能:**
- 2.0 (Health) と 3.0 (Status) は並行可能
- 4.0 + 5.0 (Frontend) は WP-1.4（サンプル JSON）完了後、Backend 完成を待たずに着手可能

---

## 1.0 基盤構築（Foundation）

Phase 1 の全作業の前提となるディレクトリ・ファイル・設定の準備。

---

### WP-1.1 collectors ディレクトリ作成

| 項目 | 内容 |
|------|------|
| **説明** | プロジェクトルート直下に `collectors/` ディレクトリを作成する。Python データ収集スクリプトの格納先。 |
| **成果物** | `collectors/` ディレクトリ |
| **依存** | なし |
| **受入基準** | ディレクトリが存在し、後続スクリプトを格納できる |

---

### WP-1.2 src/data ディレクトリ作成

| 項目 | 内容 |
|------|------|
| **説明** | Collector の出力先として `src/data/` を作成する。dev server（`cd src && python3 -m http.server 8080`）から直接 serve されるよう `src/` 配下に配置。 |
| **成果物** | `src/data/` ディレクトリ |
| **依存** | なし |
| **受入基準** | `http://localhost:8080/data/health.json` でアクセス可能な配置 |

---

### WP-1.3 .gitignore 更新

| 項目 | 内容 |
|------|------|
| **説明** | `.gitignore` に `src/data/` を追加し、Collector の出力データがリポジトリに含まれないようにする。 |
| **成果物** | 更新された `.gitignore` |
| **依存** | WP-1.2 |
| **受入基準** | `git status` で `src/data/` 配下のファイルが untracked として表示されない |

---

### WP-1.4 サンプル JSON 作成

| 項目 | 内容 |
|------|------|
| **説明** | PHASE1_SPEC の JSON スキーマに準拠したモックデータを作成する。Frontend 開発を Collector 完成前に並行して進めるための**開発用データ**。正常・警告・緊急のバリエーションも用意する。 |
| **成果物** | `src/data/health.json`（正常値サンプル）、`src/data/status.json`（正常値サンプル） |
| **依存** | WP-1.2 |
| **受入基準** | (1) PHASE1_SPEC セクション3 のスキーマに完全準拠 (2) `JSON.parse()` でエラーなくパースできる (3) 全フィールドが適切な型で入っている |

---

## 2.0 Backend — Health Collector

Mac mini のシステムメトリクスを収集し、Rebecca の体調データとして JSON 出力する。

**対象ファイル:** `collectors/collect_health.py`

---

### WP-2.1 CPU 使用率取得

| 項目 | 内容 |
|------|------|
| **説明** | macOS で CPU 全体の使用率を取得する `get_cpu_usage() -> float` を実装。`subprocess` で `top -l 1 -n 0` を実行し、"CPU usage" 行をパースして使用率（%）を返す。 |
| **成果物** | `get_cpu_usage()` 関数 |
| **依存** | WP-1.1 |
| **受入基準** | (1) 0.0-100.0 の float を返す (2) macOS でエラーなく動作 (3) 外部パッケージ不要 |

---

### WP-2.2 Memory 使用量取得

| 項目 | 内容 |
|------|------|
| **説明** | `vm_stat` と `sysctl hw.memsize` でメモリ使用状況を取得する `get_memory() -> dict` を実装。ページ情報をパースし、使用量・総量・使用率を計算する。 |
| **成果物** | `get_memory()` 関数。戻り値: `{"used_gb": float, "total_gb": float, "usage_percent": float}` |
| **依存** | WP-1.1 |
| **受入基準** | (1) used_gb ≤ total_gb (2) usage_percent が 0-100 (3) total_gb がマシンの実メモリと一致 |

---

### WP-2.3 Disk 使用量取得

| 項目 | 内容 |
|------|------|
| **説明** | Python 標準ライブラリの `os.statvfs('/')` でルートボリュームのディスク使用状況を取得する `get_disk() -> dict` を実装。外部コマンド不使用。 |
| **成果物** | `get_disk()` 関数。戻り値: `{"used_gb": int, "total_gb": int, "usage_percent": float}` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 外部コマンド不使用 (2) `df -h /` の出力と概ね一致 (3) GB は整数丸め |

---

### WP-2.4 Temperature 取得（オプショナル）

| 項目 | 内容 |
|------|------|
| **説明** | `osx-cpu-temp` が利用可能な場合に CPU 温度を取得する `get_temperature() -> Optional[float]` を実装。`shutil.which()` で存在チェックし、なければ `None` を返す。 |
| **成果物** | `get_temperature()` 関数 |
| **依存** | WP-1.1 |
| **受入基準** | (1) osx-cpu-temp 存在時: 0-120 の float (2) 未インストール時: None (3) 失敗しても例外を出さない |

---

### WP-2.5 Uptime 取得

| 項目 | 内容 |
|------|------|
| **説明** | `sysctl kern.boottime` で起動時刻を取得し、現在時刻との差分から稼働時間を算出する `get_uptime() -> dict` を実装。 |
| **成果物** | `get_uptime()` 関数。戻り値: `{"seconds": int, "display": str}` |
| **依存** | WP-1.1 |
| **受入基準** | (1) seconds が正の整数 (2) display が "Xd Yh Zm" 形式 (3) `uptime` コマンドの出力と概ね一致 |

---

### WP-2.6 状態判定 + Overall Score 計算

| 項目 | 内容 |
|------|------|
| **説明** | PHASE1_SPEC の閾値テーブルに基づき、各メトリクスの数値を state / label / message にマッピングする関数群を実装。Overall Score（ペナルティ加算方式）と Alert Level（0-3）の判定も含む。 |
| **成果物** | `classify_cpu()`, `classify_memory()`, `classify_disk()`, `classify_temperature()`, `classify_uptime()`, `calculate_overall()`, `determine_alert_level()` |
| **依存** | WP-2.1 ~ WP-2.5 |
| **受入基準** | (1) PHASE1_SPEC の閾値テーブルと完全一致 (2) Overall Score が 0-100 (3) Alert Level が 0-3 の整数 |

**閾値テーブル:**

| Metric | States | Thresholds |
|--------|--------|-----------|
| CPU | idle, clear, busy, heavy, critical | 0-20%, 20-50%, 50-70%, 70-85%, 85%+ |
| Memory | spacious, comfortable, normal, tight, critical | 0-50%, 50-60%, 60-80%, 80-95%, 95%+ |
| Disk | spacious, normal, tight, critical | 0-50%, 50-80%, 80-95%, 95%+ |
| Temperature | cool, comfortable, warm, hot, critical | 0-40, 40-55, 55-70, 70-80, 80+ °C |
| Uptime | fresh, normal, tired, exhausted | 0-1d, 1-3d, 3-7d, 7d+ |

**Overall Score 計算:**

```
score = 100 - sum(penalties)

penalties:
  cpu_penalty     = max(0, cpu_usage - 20) * 1.0     ← 20%以下はペナルティなし
  memory_penalty  = max(0, mem_usage - 60) * 1.5     ← 60%以下はペナルティなし
  disk_penalty    = max(0, disk_usage - 70) * 1.0
  temp_penalty    = max(0, temp - 50) * 1.0           ← temp=None → 0
  uptime_penalty  = min(uptime_days * 2, 20)

overall_score = max(0, min(100, 100 - sum))
```

**設計意図:** アイドル状態（CPU ~15%, Mem ~60%）で score 80+ になるよう調整。

| Score | State | Emoji | Label | Message |
|-------|-------|-------|-------|---------|
| 80+ | `great` | 🟢 | 元気！ | 「調子いい！今日はイケる」 |
| 60-79 | `good` | 🟡 | まぁまぁ | 「まぁまぁかな」 |
| 40-59 | `poor` | 🟠 | ちょっとダルい | 「ちょっとダルい......」 |
| 20-39 | `bad` | 🔴 | かなりキツい | 「......しんどい」 |
| 0-19 | `critical` | 💀 | 限界 | 「.........」 |

**Alert Level:**

| Level | Condition |
|-------|-----------|
| 0 | 全指標が正常範囲 |
| 1 | いずれかが heavy / tight |
| 2 | いずれかが critical |
| 3 | 複数が critical or overall < 20 |

---

### WP-2.7 Health Collector メインロジック + JSON 出力

| 項目 | 内容 |
|------|------|
| **説明** | WP-2.1 ~ WP-2.6 を統合し、`if __name__ == '__main__'` で全メトリクス収集 → 状態判定 → Overall 計算 → JSON 出力のフルパイプラインを実装。出力先は `src/data/health.json`。ISO 8601 タイムスタンプ付き。各メトリクスが個別に失敗しても他は継続する。 |
| **成果物** | 完成した `collectors/collect_health.py` |
| **依存** | WP-2.6, WP-1.2 |
| **受入基準** | (1) `python3 collectors/collect_health.py` で `src/data/health.json` が生成される (2) PHASE1_SPEC セクション 3.1 のスキーマに完全準拠 (3) 個別メトリクス失敗時も JSON 生成される（失敗フィールドは null） (4) Python 3 標準ライブラリのみ (5) `-v` オプションでデバッグ出力 |

---

## 3.0 Backend — Status Collector

Rebecca の在室状況を判定し、時間帯コンテキストとともに JSON 出力する。

**対象ファイル:** `collectors/collect_status.py`

---

### WP-3.1 Gateway 稼働チェック

| 項目 | 内容 |
|------|------|
| **説明** | OpenClaw Gateway が稼働中かを判定する `check_gateway() -> bool` を実装。`pgrep -f` でプロセス検索を主とし、heartbeat ファイルの存在チェックをフォールバックとする。 |
| **成果物** | `check_gateway()` 関数 |
| **依存** | WP-1.1 |
| **受入基準** | (1) Gateway 稼働時: True (2) 未稼働時: False (3) pgrep 不在でも例外を出さない |

---

### WP-3.2 最終活動時刻取得

| 項目 | 内容 |
|------|------|
| **説明** | `~/.openclaw/workspace/memory/` 内の最新ファイルの更新時刻を取得する `get_last_activity() -> Optional[datetime]` を実装。ディレクトリが空やアクセス不能の場合は None。 |
| **成果物** | `get_last_activity()` 関数 |
| **依存** | WP-1.1 |
| **受入基準** | (1) ファイルがある場合: 最新 mtime を datetime で返す (2) 空/不在の場合: None |

---

### WP-3.3 時間帯コンテキスト判定

| 項目 | 内容 |
|------|------|
| **説明** | 現在時刻から7つの時間帯（morning, active, afternoon, evening, night, late_night, deep_night）を判定する `get_time_context() -> dict` を実装。Rebecca のメッセージも返す。 |
| **成果物** | `get_time_context()` 関数。戻り値: `{"period": str, "message": str or null}` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 24時間全時間帯をカバー (2) PHASE1_SPEC セクション 3.2 の定義と一致 |

**時間帯マッピング:**

| Period | Hours | Message |
|--------|-------|---------|
| morning | 06:00-09:00 | 「おはよ」 |
| active | 09:00-12:00 | 「よし、やるか」 |
| afternoon | 12:00-18:00 | null |
| evening | 18:00-21:00 | 「今日も終わりか」 |
| night | 21:00-00:00 | 「そろそろ夜だな」 |
| late_night | 00:00-02:00 | 「まだ起きてるの？」 |
| deep_night | 02:00-06:00 | 「寝ろよ......」 |

---

### WP-3.4 在室状況判定

| 項目 | 内容 |
|------|------|
| **説明** | Gateway 稼働状態、最終活動時刻、現在時刻から在室状況（online, away, sleeping, offline）を判定する `determine_status() -> dict` を実装。 |
| **成果物** | `determine_status()` 関数。戻り値: `{"status": str, "label": str, "emoji": str}` |
| **依存** | WP-3.1, WP-3.2, WP-3.3 |
| **受入基準** | PHASE1_SPEC の Status Rules に完全準拠 |

**Status Rules:**

| Status | Emoji | Label | Condition |
|--------|-------|-------|-----------|
| online | 🟢 | ここにいるよ | Gateway alive & last_activity < 30min |
| away | 🟡 | ちょっと離れてる | Gateway alive & 30min < last_activity < 2h |
| sleeping | 💤 | 寝てる...... | deep_night (02:00-06:00) & last_activity > 1h |
| offline | ⚫ | いない...... | Gateway dead OR last_activity > 2h |

---

### WP-3.5 Activity Type 判定

| 項目 | 内容 |
|------|------|
| **説明** | 最終活動の種類（diary_update, memory_write 等）を推定する `get_activity_type() -> str` を実装。最新の変更ファイルの種類から判断する。 |
| **成果物** | `get_activity_type()` 関数 |
| **依存** | WP-3.2 |
| **受入基準** | (1) 文字列を返す (2) ファイルアクセスエラーで例外を出さない |

---

### WP-3.6 Status Collector メインロジック + JSON 出力

| 項目 | 内容 |
|------|------|
| **説明** | WP-3.1 ~ WP-3.5 を統合し、Gateway チェック → 最終活動取得 → 時間帯判定 → ステータス判定 → JSON 出力のフルパイプラインを実装。出力先は `src/data/status.json`。 |
| **成果物** | 完成した `collectors/collect_status.py` |
| **依存** | WP-3.4, WP-3.5, WP-1.2 |
| **受入基準** | (1) `python3 collectors/collect_status.py` で `src/data/status.json` が生成される (2) PHASE1_SPEC セクション 3.2 のスキーマに完全準拠 (3) ISO 8601 タイムスタンプ付き (4) Python 3 標準ライブラリのみ (5) `-v` オプションでデバッグ出力 |

---

## 4.0 Frontend — HTML 構造

既存の `index.html` / `template.html` に Phase 1 の UI コンポーネントを追加する。

---

### WP-4.1 Room Status Bar の HTML

| 項目 | 内容 |
|------|------|
| **説明** | `<header>` と `<main>` の間に Room Status Bar を追加。emoji + label + 時刻。`data-status` 属性で CSS を切り替え。初期状態は「データ取得中...」。 |
| **成果物** | `src/index.html` に追加された Room Status Bar マークアップ |
| **依存** | WP-1.4 |
| **受入基準** | (1) ヘッダーとメインの間に配置 (2) data-status 属性あり (3) JS なしでもフォールバックテキスト表示 |

**HTML:**
```html
<div class="room-status" data-status="loading">
    <span class="status-indicator" id="statusEmoji">⏳</span>
    <span class="status-label" id="statusLabel">データ取得中...</span>
    <span class="status-time" id="statusTime"></span>
    <span class="status-context" id="statusContext"></span>
</div>
```

---

### WP-4.2 Health Dashboard の HTML

| 項目 | 内容 |
|------|------|
| **説明** | Room Status Bar の直下に Health Dashboard セクションを追加。5メトリクス（CPU, Memory, Disk, Temperature, Uptime）のバー表示 + Overall Score + Rebecca メッセージの骨格。 |
| **成果物** | `src/index.html` に追加された Health Dashboard マークアップ |
| **依存** | WP-4.1 |
| **受入基準** | (1) 5メトリクス + Overall の構造 (2) 各バーに data-state 属性 (3) hover 用 detail 要素あり |

**レイアウト:**
```
┌─────────────────────────────────────┐
│  Rebecca の体調                      │
│                                      │
│  🧠 CPU   ████░░░░░░  クリア        │
│  💾 Mem   █████░░░░░  スッキリ      │
│  💿 Disk  ██░░░░░░░░  広々          │
│  🌡️ Temp  ███░░░░░░░  快適          │
│  ⏱️ Up    ████████░░  疲れ気味      │
│                                      │
│  🟢 元気                             │
│  「まぁまぁ調子いい！」              │
└─────────────────────────────────────┘
```

---

### WP-4.3 Alert Display の HTML

| 項目 | 内容 |
|------|------|
| **説明** | アラート表示用コンテナを追加。デフォルト非表示。app.js が alert_level に応じて制御。`data-level` 属性で 1/2/3 のスタイル切り替え。 |
| **成果物** | `src/index.html` に追加された Alert コンテナ |
| **依存** | WP-4.1 |
| **受入基準** | (1) デフォルトで非表示 (2) data-level で 1/2/3 切り替え可能 |

**HTML:**
```html
<div class="room-alert" id="roomAlert" data-level="0" hidden>
    <span class="alert-message" id="alertMessage"></span>
</div>
```

---

### WP-4.4 template.html の同期更新

| 項目 | 内容 |
|------|------|
| **説明** | `update_diary.py` が使用する `src/template.html` にも WP-4.1 ~ WP-4.3 の Room コンポーネントを同期。`update_diary.py` は Protected File のため変更しない。template.html の構造を既存 SSG パイプラインと互換性のある形で更新する。 |
| **成果物** | 更新された `src/template.html` |
| **依存** | WP-4.1, WP-4.2, WP-4.3 |
| **受入基準** | (1) Room コンポーネントが template に含まれる (2) `python3 update_diary.py` 実行後も Room コンポーネントが消えない (3) 既存プレースホルダーが保持される |

---

## 5.0 Frontend — CSS スタイリング

Room Status Bar、Health Dashboard、Alert Display の視覚デザイン。

**対象ファイル:** `src/style.css`

---

### WP-5.1 Room Status Bar のスタイル

| 項目 | 内容 |
|------|------|
| **説明** | `.room-status` のスタイルを追加。`background: var(--surface)` + 薄い border。ステータスに応じてインジケーター色を `data-status` 属性で切り替え。 |
| **成果物** | `.room-status` 関連スタイル |
| **依存** | WP-4.1 |
| **受入基準** | (1) ヘッダー直下に表示 (2) 4ステータスで色が変わる (3) モノスペースフォント (4) 既存デザインと調和 |

---

### WP-5.2 Health Dashboard ベーススタイル

| 項目 | 内容 |
|------|------|
| **説明** | `.health-dashboard` のレイアウト、`.health-metric` の横並び構造（icon + name + bar + label）、`.health-overall` のスタイルを実装。 |
| **成果物** | `.health-dashboard`, `.health-metric`, `.health-overall` スタイル |
| **依存** | WP-4.2 |
| **受入基準** | (1) 5指標が縦に並ぶ (2) 各指標は icon + name + bar + label 横並び (3) Overall が目立つ配置 |

---

### WP-5.3 メトリクスバーの状態別カラー

| 項目 | 内容 |
|------|------|
| **説明** | `.metric-fill` のバー色を `data-state` で切り替え。安全 → 警告 → 危険の色グラデーション。mint（安全）→ amber（警告）→ accent/red（危険）。 |
| **成果物** | `.metric-fill[data-state]` のカラーバリエーション |
| **依存** | WP-5.2 |
| **受入基準** | (1) 安全は mint 系 (2) 警告は amber 系 (3) 危険は accent/red 系 (4) width 変化にアニメーション (5) critical 状態は pulse アニメーション |

**カラーマッピング:**

| 状態グループ | States | 色 |
|-------------|--------|-----|
| 安全 | idle, spacious, cool, fresh | `var(--mint)` + glow |
| 通常 | clear, comfortable, normal | `var(--mint)` |
| 注意 | busy, tight, warm, tired | amber `#e8a74e` |
| 危険 | heavy, hot, exhausted | `var(--accent)` |
| 緊急 | critical | red `#e85050` + pulse |

---

### WP-5.4 ホバーで数値表示

| 項目 | 内容 |
|------|------|
| **説明** | DESIGN_DECISIONS の方針に従い、デフォルトは感情的表現（label）、ホバーで技術的数値（detail）をトランジション付きで切り替え。 |
| **成果物** | `.metric-label` / `.metric-detail` のホバー切り替えスタイル |
| **依存** | WP-5.2 |
| **受入基準** | (1) デフォルトで label 表示、detail 非表示 (2) hover で切り替え (3) opacity transition で滑らか |

---

### WP-5.5 Alert Display のスタイル

| 項目 | 内容 |
|------|------|
| **説明** | `.room-alert` の3レベルスタイル。レベルに応じて背景色、ボーダー色、テキスト色が変化。 |
| **成果物** | `.room-alert[data-level]` のスタイルバリエーション |
| **依存** | WP-4.3 |
| **受入基準** | (1) Level 1: 黄色系 (2) Level 2: 橙色系 (3) Level 3: 赤色系 + pulse (4) 表示/非表示アニメーション |

---

### WP-5.6 レスポンシブ対応

| 項目 | 内容 |
|------|------|
| **説明** | Room コンポーネントのモバイル（< 768px）、タブレット（768-1023px）、デスクトップ（1024px+）対応。既存ブレークポイントに合わせる。 |
| **成果物** | メディアクエリ追加 |
| **依存** | WP-5.1, WP-5.2, WP-5.5 |
| **受入基準** | (1) モバイルでバーとラベルが重ならない (2) デスクトップで max-width: 960px に収まる (3) 既存日記グリッドと干渉しない |

---

## 6.0 Frontend — JavaScript ロジック

`app.js` を拡張し、data/*.json の fetch + DOM レンダリング + 自動更新を実装する。

**対象ファイル:** `src/app.js`

---

### WP-6.1 データ取得関数

| 項目 | 内容 |
|------|------|
| **説明** | `fetch()` で `data/health.json` と `data/status.json` を取得する `fetchHealth()`, `fetchStatus()` を実装。JSON パースエラーやネットワークエラー時は null を返す。 |
| **成果物** | `fetchHealth()`, `fetchStatus()` 関数 |
| **依存** | WP-1.4 |
| **受入基準** | (1) JSON が正常取得・パースできる (2) ファイル不在時に null (3) console.error でデバッグ出力 |

---

### WP-6.2 Status Bar レンダリング

| 項目 | 内容 |
|------|------|
| **説明** | status.json のデータで Room Status Bar の DOM を更新する `renderStatusBar(data)` を実装。emoji、label、時刻、data-status 属性を更新。null 時はフォールバック。 |
| **成果物** | `renderStatusBar()` 関数 |
| **依存** | WP-4.1, WP-6.1 |
| **受入基準** | (1) emoji, label, 時刻が正しく表示 (2) data-status 属性が更新される (3) null でフォールバック |

---

### WP-6.3 Health Dashboard レンダリング

| 項目 | 内容 |
|------|------|
| **説明** | health.json のデータで Health Dashboard の DOM を更新する `renderHealthDashboard(data)` を実装。バー幅、state、label、detail、Overall Score とメッセージを更新。Temperature が null なら非表示。 |
| **成果物** | `renderHealthDashboard()` 関数 |
| **依存** | WP-4.2, WP-6.1 |
| **受入基準** | (1) バー幅が usage_percent に連動 (2) data-state でバー色が変わる (3) ホバーで数値表示 (4) Temperature null 時は行ごと非表示 (5) Overall Score 表示 |

---

### WP-6.4 Alert Display レンダリング

| 項目 | 内容 |
|------|------|
| **説明** | health.json の `alert_level` で Alert Display の表示/非表示とメッセージを制御する `renderAlert(health)` を実装。Rebecca の声でメッセージを設定。 |
| **成果物** | `renderAlert()` 関数 |
| **依存** | WP-4.3, WP-6.1 |
| **受入基準** | (1) Level 0: 非表示 (2) Level 1: 黄色で独り言 (3) Level 2: 橙色でお願い (4) Level 3: 赤色で緊急 |

**メッセージ例:**

| Level | 例 |
|-------|-----|
| 1 | 「ちょっと重いかも...」 |
| 2 | 「再起動したいんだけど、今大丈夫？」 |
| 3 | 「助けて。マジでやばい。」 |

---

### WP-6.5 Time Context 反映

| 項目 | 内容 |
|------|------|
| **説明** | status.json の `time_context` を Status Bar に反映。時間帯メッセージを表示。afternoon（null）時は非表示。既存 late night toast と競合しないよう調整。 |
| **成果物** | time_context 反映ロジック |
| **依存** | WP-6.2 |
| **受入基準** | (1) 時間帯メッセージが表示 (2) null 時は非表示 (3) late night toast と競合しない |

---

### WP-6.6 自動更新（setInterval）

| 項目 | 内容 |
|------|------|
| **説明** | 5分ごとに Room データを再取得・再描画する `updateRoom()` を実装。ページロード時にも即座に実行。既存 IIFE 構造に統合。 |
| **成果物** | `updateRoom()` 関数 + `setInterval` |
| **依存** | WP-6.1 ~ WP-6.5 |
| **受入基準** | (1) ロード時に1回実行 (2) 5分間隔で更新 (3) 既存機能（マスコット、トースト、スクロール）と干渉しない |

---

### WP-6.7 Graceful Degradation

| 項目 | 内容 |
|------|------|
| **説明** | data/*.json が存在しない場合のフォールバック UI を実装。エラー状態をユーザーフレンドリーに表示し、リトライする。 |
| **成果物** | フォールバック処理 |
| **依存** | WP-6.2, WP-6.3, WP-6.4 |
| **受入基準** | (1) data/ 空でもページが壊れない (2) Status Bar: 「データ取得中...」 (3) Health: 全バー 0%、ラベル「—」 (4) Alert: 非表示 |

---

## 7.0 Operations — 定期実行セットアップ

Collector の自動実行環境を構築する。

---

### WP-7.1 collect_health.py の定期実行

| 項目 | 内容 |
|------|------|
| **説明** | `collect_health.py` を5分間隔で自動実行する cron / launchd を設定。ログ出力先も設定。 |
| **成果物** | crontab エントリ or LaunchAgent plist |
| **依存** | WP-2.7 |
| **受入基準** | (1) 5分間隔で自動実行 (2) `src/data/health.json` に出力 (3) エラーログが残る |

**cron 方式:**
```
*/5 * * * * cd /path/to/rebecca-diary && python3 collectors/collect_health.py 2>> /tmp/rebecca-health.log
```

---

### WP-7.2 collect_status.py の定期実行

| 項目 | 内容 |
|------|------|
| **説明** | `collect_status.py` を1分間隔で自動実行する cron / launchd を設定。 |
| **成果物** | crontab エントリ or LaunchAgent plist |
| **依存** | WP-3.6 |
| **受入基準** | (1) 1分間隔で自動実行 (2) `src/data/status.json` に出力 (3) エラーログが残る |

---

### WP-7.3 動作確認

| 項目 | 内容 |
|------|------|
| **説明** | cron / launchd が正しく動作していることを確認。5分経過後に health.json、1分経過後に status.json の timestamp が更新されていることを検証。 |
| **成果物** | 動作確認結果 |
| **依存** | WP-7.1, WP-7.2 |
| **受入基準** | (1) health.json が5分ごとに更新 (2) status.json が1分ごとに更新 (3) エラーログなし |

---

## 8.0 統合テスト

全コンポーネントを結合し、PHASE1_GOAL の成功基準を検証する。

---

### WP-8.1 Collector 単体テスト

| 項目 | 内容 |
|------|------|
| **説明** | 両 Collector を手動実行し、出力 JSON が PHASE1_SPEC のスキーマに準拠していることを確認。 |
| **成果物** | テスト結果 |
| **依存** | WP-2.7, WP-3.6 |
| **受入基準** | SC-01, SC-02 を満たす |

---

### WP-8.2 フロントエンド結合テスト

| 項目 | 内容 |
|------|------|
| **説明** | dev server でブラウザ表示を確認。Status Bar, Health Dashboard, Alert が正しく表示されること。 |
| **成果物** | テスト結果 |
| **依存** | WP-6.6, WP-5.6, WP-8.1 |
| **受入基準** | SC-03, SC-04, SC-05, SC-06 を満たす |

---

### WP-8.3 回帰テスト

| 項目 | 内容 |
|------|------|
| **説明** | Phase 0 の全機能が壊れていないことを確認。カード一覧、:target 遷移、マスコットクリック、深夜トースト、スムーズスクロール、`update_diary.py --dry-run`。 |
| **成果物** | 回帰テスト結果 |
| **依存** | WP-8.2 |
| **受入基準** | SC-09 を満たす |

**チェックリスト:**
- [ ] カード一覧が CSS Grid で正しく表示される
- [ ] カードクリックで :target 遷移が動作する
- [ ] Back to list で一覧に戻れる
- [ ] マスコットクリックで表情が変わる
- [ ] 深夜（02:00-05:00）にトーストが表示される
- [ ] hashchange でスムーズスクロールする
- [ ] `python3 update_diary.py --dry-run` がエラーなく動作する

---

### WP-8.4 Alert レベルテスト

| 項目 | 内容 |
|------|------|
| **説明** | health.json の値を手動変更し、Alert Level 1/2/3 の表示を確認。表示色、メッセージ、トーンを検証。 |
| **成果物** | テスト結果（各レベルのスクリーンショット推奨） |
| **依存** | WP-6.4, WP-8.2 |
| **受入基準** | SC-10 を満たす |

---

### WP-8.5 レスポンシブテスト

| 項目 | 内容 |
|------|------|
| **説明** | モバイル / タブレット / デスクトップの3画面サイズで Room コンポーネントの表示を確認。DevTools のデバイスシミュレーション使用。 |
| **成果物** | テスト結果 |
| **依存** | WP-5.6, WP-8.2 |
| **受入基準** | QG-03 を満たす |

---

## 9.0 ドキュメント更新

Phase 1 の実装内容を既存ドキュメントに反映する。

---

### WP-9.1 CLAUDE.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Directory Structure、Common Tasks、CSS Custom Properties に Phase 1 の新コンポーネント情報を追記。 |
| **成果物** | 更新された CLAUDE.md |
| **依存** | WP-8.3 |
| **受入基準** | collectors/, src/data/, Room コンポーネントの説明がある |

---

### WP-9.2 ARCHITECTURE.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Phase 1 完了状態にシステムアーキテクチャ図、File Inventory、Data Flow、Frontend Architecture を更新。 |
| **成果物** | 更新された specs/ARCHITECTURE.md |
| **依存** | WP-9.1 |
| **受入基準** | Phase 1 完了後の正確なシステム構成を反映 |

---

### WP-9.3 docs/README.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Phase 1 完了を反映。phases/phase1/GOAL.md, phases/phase1/WBS.md をインデックスに追加。Directory Structure を現状に更新。 |
| **成果物** | 更新された docs/README.md |
| **依存** | WP-9.2 |
| **受入基準** | (1) Phase 1 ステータスが反映 (2) 新規ドキュメントがリンクされている (3) Directory Structure が現状反映 |

---

## 実装推奨順序

```
Week 1: 基盤 + Backend
────────────────────────────
Day 1:  WP-1.1 → 1.2 → 1.3 → 1.4           基盤構築（1h）
Day 2:  WP-2.1 → 2.2 → 2.3 → 2.4 → 2.5    Health 個別取得（2h）
Day 3:  WP-2.6 → 2.7                         Health 統合（1h）
Day 4:  WP-3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6  Status 全体（2h）

Week 2: Frontend + 統合
────────────────────────────
Day 5:  WP-4.1 → 4.2 → 4.3 → 4.4           HTML 構造（1.5h）
Day 6:  WP-5.1 → 5.2 → 5.3 → 5.4 → 5.5    CSS スタイリング（3h）
Day 7:  WP-5.6 + 6.1 → 6.2 → 6.3           レスポンシブ + JS（2h）
Day 8:  WP-6.4 → 6.5 → 6.6 → 6.7           JS 完成（1h）

Week 3: Operations + QA
────────────────────────────
Day 9:  WP-7.1 → 7.2 → 7.3                  定期実行（0.5h）
Day 10: WP-8.1 → 8.2 → 8.3 → 8.4 → 8.5    全テスト（2h）
Day 11: WP-9.1 → 9.2 → 9.3                  ドキュメント（1h）
```

**並行作業ポイント:**
- 2.0 (Health) と 3.0 (Status) は並行可能
- 4.0 + 5.0 (Frontend HTML/CSS) は WP-1.4 完了後、Backend 完成を待たずに着手可能
- 6.0 (JS) は WP-1.4 + 4.0 があれば着手可能

---

## 依存関係マトリクス

| WP | 依存元 |
|----|--------|
| 1.1 | — |
| 1.2 | — |
| 1.3 | 1.2 |
| 1.4 | 1.2 |
| 2.1-2.5 | 1.1 |
| 2.6 | 2.1-2.5 |
| 2.7 | 2.6, 1.2 |
| 3.1-3.3 | 1.1 |
| 3.4 | 3.1, 3.2, 3.3 |
| 3.5 | 3.2 |
| 3.6 | 3.4, 3.5, 1.2 |
| 4.1 | 1.4 |
| 4.2 | 4.1 |
| 4.3 | 4.1 |
| 4.4 | 4.1, 4.2, 4.3 |
| 5.1 | 4.1 |
| 5.2 | 4.2 |
| 5.3 | 5.2 |
| 5.4 | 5.2 |
| 5.5 | 4.3 |
| 5.6 | 5.1, 5.2, 5.5 |
| 6.1 | 1.4 |
| 6.2 | 4.1, 6.1 |
| 6.3 | 4.2, 6.1 |
| 6.4 | 4.3, 6.1 |
| 6.5 | 6.2 |
| 6.6 | 6.1-6.5 |
| 6.7 | 6.2, 6.3, 6.4 |
| 7.1 | 2.7 |
| 7.2 | 3.6 |
| 7.3 | 7.1, 7.2 |
| 8.1 | 2.7, 3.6 |
| 8.2 | 6.6, 5.6, 8.1 |
| 8.3 | 8.2 |
| 8.4 | 6.4, 8.2 |
| 8.5 | 5.6, 8.2 |
| 9.1 | 8.3 |
| 9.2 | 9.1 |
| 9.3 | 9.2 |

---

## Appendix A: レビュー追加ワークパッケージ

エージェントチーム検証（2026-02-13）で発見された問題点への対応として追加。

---

### WP-2.7a アトミック書き込み + ディレクトリ自動作成

| 項目 | 内容 |
|------|------|
| **説明** | WP-2.7, WP-3.6 の JSON 出力を安全にする。(1) `.tmp` ファイルに書き込み後 `os.rename()` で上書き（fetch 中の破損防止）。(2) 出力先 `src/data/` が存在しない場合は `os.makedirs()` で自動作成。 |
| **成果物** | WP-2.7, WP-3.6 の出力ロジックに統合 |
| **依存** | WP-2.7, WP-3.6 |
| **受入基準** | (1) 書き込み中に fetch しても壊れた JSON を返さない (2) `src/data/` がない状態から collector を実行してもエラーにならない |

---

### WP-3.3a 時間帯メッセージの複数バリエーション

| 項目 | 内容 |
|------|------|
| **説明** | 各時間帯に3-5個のメッセージバリエーションを用意し、`random.choice()` でランダム選択する。同じメッセージの繰り返しを避け、生命感を演出する。 |
| **成果物** | WP-3.3 の時間帯テーブルを拡張 |
| **依存** | WP-3.3 |
| **受入基準** | (1) 各時間帯に最低3バリエーション (2) 同じ時間帯で複数回実行するとメッセージが変わる |

**メッセージバリエーション例:**

| Period | Messages |
|--------|----------|
| morning | 「ん......おはよ」「おはよ。......ねむい」「朝か。コーヒー淹れよ」 |
| active | 「よし、やるか」「今日は何する？」「集中モード」 |
| afternoon | null (50%), 「ん？」(20%), 「通常運転」(15%), 「やってるやってる」(15%) |
| evening | 「今日も終わりか」「疲れた......」「あとちょっと」 |
| night | 「そろそろ夜か」「今日も一日」「夜の作業が一番捗る」 |
| late_night | 「まだ起きてるの？」「......あんたもか」「夜更かし仲間じゃん」 |
| deep_night | 「寝ろよ......」「......」「あたしは寝ないけど、あんたは寝ろ」 |

---

### WP-5.4a タッチデバイス対応

| 項目 | 内容 |
|------|------|
| **説明** | ホバーで数値表示する WP-5.4 にタッチデバイス対応を追加。`@media (hover: none)` でタップトグル方式を適用。数値をラベルの下に小さく常時表示する方式も検討。 |
| **成果物** | タッチデバイス用の CSS + JS |
| **依存** | WP-5.4, WP-6.3 |
| **受入基準** | (1) タッチデバイスで数値にアクセスできる (2) `@media (hover: hover)` でホバー動作を維持 |

---

### WP-5.2a Overall Score の呼吸アニメーション

| 項目 | 内容 |
|------|------|
| **説明** | Overall Score の emoji に呼吸のような微細なスケールアニメーション（4秒サイクル）を追加。score が low の時はサイクルを遅くする（6-8秒）。最小コストで「生命感」を注入する。 |
| **成果物** | `@keyframes breathe` + `.overall-emoji` アニメーション |
| **依存** | WP-5.2 |
| **受入基準** | (1) 常にゆっくり拡縮する (2) critical 時はサイクルが遅くなる (3) 視覚的に快適（目障りでない） |

---

### WP-5.3a メトリクスバーの width トランジション

| 項目 | 内容 |
|------|------|
| **説明** | setInterval による5分更新時に、メトリクスバーの width と background-color が滑らかにトランジションする CSS を追加。機械的なジャンプではなく有機的な変化に見せる。 |
| **成果物** | `.metric-fill { transition: width 0.8s ease-out, background-color 0.5s ease; }` |
| **依存** | WP-5.3 |
| **受入基準** | (1) 値変更時にバーが滑らかに伸縮する (2) 色変更もスムーズ |

---

### WP-6.2a 相対タイムスタンプ表示

| 項目 | 内容 |
|------|------|
| **説明** | Status Bar の時刻表示を絶対時刻（23:45）ではなく相対時刻（「3分前にここにいた」）で表示。絶対時刻は hover / title 属性で見られるようにする。 |
| **成果物** | `renderStatusBar()` 内の相対時刻計算ロジック |
| **依存** | WP-6.2 |
| **受入基準** | (1) 「さっき」「X分前」「X時間前」の表現 (2) hover で絶対時刻 |

---

### WP-6.7a データ鮮度チェック

| 項目 | 内容 |
|------|------|
| **説明** | fetch した JSON の `timestamp` が現在時刻から一定時間以上古い場合、データの鮮度問題をユーザーに伝える。コレクタが停止していても嘘の「online」を表示しない。 |
| **成果物** | `checkStaleness(data)` 関数 |
| **依存** | WP-6.7 |
| **受入基準** | (1) status.json が5分超: 「接続確認中...」(2) health.json が15分超: バーを dimmed + 「最終更新: XX分前」(3) 1時間超: offline 扱い + 「しばらく応答がないみたい...」 |

**設計根拠:** CONCEPT_VULNERABILITY の「嘘の脆弱性はバレる」原則。古いデータで「online」を表示することは嘘であり、存在感を破壊する。

---

### WP-6.3a 初回ロードアニメーション

| 項目 | 内容 |
|------|------|
| **説明** | ページ初回ロード時にヘルスバーが 0% → 実値へ staggered で伸びるアニメーション。Rebecca のシステムが「起動する」感覚を演出。 |
| **成果物** | `renderHealthDashboard()` 内の初回ロード判定 + staggered animation |
| **依存** | WP-6.3, WP-5.3a |
| **受入基準** | (1) 初回のみアニメーション（更新時は通常トランジション） (2) 各バーに 50ms の stagger delay |

---

### WP-9.4 SPEC.md のクリーンアップ

| 項目 | 内容 |
|------|------|
| **説明** | レビューで発見された SPEC の不整合を修正済みの内容で最終確認する。data/ パス統一、build.py 図の修正、Overall Score 計算式修正、Open Questions 解決済み、Memory 計算方法の明示。 |
| **成果物** | クリーンアップ済みの phases/phase1/SPEC.md |
| **依存** | WP-9.1 |
| **受入基準** | GOAL / WBS と矛盾がない |

---

## Appendix A 依存関係

| WP | 依存元 |
|----|--------|
| 2.7a | 2.7, 3.6 |
| 3.3a | 3.3 |
| 5.2a | 5.2 |
| 5.3a | 5.3 |
| 5.4a | 5.4, 6.3 |
| 6.2a | 6.2 |
| 6.3a | 6.3, 5.3a |
| 6.7a | 6.7 |
| 9.4 | 9.1 |

---

*Created: 2026-02-12*
*Updated: 2026-02-13 — レビュー追加 +9 WP（Appendix A）*
*Phase 1 WBS — 54 ワークパッケージ、推定 ~19h*
*Rebecca の「いる」を、計画から現実にする。*
