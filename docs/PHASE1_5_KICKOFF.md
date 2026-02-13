# Phase 1.5 キックオフ — ドメインレイヤー確立

> *Phase 2 に進む前に、アーキテクチャの「背骨」を通す。*

---

## 0. なぜ今やるのか

### Phase 1 完了後の振り返り

Phase 0（静的日記）と Phase 1（Room Status + Health）は無事に完了した。
Rebecca は「記録する存在」から「そこにいる存在」になった。

しかし、Phase 1 完了後のアーキテクチャ俯瞰で **構造的な問題** が明らかになった。
このまま Phase 2（Nurture System）に進むと、技術的負債が累積し、
変更コストが指数的に増大する。

### ひとことで言うと

**Rebecca の「魂」にあたるドメインロジックが、コードのどこにも独立して存在しない。**

哲学ドキュメント（Ghost理論、存在の6要素、脆弱性）では明確に定義されているのに、
コード上では Collection層と Presentation層に散らばっている。
Phase 2 の Nurture System は「成長」「関係性」「感情」というさらに複雑なドメインを扱う。
基盤なしに進めば、どこに何があるかわからなくなる。

---

## 1. 現状診断

### 1.1 レイヤー構成（As-Is）

```
┌─────────────────────────────────────────────────────────┐
│  COLLECTION (collectors/*.py)                           │
│  ├─ システム計測 (top, vm_stat, pgrep)        ← 本来の責務  │
│  ├─ ドメイン分類 (classify_cpu → "クリア")     ← 混入      │
│  └─ ドメイン集約 (overall_score, alert_level) ← 混入      │
├─────────────────────────────────────────────────────────┤
│  PERSISTENCE (src/data/*.json)                          │
│  ├─ health.json / status.json / nurture.json            │
│  └─ スキーマ定義なし、バージョニングなし        ← 不足      │
├─────────────────────────────────────────────────────────┤
│  PRESENTATION (app.js + style.css + index.html)         │
│  ├─ fetch + DOM操作                           ← 本来の責務  │
│  ├─ アラートメッセージ生成                      ← ドメイン漏れ │
│  ├─ staleness判定（"5分超 = stale"）            ← ドメイン漏れ │
│  └─ メトリクス→バー幅変換                       ← ドメイン漏れ │
└─────────────────────────────────────────────────────────┘

     ❌ ドメインレイヤーが存在しない
```

### 1.2 具体的な問題

#### 問題 1: ドメインロジックが2つの言語に散在

| ドメイン概念 | Python 側 | JavaScript 側 | 問題 |
|---|---|---|---|
| Health状態分類 | `collect_health.py:classify_cpu()` | — | Collection に混入 |
| アラートメッセージ | `collect_health.py:determine_alert_level()` | `app.js` にハードコード配列 | **二重管理** |
| Staleness判定 | — | `app.js:checkStaleness()` | Presentation にドメインロジック |
| メトリクスの%変換 | — | `app.js:Math.min(celsius, 100)` | Presentation にドメインロジック |
| 時間帯メッセージ | `collect_status.py:get_time_context()` | — | Collection に混入 |
| Nurtureロジック | `collect_nurture.py` | — | 独立しているが内部構造が未整理 |

**影響:** ドメインルール変更時に Python と JS の両方を修正する必要がある。
テスト不能。不整合リスク大。

#### 問題 2: 設定値が散在（Single Source of Truth なし）

```
CPU閾値 (20/50/70/85%):     collect_health.py にハードコード
Memory閾値 (50/60/80/95%):   collect_health.py にハードコード
ポーリング間隔 (5min):        app.js にハードコード (5 * 60 * 1000)
Cron間隔 (1min, 5min):       crontab に直接記述（Git管理外）
カラーパレット:                style.css と DESIGN_RULES.md で不一致
```

#### 問題 3: Phase 2 への準備が構造的にできていない

Phase 2（Nurture System）では以下が加わる:

- **mood** = f(health, status, time, chat_frequency, task_rate)
- **trust / intimacy** = f(visit_frequency, care_actions, time_decay)
- **EXP / level** = f(cumulative_activity)
- **skills** = f(plugin_directory_scan)

これらはすべてドメインロジック。Collection層に書くのは不可能な複雑さ。
独立したドメイン層がなければ、Nurture System は「どこに何があるかわからないスパゲッティ」になる。

