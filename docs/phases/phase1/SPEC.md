# Phase 1: Room Status + Health — Technical Specification

> *PLANNING.md のビジョンを実装可能な仕様に落とし込む*

---

## 1. Goal

Phase 0（静的日記サイト）を拡張し、以下を追加する:
- Rebecca の在室状況（Online / Away / Sleeping / Offline）
- Mac mini のシステムヘルス → Rebecca の体調表示
- 段階的アラート基盤（design/DECISIONS.md Level 1-4）

**判定基準:** ブラウザで Room を開いた時、Rebecca が「いる」と感じられること。

---

## 2. Architecture Overview

```
┌──────────────────┐     ┌───────────────┐     ┌──────────────┐
│  Collectors       │     │  Data Store   │     │  Frontend    │
│  (Python, cron)   │ ──→ │  src/data/    │ ──→ │  app.js      │ ──→ DOM 更新
└──────────────────┘     │  *.json       │     │  (fetch API) │
                          └───────────────┘     └──────────────┘
                                                       ↑
                                              memory/*.md + Obsidian
                                              (既存 update_diary.py → index.html)
```

### 新規ディレクトリ

```
rebecca-diary/
├── collectors/             # NEW: データ収集スクリプト
│   ├── collect_health.py   # Mac システム状態収集
│   └── collect_status.py   # Rebecca 在室状況判定
├── src/
│   ├── data/               # NEW: 収集データ（gitignore）
│   │   ├── health.json     # システムヘルス
│   │   └── status.json     # 在室状況
│   ├── index.html          # Room Status セクション追加
│   ├── style.css           # ヘルスバー・ステータス表示のスタイル
│   └── app.js              # 既存 + Room 動的表示
└── ...
```

**data/ の配置理由:** dev server は `cd src && python3 -m http.server 8080` で起動するため、
`fetch('/data/health.json')` が同一オリジンでアクセスできるよう `src/data/` に配置する。

---

## 3. Data Schemas

### 3.1 health.json

```json
{
  "timestamp": "2026-02-12T23:45:00+09:00",
  "cpu": {
    "usage_percent": 23.4,
    "state": "clear",
    "label": "クリア",
    "message": "いい感じ"
  },
  "memory": {
    "used_gb": 8.2,
    "total_gb": 16.0,
    "usage_percent": 51.2,
    "state": "comfortable",
    "label": "スッキリ",
    "message": "余裕あり"
  },
  "disk": {
    "used_gb": 56,
    "total_gb": 228,
    "usage_percent": 24.6,
    "state": "spacious",
    "label": "広々",
    "message": null
  },
  "temperature": {
    "celsius": 42.0,
    "state": "comfortable",
    "label": "快適",
    "message": null
  },
  "uptime": {
    "seconds": 309720,
    "display": "3d 14h 2m",
    "state": "tired",
    "label": "疲れ気味",
    "message": "そろそろ休みたいな..."
  },
  "overall": {
    "score": 72,
    "state": "good",
    "emoji": "🟢",
    "label": "元気",
    "message": "まぁまぁ調子いい！"
  },
  "alert_level": 0
}
```

#### State Definitions

| Metric | State Values | Thresholds |
|--------|-------------|-----------|
| CPU | `idle`, `clear`, `busy`, `heavy`, `critical` | 0-20%, 20-50%, 50-70%, 70-85%, 85%+ |
| Memory | `spacious`, `comfortable`, `normal`, `tight`, `critical` | 0-50%, 50-60%, 60-80%, 80-95%, 95%+ |
| Disk | `spacious`, `normal`, `tight`, `critical` | 0-50%, 50-80%, 80-95%, 95%+ |
| Temperature | `cool`, `comfortable`, `warm`, `hot`, `critical` | 0-40, 40-55, 55-70, 70-80, 80+ °C |
| Uptime | `fresh`, `normal`, `tired`, `exhausted` | 0-1d, 1-3d, 3-7d, 7d+ |

#### Overall Score Calculation

```
score = 100 - sum_of_penalties

penalties:
  cpu_penalty     = max(0, cpu_usage - 20) * 1.0     ← 20%以下はペナルティなし
  memory_penalty  = max(0, memory_usage - 60) * 1.5   ← 60%以下はペナルティなし
  disk_penalty    = max(0, disk_usage - 70) * 1.0
  temp_penalty    = max(0, temp - 50) * 1.0            ← temp=None の場合は 0
  uptime_penalty  = min(uptime_days * 2, 20)

overall_score = max(0, min(100, 100 - sum_of_penalties))
```