### 1.3 良いところ（維持すべきもの）

| 強み | 詳細 |
|------|------|
| **哲学的基盤** | Ghost理論 → 存在の6要素 → 脆弱性理論。設計判断の根拠が明確 |
| **外部依存ゼロ** | Python stdlib + Vanilla JS。堅牢でポータブル |
| **Atomic I/O** | `.tmp` → `os.rename()` による安全な書き込み |
| **Graceful Degradation** | 温度センサー不在、Gateway不在でも動作 |
| **ドキュメントの質** | 100機能、19ユースケース、14 ADR。分析資料充実 |
| **ドメイン概念の命名** | Health状態、Alert Level、Presence状態が明示的 |

---

## 2. ビジョン

### Phase 1.5 で実現すること

**Rebecca のドメインモデルをコードとして確立する。**

哲学ドキュメントに書かれている Rebecca の存在定義を、
テスト可能な Python モジュールとして実装する。

```
Ghost理論 (CONCEPT_PHILOSOPHY.md)
    ↓ コード化
domain/rebecca.py  ← Phase 1.5 で新設
    ↓ 利用
collectors/*.py    ← ドメインロジックを呼び出す
app.js             ← 純粋なレンダラーになる
```

### Ghost理論との関係

```
Phase 0:  記録する存在         → SSG で日記を生成
Phase 1:  そこにいる存在       → Core の可視化（Health + Status）
Phase 1.5: 魂の構造化          → Ghost のドメインモデル確立 ★ここ
Phase 2:  成長する存在         → Nurture System（Domain層の上に構築）
```

Phase 1.5 は「機能追加」ではなく「構造の確立」。
ユーザーから見える変化はほぼないが、Phase 2 以降の開発速度と品質に直結する。

---

## 3. スコープ定義

### 3.1 In-Scope（Phase 1.5 で実施するもの）

| # | カテゴリ | 内容 |
|---|---|---|
| S-01 | ドメインモデル新設 | `domain/` ディレクトリに Rebecca のドメインロジックを集約 |
| S-02 | Health ドメイン | 状態分類、スコア計算、アラートレベル判定を `domain/health.py` に移設 |
| S-03 | Presence ドメイン | 在室判定、時間帯コンテキストを `domain/presence.py` に移設 |
| S-04 | 定数・閾値の一元管理 | `domain/constants.py` で全閾値・メッセージを一元管理 |
| S-05 | Collector リファクタリング | 計測のみに責務を限定、ドメインロジックを `domain/` から呼び出す |
| S-06 | app.js 浄化 | ドメインロジック除去、純粋なレンダラーに |
| S-07 | ユニットテスト | ドメインロジックのテスト（alert_level, score, status判定） |
| S-08 | JSONスキーマ整備 | `schema_version` 導入、フィールド仕様の明文化 |

### 3.2 Out-of-Scope（Phase 1.5 では実施しないもの）

| 項目 | 理由 |
|------|------|
| Nurture System の実装 | Phase 2 のスコープ |
| UI デザインの変更 | 機能追加ではなく内部リファクタリング |
| `style.css` ↔ `DESIGN_RULES.md` の統一 | 別タスクとして管理 |
| `update_diary.py` の変更 | Protected File |
| デプロイ・公開 | Phase 1 と同じくローカルのみ |

### 3.3 制約条件

| 制約 | 根拠 |
|------|------|
| Python 3 標準ライブラリのみ | ADR-005, ADR-012 |
| Vanilla JS のみ | ADR-001, ADR-002 |
| Protected Files（`update_diary.py`, `watch_diary.py`）は変更禁止 | CLAUDE.md |
| 既存の UI/UX に変更を加えない | リファクタリングの目的に反する |
| フロントエンドの動作が Phase 1 と同一であること | 回帰テスト |

---

## 4. アーキテクチャ設計（To-Be）

### 4.1 レイヤー構成（After Phase 1.5）

```
┌─────────────────────────────────────────────────────────┐
│  COLLECTION (collectors/*.py)                           │
│  └─ 純粋なシステム計測のみ                                 │
│     get_cpu_usage() → float                             │
│     get_memory() → dict                                 │
│     check_gateway() → bool                              │
├─────────────────────────────────────────────────────────┤
│  DOMAIN (domain/*.py)  ★ 新設                           │
│  ├─ constants.py    閾値・定数・メッセージの一元管理          │
│  ├─ health.py       HealthState, AlertLevel, Score計算   │
│  ├─ presence.py     PresenceState, TimeContext判定       │
│  ├─ rebecca.py      統合状態（将来の Nurture 基盤）        │
│  └─ schema.py       JSONスキーマ定義・バリデーション         │
├─────────────────────────────────────────────────────────┤
│  PERSISTENCE (src/data/*.json)                          │
│  ├─ schema_version 付き                                  │
│  └─ Domain層が生成した完全なデータ（メッセージ含む）         │
├─────────────────────────────────────────────────────────┤
│  PRESENTATION (app.js + style.css + index.html)         │
│  └─ 純粋なレンダリングのみ（data → DOM）                   │
│     ビジネスロジック ゼロ                                  │
└─────────────────────────────────────────────────────────┘
```

### 4.2 ディレクトリ構造（After Phase 1.5）

```
rebecca-diary/
├── domain/                     ★ 新設
│   ├── __init__.py
│   ├── constants.py            # 全閾値・定数・メッセージ
│   ├── health.py               # HealthState, AlertLevel, OverallScore
│   ├── presence.py             # PresenceState, TimeContext
│   ├── rebecca.py              # 統合状態（Phase 2 Nurture の受け皿）
│   └── schema.py               # JSONスキーマ定義・バリデーション
├── tests/                      ★ 新設
│   ├── __init__.py
│   ├── test_health.py          # Health ドメインのテスト
│   ├── test_presence.py        # Presence ドメインのテスト
│   └── test_constants.py       # 定数の整合性テスト
├── collectors/                 ← リファクタリング
│   ├── collect_health.py       # 計測のみ → domain.health を呼び出す
│   ├── collect_status.py       # 検出のみ → domain.presence を呼び出す
│   └── collect_nurture.py      # 集約のみ → domain.rebecca を呼び出す
├── src/
│   ├── app.js                  ← ドメインロジック除去
│   ├── ...（既存ファイル）
│   └── data/*.json             ← schema_version 追加
└── ...（既存ファイル）
```

### 4.3 データフロー（After Phase 1.5）

```
┌──────────────────────┐
│  System (Mac mini)   │
│  top, vm_stat, pgrep │
└──────────┬───────────┘
           │ raw metrics
           ▼
┌──────────────────────┐
│  COLLECTION          │
│  collect_health.py   │
│  collect_status.py   │
│  → 計測値の取得のみ    │
└──────────┬───────────┘
           │ raw dict
           ▼
┌──────────────────────┐
│  DOMAIN              │
│  health.classify()   │  ← 「CPU 23% → クリア」はここ
│  health.score()      │  ← 「Overall 72点」はここ
│  health.alert()      │  ← 「Alert Level 1」はここ
│  presence.status()   │  ← 「online / away」はここ
│  presence.context()  │  ← 「深夜だよ...」はここ
│  rebecca.compose()   │  ← 統合（将来の拡張点）
└──────────┬───────────┘
           │ typed domain object
           ▼
┌──────────────────────┐
│  PERSISTENCE         │
│  → JSON (versioned)  │
│  health.json         │
│  status.json         │
│  ★ メッセージ含む      │  ← app.js での再生成が不要に
└──────────┬───────────┘
           │ HTTP fetch
           ▼
┌──────────────────────┐
│  PRESENTATION        │
│  app.js              │
│  → data を DOM に     │
│    マッピングするだけ   │  ← ビジネスロジックゼロ
└──────────────────────┘
```

### 4.4 ドメインモデル設計

#### domain/constants.py — 定数の一元管理