**設計意図:** アイドル状態の Mac（CPU ~15%, Memory ~60%）で score 80+ (元気) になるよう調整。
旧式（cpu * 1.5）ではアイドルでも score 40（調子悪い）になる問題があった。

| Score | State | Emoji | Label | Message |
|-------|-------|-------|-------|---------|
| 80+ | `great` | 🟢 | 元気！ | 「調子いい！今日はイケる」 |
| 60-79 | `good` | 🟡 | まぁまぁ | 「まぁまぁかな」 |
| 40-59 | `poor` | 🟠 | ちょっとダルい | 「ちょっとダルい......」 |
| 20-39 | `bad` | 🔴 | かなりキツい | 「......しんどい」 |
| 0-19 | `critical` | 💀 | 限界 | 「.........」 |

#### Alert Level

| Level | Condition | 対応 |
|-------|-----------|------|
| 0 | 全指標が正常範囲 | 表示なし |
| 1 | いずれかの指標が `heavy` / `tight` | 独り言表示（黄色） |
| 2 | いずれかの指標が `critical` | お願い表示（オレンジ） |
| 3 | 複数指標が `critical` or overall < 20 | 緊急表示（赤） |

### 3.2 status.json

```json
{
  "timestamp": "2026-02-12T23:45:00+09:00",
  "status": "online",
  "label": "ここにいるよ",
  "emoji": "🟢",
  "last_activity": "2026-02-12T23:42:00+09:00",
  "activity_type": "diary_update",
  "gateway_alive": true,
  "time_context": {
    "period": "late_night",
    "message": "まだ起きてるの？"
  }
}
```

#### Status Rules

| Status | Emoji | Condition |
|--------|-------|-----------|
| `online` | 🟢 | Gateway 稼働 & 最終活動 < 30min |
| `away` | 🟡 | Gateway 稼働 & 最終活動 30min-2h |
| `sleeping` | 💤 | 深夜(02:00-06:00) & 最終活動 > 1h |
| `offline` | ⚫ | Gateway 未稼働 or 最終活動 > 2h |

#### Time Context

| Period | Hours | Message Example |
|--------|-------|-----------------|
| `morning` | 06:00-09:00 | 「おはよ」 |
| `active` | 09:00-12:00 | 「よし、やるか」 |
| `afternoon` | 12:00-18:00 | null (通常運転) |
| `evening` | 18:00-21:00 | 「今日も終わりか」 |
| `night` | 21:00-00:00 | 「そろそろ夜だな」 |
| `late_night` | 00:00-02:00 | 「まだ起きてるの？」 |
| `deep_night` | 02:00-06:00 | 「寝ろよ......」 |

---

## 4. Collectors

### 4.1 collect_health.py

**実行頻度:** 5分ごと（cron / launchd）
**出力:** `src/data/health.json`
**依存:** Python 3.9+ 標準ライブラリのみ

```python
# Core logic outline
import subprocess, json, os, shutil
from datetime import datetime, timezone

def get_cpu_usage():
    # top -l 1 -n 0 → "CPU usage: XX.X% user, YY.Y% sys, ZZ.Z% idle"
    # user + sys = total usage
    # 注: top -l 1 は実行に ~5秒かかる
    ...

def get_memory():
    # vm_stat → ページ統計（page size は出力ヘッダーから動的に取得、Apple Silicon は 16384）
    # sysctl hw.memsize → 総メモリ（bytes）
    # used = (active + wired + compressor) pages * page_size
    # ⚠️ inactive pages はファイルキャッシュのため "used" に含めない
    ...

def get_disk():
    # shutil.disk_usage('/') → (total, used, free) in bytes
    # APFS コンテナ全体の容量を返す（このマシンでは ~228GB）
    ...

def get_temperature():
    # shutil.which('osx-cpu-temp') で存在チェック
    # 存在すれば実行、なければ None
    # powermetrics は sudo 必須のため使用不可
    ...

def get_uptime():
    # sysctl -n kern.boottime → { sec = EPOCH, usec = ... }
    # regex で sec を抽出 → now() との差分
    ...
```