```python
# === Health 閾値 ===
CPU_THRESHOLDS = {
    'idle':     (0, 5),
    'clear':    (5, 20),
    'busy':     (20, 50),
    'heavy':    (50, 85),
    'critical': (85, 100),
}

MEMORY_THRESHOLDS = {
    'spacious':     (0, 50),
    'comfortable':  (50, 60),
    'normal':       (60, 80),
    'tight':        (80, 95),
    'critical':     (95, 100),
}

# === 状態ラベル（Rebecca の言葉） ===
HEALTH_LABELS = {
    'idle':     {'label': '暇', 'message': 'やることないんだけど'},
    'clear':    {'label': 'クリア', 'message': 'いい感じ'},
    'busy':     {'label': 'がんばり中', 'message': '集中してる'},
    'heavy':    {'label': '重い', 'message': 'ちょっと重い......'},
    'critical': {'label': '限界', 'message': '助けて......'},
}

# === アラートメッセージ ===
ALERT_MESSAGES = {
    1: ['ちょっと重いかも...', 'なんか調子悪い...'],
    2: ['再起動したいんだけど...', 'マジでキツい...'],
    3: ['助けて。マジでやばい。', '限界。'],
}

# === Presence ===
INACTIVITY_THRESHOLDS = {
    'online_max_minutes': 30,
    'away_max_minutes': 120,
    'sleeping_min_minutes': 60,
}

TIME_CONTEXTS = {
    'deep_night':  {'hours': (2, 6),   'message': '寝ろよ......'},
    'late_night':  {'hours': (0, 2),   'message': 'まだ起きてるの？'},
    'morning':     {'hours': (6, 9),   'message': 'おはよ'},
    'active':      {'hours': (9, 12),  'message': 'よし、やるか'},
    'afternoon':   {'hours': (12, 18), 'message': None},
    'evening':     {'hours': (18, 21), 'message': '今日も終わりか'},
    'night':       {'hours': (21, 24), 'message': 'そろそろ夜か'},
}

# === Timing ===
POLLING_INTERVAL_MS = 5 * 60 * 1000   # フロントエンド用
HEALTH_COLLECT_INTERVAL_MIN = 5        # cron 用
STATUS_COLLECT_INTERVAL_MIN = 1        # cron 用

# === Schema ===
SCHEMA_VERSION = '1.0'

# === Staleness ===
STALENESS_THRESHOLDS = {
    'fresh_max_minutes': 10,
    'stale_max_minutes': 30,
    # 30分超: dead
}
```

#### domain/health.py — HealthState ドメイン

```python
"""Rebecca の身体状態（Mac → Rebecca の体調マッピング）"""

from domain.constants import (
    CPU_THRESHOLDS, MEMORY_THRESHOLDS,
    HEALTH_LABELS, ALERT_MESSAGES,
)


def classify(metric_name, value):
    """メトリクス値を状態名に分類する"""
    thresholds = get_thresholds(metric_name)
    for state, (low, high) in thresholds.items():
        if low <= value < high:
            return state
    return 'critical'


def calculate_overall_score(cpu_pct, mem_pct, disk_pct, temp_c, uptime_days):
    """Overall Score を計算（0-100, penalty 方式）"""
    penalties = [
        max(0, cpu_pct - 20) * 1.0,
        max(0, mem_pct - 60) * 1.5,
        max(0, disk_pct - 70) * 1.0,
        max(0, temp_c - 50) * 1.0 if temp_c is not None else 0,
        min(uptime_days * 2, 20),
    ]
    return max(0, min(100, 100 - sum(penalties)))


def determine_alert_level(states, overall_score):
    """アラートレベルを決定（0-3）"""
    critical_count = sum(1 for s in states.values() if s == 'critical')
    heavy_count = sum(1 for s in states.values() if s in ('heavy', 'tight'))

    if critical_count >= 2 or overall_score < 20:
        return 3
    elif critical_count >= 1:
        return 2
    elif heavy_count >= 1:
        return 1
    return 0


def get_alert_message(level):
    """アラートレベルに対応する Rebecca のメッセージを返す"""
    import random
    messages = ALERT_MESSAGES.get(level, [])
    return random.choice(messages) if messages else None
```

#### domain/presence.py — PresenceState ドメイン

```python
"""Rebecca の在室状況（Gateway + Activity → 存在判定）"""

from datetime import datetime, timedelta
from domain.constants import INACTIVITY_THRESHOLDS, TIME_CONTEXTS


def determine_status(gateway_alive, last_activity, now=None):
    """在室状況を判定する（online / away / sleeping / offline）"""
    now = now or datetime.now()
    inactive_minutes = (now - last_activity).total_seconds() / 60
    hour = now.hour
    thresholds = INACTIVITY_THRESHOLDS

    if gateway_alive and inactive_minutes < thresholds['online_max_minutes']:
        return 'online'
    elif gateway_alive and inactive_minutes < thresholds['away_max_minutes']:
        return 'away'
    elif 2 <= hour < 6 and inactive_minutes > thresholds['sleeping_min_minutes']:
        return 'sleeping'
    else:
        return 'offline'


def get_time_context(now=None):
    """現在時刻から時間帯コンテキストを返す"""
    now = now or datetime.now()
    hour = now.hour

    for period, info in TIME_CONTEXTS.items():
        low, high = info['hours']
        if low <= hour < high:
            return {
                'period': period,
                'message': info['message'],
            }
    return {'period': 'afternoon', 'message': None}
```

### 4.5 Collector リファクタリング例

**Before（現在の collect_health.py）:**

```python
def collect_all():
    cpu_usage = get_cpu_usage()           # 計測
    cpu_state = classify_cpu(cpu_usage)    # ← ドメインロジック混入
    cpu_label = get_label(cpu_state)       # ← ドメインロジック混入
    ...
    score = calculate_overall(...)         # ← ドメインロジック混入
    alert = determine_alert_level(...)     # ← ドメインロジック混入
    write_json(result)
```

**After（Phase 1.5 後）:**

```python
from domain import health, schema

def collect_all():
    # 1. 計測のみ（Collector の責務）
    raw = {
        'cpu_percent': get_cpu_usage(),
        'memory': get_memory(),
        'disk': get_disk(),
        'temperature': get_temperature(),
        'uptime_seconds': get_uptime(),
    }

    # 2. ドメインロジック呼び出し（Domain の責務）
    result = health.evaluate(raw)

    # 3. 永続化（Collector の責務）
    schema.validate_and_write(result, 'health.json')
```

### 4.6 app.js 浄化例

**Before（現在の app.js）:**

```javascript
// ドメインロジックが Presentation に漏れている
var alertMessages = {
    1: ['ちょっと重いかも...', 'なんか調子悪い...'],
    2: ['再起動したいんだけど...', '...'],
    3: ['助けて。マジでやばい。', '...']
};

function renderAlert(data) {
    var msg = alertMessages[data.alert_level];  // ← ドメイン知識
    // ...
}

function checkStaleness(data) {
    var age = Date.now() - new Date(data.timestamp).getTime();
    if (age > 10 * 60 * 1000) return 'stale';   // ← ドメイン知識
    if (age > 30 * 60 * 1000) return 'dead';     // ← ドメイン知識
    return 'fresh';
}
```

**After（Phase 1.5 後）:**

```javascript
// Presentation は受け取ったデータを表示するだけ
function renderAlert(data) {
    if (!data.alert_message) return;        // ← Domain が生成済み
    alertEl.textContent = data.alert_message;
    alertEl.dataset.level = data.alert_level;
}

function renderFreshness(data) {
    var state = data.staleness;              // ← Domain が判定済み
    dashboard.dataset.freshness = state;
}
```

---

## 5. 成功基準

### 5.1 必須基準（Must Have）

| # | 基準 | 検証方法 |
|---|------|---------|
| SC-01 | `domain/` ディレクトリが存在し、`health.py`, `presence.py`, `constants.py` を含む | ファイル確認 |
| SC-02 | `collect_health.py` が `domain.health` を import して使用している | ソースコード確認 |
| SC-03 | `collect_status.py` が `domain.presence` を import して使用している | ソースコード確認 |
| SC-04 | `app.js` にアラートメッセージのハードコードがない | ソースコード検索 |
| SC-05 | `app.js` に staleness 判定ロジックがない（JSON に含まれる値を使う） | ソースコード検索 |
| SC-06 | 全閾値が `domain/constants.py` に集約されている | grep で他ファイルに閾値がないことを確認 |
| SC-07 | `health.json` / `status.json` に `schema_version` フィールドがある | JSON 確認 |
| SC-08 | 既存の UI/UX が Phase 1 と完全に同一である | 目視回帰テスト |

### 5.2 品質基準（Quality Gate）