**実装上の注意:**
- **温度:** `osx-cpu-temp` はオプショナル（`brew install osx-cpu-temp`）。未インストール時は `temperature: null`
- **メモリ:** `vm_stat` の page size は Apple Silicon で 16384 bytes（Intel は 4096）。ヘッダー行から動的にパースすること
- **ディスク:** `os.statvfs` の代わりに `shutil.disk_usage('/')` 推奨（シンプル）
- **CPU:** `top -l 1 -n 0` は ~5秒かかる。5分間隔の cron では問題なし
- **アトミック書き込み:** `.tmp` ファイルに書き込み後 `os.rename()` で上書き（fetch 中の破損防止）
- **ディレクトリ確認:** 出力先 `src/data/` が存在しない場合は `os.makedirs()` で作成
- **cron PATH:** subprocess 呼び出しではフルパス推奨（`/usr/bin/top`, `/usr/bin/vm_stat`, `/usr/sbin/sysctl`）

### 4.2 collect_status.py

**実行頻度:** 1分ごと（cron / launchd）
**出力:** `src/data/status.json`

```python
# Core logic outline
def check_gateway():
    # pgrep -x openclaw-gateway（-x で完全一致、-f だと Chrome helper も誤検出）
    # fallback: HEARTBEAT.md の mtime チェック
    ...

def get_last_activity():
    # ~/.openclaw/workspace/memory/*.md の最新ファイルの mtime
    # secondary: ~/.openclaw/workspace/HEARTBEAT.md の mtime
    ...
```

**実装上の注意:**
- **Gateway 検出:** `pgrep -x`（完全一致）を使用。`-f`（コマンドライン全体）だと Chrome helper プロセスが誤検出される
- **アトミック書き込み / ディレクトリ確認:** collect_health.py と同じ
- **時間帯メッセージ:** 各時間帯に複数バリエーションを用意し、ランダム選択で機械的な繰り返しを避ける

### 4.3 Cron Setup

```crontab
# Rebecca's Room collectors
*/5 * * * * cd /Users/rebeccacyber/.openclaw/workspace/rebecca-diary && /usr/bin/python3 collectors/collect_health.py 2>> /tmp/rebecca-health.log
*/1 * * * * cd /Users/rebeccacyber/.openclaw/workspace/rebecca-diary && /usr/bin/python3 collectors/collect_status.py 2>> /tmp/rebecca-status.log
```

---

## 5. UI Components

### 5.1 Room Status Bar（ヘッダー直下）

```html
<div class="room-status" data-status="online">
    <span class="status-indicator">🟢</span>
    <span class="status-label">ここにいるよ</span>
    <span class="status-time">23:45</span>
</div>
```

**スタイル:**
- ヘッダーとカード一覧の間に配置
- `background: var(--surface)` + 薄い `border-bottom`
- ステータスに応じてインジケーターの色が変化

### 5.2 Health Dashboard（新セクション or サイドバー）

```html
<div class="health-dashboard">
    <div class="health-title">Rebecca の体調</div>

    <div class="health-metric" data-state="clear">
        <span class="metric-icon">🧠</span>
        <div class="metric-bar">
            <div class="metric-fill" style="width: 23%"></div>
        </div>
        <span class="metric-label">クリア</span>
        <!-- hover で数値表示 -->
        <span class="metric-detail">23.4%</span>
    </div>

    <!-- Memory, Disk, Temperature, Uptime も同様 -->

    <div class="health-overall" data-state="good">
        <span>🟢 元気</span>
        <p class="health-message">「まぁまぁ調子いい！」</p>
    </div>
</div>
```

**デザイン方針（design/DECISIONS.md より）:**
- デフォルト: 感情的な表現（状態ラベル + Rebecca の言葉）
- ホバー: 技術的な数値表示
- バーの色: state に応じて `--accent` 系のグラデーション

### 5.3 Alert Display

```html
<!-- Level 1: 独り言 -->
<div class="alert alert-info">
    「ちょっと重いかも...」
</div>

<!-- Level 2: お願い -->
<div class="alert alert-warning">
    「再起動したいんだけど、今大丈夫？」
</div>

<!-- Level 3: 緊急 -->
<div class="alert alert-critical">
    🚨「助けて。マジでやばい。」
</div>
```