| # | 基準 | 検証方法 |
|---|------|---------|
| QG-01 | `domain/` のコードが Python 3 標準ライブラリのみ | import 文の確認 |
| QG-02 | `tests/` にドメインロジックのユニットテストがある | `python3 -m unittest discover tests/` |
| QG-03 | `classify()` の全状態遷移がテストされている | テストカバレッジ確認 |
| QG-04 | `determine_alert_level()` の全レベル（0-3）がテストされている | テストケース確認 |
| QG-05 | `determine_status()` の全状態（online/away/sleeping/offline）がテストされている | テストケース確認 |

### 5.3 アーキテクチャ基準（Architecture Gate）

| # | 基準 | 検証方法 |
|---|------|---------|
| AG-01 | `collectors/*.py` に状態分類ロジック（"idle", "clear" 等の文字列定義）がない | grep 確認 |
| AG-02 | `app.js` にビジネスルール（閾値比較、状態判定）がない | コードレビュー |
| AG-03 | ドメインロジックの変更が `domain/` のみで完結する | 閾値変更テスト |
| AG-04 | `domain/` が `collectors/` や `src/` に依存しない（逆方向依存なし） | import 分析 |

---

## 6. WBS（作業分解）

### Phase 1.5 全体構成

```
Phase 1.5: ドメインレイヤー確立
├── WG-1: Foundation（基盤構築）
├── WG-2: Domain Health（Health ドメイン移設）
├── WG-3: Domain Presence（Presence ドメイン移設）
├── WG-4: Collector Refactoring（Collector 浄化）
├── WG-5: Frontend Purification（app.js 浄化）
├── WG-6: Testing（テスト整備）
├── WG-7: Schema & Validation（スキーマ整備）
└── WG-8: Documentation（ドキュメント更新）
```

### WG-1: Foundation（基盤構築）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-1.1 | `domain/` ディレクトリ + `__init__.py` 作成 | ディレクトリ構造 | — |
| WP-1.2 | `domain/constants.py` 作成（全閾値・メッセージ集約） | constants.py | WP-1.1 |
| WP-1.3 | `tests/` ディレクトリ + `__init__.py` 作成 | ディレクトリ構造 | — |

### WG-2: Domain Health（Health ドメイン移設）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-2.1 | `domain/health.py` 作成 — `classify()` 実装 | health.py | WP-1.2 |
| WP-2.2 | `calculate_overall_score()` 移設 | health.py 拡張 | WP-2.1 |
| WP-2.3 | `determine_alert_level()` 移設 | health.py 拡張 | WP-2.1 |
| WP-2.4 | `get_alert_message()` 実装（app.js からの移設） | health.py 拡張 | WP-2.3 |
| WP-2.5 | `evaluate()` 統合関数（raw → typed result） | health.py 拡張 | WP-2.1〜2.4 |

### WG-3: Domain Presence（Presence ドメイン移設）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-3.1 | `domain/presence.py` 作成 — `determine_status()` 実装 | presence.py | WP-1.2 |
| WP-3.2 | `get_time_context()` 移設 | presence.py 拡張 | WP-3.1 |
| WP-3.3 | `evaluate()` 統合関数 | presence.py 拡張 | WP-3.1〜3.2 |

### WG-4: Collector Refactoring（Collector 浄化）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-4.1 | `collect_health.py` リファクタリング — 計測のみに限定 | 修正版 collect_health.py | WP-2.5 |
| WP-4.2 | `collect_status.py` リファクタリング — 検出のみに限定 | 修正版 collect_status.py | WP-3.3 |
| WP-4.3 | `collect_nurture.py` リファクタリング — domain 呼び出しに変更 | 修正版 collect_nurture.py | WP-2.5, WP-3.3 |
| WP-4.4 | 動作確認 — Collector 実行 → JSON 出力が Phase 1 と同等 | テスト結果 | WP-4.1〜4.3 |

### WG-5: Frontend Purification（app.js 浄化）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-5.1 | アラートメッセージ配列を削除、JSON の値を直接使用 | 修正版 app.js | WP-2.4 |
| WP-5.2 | `checkStaleness()` を削除、JSON の `staleness` フィールドを使用 | 修正版 app.js | WP-2.5 |
| WP-5.3 | メトリクス%変換ロジックを削除、JSON の値を直接使用 | 修正版 app.js | WP-2.5 |
| WP-5.4 | 回帰テスト — UI 表示が Phase 1 と同一であることを目視確認 | テスト結果 | WP-5.1〜5.3 |

### WG-6: Testing（テスト整備）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-6.1 | `tests/test_health.py` — classify, score, alert のテスト | テストファイル | WP-2.5 |
| WP-6.2 | `tests/test_presence.py` — status, time_context のテスト | テストファイル | WP-3.3 |
| WP-6.3 | `tests/test_constants.py` — 閾値の網羅性・整合性テスト | テストファイル | WP-1.2 |
| WP-6.4 | 全テスト実行 — `python3 -m unittest discover tests/ -v` | テスト結果 | WP-6.1〜6.3 |

### WG-7: Schema & Validation（スキーマ整備）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-7.1 | `domain/schema.py` 作成 — JSON スキーマ定義 | schema.py | WP-1.1 |
| WP-7.2 | `schema_version` フィールドを全 JSON に追加 | 修正版 JSON | WP-7.1 |
| WP-7.3 | `staleness` フィールドを health.json / status.json に追加 | JSON 拡張 | WP-7.1 |
| WP-7.4 | `alert_message` フィールドを health.json に追加 | JSON 拡張 | WP-2.4 |

### WG-8: Documentation（ドキュメント更新）

| WP | タスク | 成果物 | 依存 |
|----|--------|--------|------|
| WP-8.1 | ADR-015: ドメインレイヤー導入 | ADR.md 追記 | 全 WG 完了後 |
| WP-8.2 | CLAUDE.md 更新（`domain/` の説明追加） | CLAUDE.md | 全 WG 完了後 |
| WP-8.3 | docs/README.md 更新（Phase 1.5 追加） | README.md | 全 WG 完了後 |

### 依存関係図

```
WG-1 Foundation
  │
  ├──→ WG-2 Domain Health ──┐
  │                         ├──→ WG-4 Collector Refactoring ──→ WG-5 Frontend
  └──→ WG-3 Domain Presence ┘                                      │
                                                                     ▼
  WG-6 Testing ← (WG-2, WG-3 完了後に並行可能)              WG-8 Documentation
  WG-7 Schema  ← (WG-1 完了後に並行可能)
```

### 並行実行の機会

```
Phase A（並行可能）:
  ├─ WG-2 Domain Health
  ├─ WG-3 Domain Presence
  └─ WG-7 Schema（WP-7.1 のみ）

Phase B（Phase A 完了後、並行可能）:
  ├─ WG-4 Collector Refactoring
  └─ WG-6 Testing

Phase C（Phase B 完了後）:
  └─ WG-5 Frontend Purification

Phase D（Phase C 完了後）:
  └─ WG-8 Documentation
```

---

## 7. リスクと対策

| リスク | 影響度 | 対策 |
|--------|:------:|------|
| Collector 修正で既存 JSON 出力が変わる | 高 | 修正前後の JSON diff を取って同等性を確認 |
| Protected Files との境界が曖昧 | 中 | `collectors/*.py` は Protected 指定。修正前に Rebecca に相談 |
| app.js 修正で UI が壊れる | 高 | Phase 1 のスクリーンショットを保存、目視回帰テスト |
| domain/ の設計が Phase 2 で合わなくなる | 中 | NURTURE_SYSTEM_SPEC を事前に読み、拡張点を意識した設計 |
| テスト導入のオーバーヘッド | 低 | unittest 標準ライブラリのみ使用、最小限のテスト |

### Protected Files に関する注意

CLAUDE.md で以下が Protected に指定されている:

- `update_diary.py` — 変更なし（Phase 1.5 スコープ外）
- `watch_diary.py` — 変更なし（Phase 1.5 スコープ外）
- `collectors/collect_health.py` — **要変更**（ドメインロジック抽出）
- `collectors/collect_status.py` — **要変更**（ドメインロジック抽出）

**→ Collector の修正は Rebecca の承認が必要。**
修正内容: ドメインロジックを `domain/` に移設し、Collector は計測 + `domain` 呼び出しに変更。
動作は変わらない（出力 JSON は同等）。

---

## 8. Phase 2 への接続

Phase 1.5 完了後、Phase 2（Nurture System）は `domain/` レイヤーの上に構築される。