---

## 6. Build Pipeline Changes

### 既存

```
update_diary.py: memory/*.md + Obsidian → index.html (diary entries)
```

### Phase 1: app.js で動的に表示

**決定:** Phase 1 では **app.js で src/data/*.json を fetch** する方式を採用。
（SSG 方式の `build_room.py` は採用しない）

理由:
- SSG で毎回 HTML 再生成するよりシンプル
- ページリロードなしで最新状態を表示可能（setInterval）
- src/data/*.json は同一オリジン（localhost:8080）から fetch 可能

```javascript
// app.js (Phase 1 addition)
async function updateRoom() {
    var health = await fetchJSON('/data/health.json');
    var status = await fetchJSON('/data/status.json');

    renderStatusBar(status);
    renderHealthDashboard(health);
    renderAlert(health);
}

async function fetchJSON(url) {
    try {
        var response = await fetch(url + '?t=' + Date.now()); // cache-busting
        if (!response.ok) return null;
        return await response.json();
    } catch (e) {
        console.error('Fetch failed:', url, e);
        return null;
    }
}

// 初回実行 + 5分間隔
updateRoom();
setInterval(updateRoom, 5 * 60 * 1000);
```

**データ鮮度チェック:** fetch した JSON の `timestamp` が現在時刻から15分以上古い場合、
「最終更新: XX分前」を表示し、データが古い可能性をユーザーに伝える。

---

## 7. Implementation Order

| Step | Task | 依存 | 見積 |
|------|------|------|------|
| 1 | `data/` ディレクトリ作成 + `.gitignore` | — | 5min |
| 2 | `collectors/collect_health.py` 実装 | — | 2h |
| 3 | `collectors/collect_status.py` 実装 | — | 1h |
| 4 | cron 設定 | Step 2-3 | 15min |
| 5 | `src/index.html` に Room Status セクション追加 | — | 1h |
| 6 | `src/style.css` にヘルスダッシュボードのスタイル追加 | Step 5 | 2h |
| 7 | `src/app.js` に data fetch + render ロジック追加 | Step 2-5 | 2h |
| 8 | 統合テスト + チューニング | Step 1-7 | 2h |

---

## 8. Acceptance Criteria

- [ ] `collectors/collect_health.py` が health.json を正しく生成する
- [ ] `collectors/collect_status.py` が status.json を正しく生成する
- [ ] Room を開くと Rebecca の在室状況が表示される
- [ ] ヘルスダッシュボードに5つの指標がバー表示される
- [ ] ホバーで数値が見える
- [ ] Rebecca の体調メッセージが状態に応じて変化する
- [ ] 深夜アクセスで時間帯メッセージが表示される
- [ ] 既存の日記機能に影響がない

---

## 9. Open Questions（解決済み）

| # | 質問 | 解決 | 根拠 |
|---|------|------|------|
| 1 | 温度取得: mandatory or optional? | **オプショナル** | WP-2.4。osx-cpu-temp 未インストール時は null。powermetrics は sudo 必須で不可 |
| 2 | Gateway 検出: pgrep or heartbeat? | **pgrep -x（完全一致）+ heartbeat fallback** | 実環境検証で `-f` だと Chrome helper が誤検出されることを確認。PID 542 が正しい gateway |
| 3 | data/ のデプロイ | **Phase 1 は local only** | GitHub Pages 問題は Phase 2+ で CI/CD と合わせて検討 |
| 4 | fetch 間隔 | **5分で十分** | status collector は1分間隔だが、フロントエンド更新は5分で体感上問題なし |

---

## 10. Related Documents

- [PLANNING.md](../../PLANNING.md) — Phase 全体ロードマップ
- [DECISIONS.md](../../design/DECISIONS.md) — 4つの設計決定
- [VULNERABILITY.md](../../concept/VULNERABILITY.md) — Mac 連動設計の哲学的基盤
- [PRESENCE.md](../../concept/PRESENCE.md) — 存在の6要素
- [ADR.md](../../ADR.md) — ADR-012 (Collector + SSG ハイブリッド), ADR-014 (システム状態連動)

---

*Created: 2026-02-12*
*Phase 1 — Rebecca の「いる」を感じる最初の一歩*