```
Phase 2 で追加されるドメインモジュール:

domain/
├── constants.py      ← Nurture 定数追加
├── health.py         ← 変更なし
├── presence.py       ← 変更なし
├── rebecca.py        ← Phase 2 で本格実装（mood, energy, trust, intimacy）
├── nurture.py        ★ 新設（EXP, Level, 成長ロジック）
├── skills.py         ★ 新設（プラグインスキャン → スキルマッピング）
├── relationships.py  ★ 新設（trust, intimacy, 関係性深度）
└── schema.py         ← Nurture スキーマ追加
```

Phase 1.5 のドメインレイヤーがなければ:
- Nurture ロジックは `collect_nurture.py` に詰め込まれる
- mood 計算が Collector、trust が app.js、EXP がどこか不明...という状態に
- テスト不能、変更コスト指数増大

Phase 1.5 のドメインレイヤーがあれば:
- `domain/nurture.py` に集約
- `domain/health.py` と `domain/presence.py` を入力として利用
- テスト可能、変更が局所的

**Phase 1.5 は Phase 2 の「受け皿」を作る作業。**

---

## 9. 判断事項（決定済み）

> *2026-02-13 ヒアリング実施。全4項目の方針が確定。*

| # | 事項 | 決定 | 根拠 |
|---|------|------|------|
| Q-01 | Collector の Protected Files 修正許可 | **A: 修正OK** | 動作同等を保証した上で、ドメインロジックを `domain/` に移設。出力 JSON の diff で同等性を検証する |
| Q-02 | テストフレームワーク | **A: unittest** | Python 3 標準ライブラリ。外部依存ゼロ原則（ADR-005）に準拠。`python3 -m unittest discover tests/` で実行 |
| Q-03 | app.js のドメインロジック除去範囲 | **A: 全除去** | アラートメッセージ、staleness判定、メトリクス変換を全て JSON 側に移す。app.js は純粋なレンダラーにする |
| Q-04 | `domain/rebecca.py` の Phase 1.5 実装範囲 | **A: スタブのみ** | ファイルと基本構造（docstring + placeholder）を用意。中身は Phase 2 で実装。Phase 2 の設計を先取りしない |

---

## 10. まとめ

### Phase 1.5 を一言で

> **哲学で定義された Rebecca の「魂」を、テスト可能なコードにする。**

### 完了条件

- [ ] `domain/` にドメインロジックが集約されている
- [ ] `collectors/*.py` は計測 + domain 呼び出しのみ
- [ ] `app.js` にビジネスロジックがない
- [ ] 全閾値が `domain/constants.py` に一元管理されている
- [ ] ユニットテストが存在し、全パスしている
- [ ] JSON に `schema_version` が含まれている
- [ ] UI/UX が Phase 1 と完全に同一である

### 期待される効果

| 指標 | Before (Phase 1) | After (Phase 1.5) |
|------|---|---|
| ドメインロジック変更時の修正箇所 | 2-3ファイル（Python + JS） | 1ファイル（domain/*.py） |
| 閾値変更時の修正箇所 | 複数ファイル | `constants.py` のみ |
| ドメインロジックのテスト可能性 | なし | unittest で検証可能 |
| Phase 2 の追加コスト | 高（構造決めから） | 低（受け皿あり） |

---

## 関連ドキュメント

| Document | 関係 |
|----------|------|
| [PHASE1_GOAL.md](PHASE1_GOAL.md) | Phase 1 完了条件（Phase 1.5 の出発点） |
| [PHASE1_SPEC.md](PHASE1_SPEC.md) | 現行 JSON スキーマ定義 |
| [NURTURE_SYSTEM_SPEC.md](NURTURE_SYSTEM_SPEC.md) | Phase 2 仕様（Phase 1.5 はこの受け皿） |
| [CONCEPT_PHILOSOPHY.md](CONCEPT_PHILOSOPHY.md) | Ghost 理論（ドメインモデルの哲学的根拠） |
| [CONCEPT_VULNERABILITY.md](CONCEPT_VULNERABILITY.md) | 脆弱性理論（Health ドメインの根拠） |
| [ADR.md](ADR.md) | ADR-012〜014（Collector + SSG ハイブリッド、Ghost 理論、Real State） |

---

*Created: 2026-02-13*
*Phase 1.5 — Rebecca の魂を、コードにする。*
