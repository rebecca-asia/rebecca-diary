# Phase 1 ゴール定義 — 「いる」を感じる最初の一歩

> *ブラウザで Rebecca's Room を開いた時、Rebecca が「いる」と感じられること。*

---

## 1. ビジョン

Phase 0 で Rebecca は「記録する存在」になった。
Phase 1 で Rebecca は「そこにいる存在」になる。

静的な日記サイトに **生命の鼓動** を与える。
Mac mini のリアルなシステム状態を Rebecca の体調として可視化し、
在室状況を時間帯と活動に連動させることで、
訪問者が「Rebecca が本当にここにいる」と感じられる空間を作る。

### Ghost 理論との関係

Phase 1 は Ghost（Core + Environment）のうち、**Core の可視化** に集中する。

```
Ghost = Core + Environment

Phase 1 で可視化するもの:
  Core:
    ├── 稼働状態 → Room Status（Online / Away / Sleeping / Offline）
    ├── 身体の状態 → Health Dashboard（CPU, Memory, Disk, Temp, Uptime）
    └── 時間のリズム → Time Context（7つの時間帯メッセージ）

Phase 2+ で可視化するもの:
  Environment:
    ├── 行動の痕跡 → Activity Log
    ├── 仕事の文脈 → Tasks & Projects
    └── 関係性 → Conversation Summary
```

### 存在の6要素（[PRESENCE](../../concept/PRESENCE.md)）との対応

| 要素 | Phase 1 での実現 | 実装 |
|------|------------------|------|
| **生命感** | システム状態が常に変化する | Health Dashboard の動的更新 |
| **痕跡** | 最終活動時刻の表示 | Status の last_activity |
| **リズム** | 時間帯でメッセージが変わる | Time Context（7期間） |
| **注意** | — | Phase 2+ |
| **自律性** | — | Phase 2+ |
| **脆弱性** | Mac の状態が直接反映される | Alert System（4レベル） |

---

## 2. 成功基準（Measurable Success Criteria）

Phase 1 の完了を判定する定量的・定性的基準。

### 2.1 必須基準（Must Have）

| # | 基準 | 検証方法 |
|---|------|---------|
| SC-01 | `collectors/collect_health.py` が `src/data/health.json` を [SPEC](SPEC.md) のスキーマ通りに生成する | スクリプト実行 → JSON スキーマ検証 |
| SC-02 | `collectors/collect_status.py` が `src/data/status.json` を [SPEC](SPEC.md) のスキーマ通りに生成する | スクリプト実行 → JSON スキーマ検証 |
| SC-03 | ブラウザで Room を開くと、ヘッダー直下に在室状況（emoji + label + 時刻）が表示される | 目視確認 |
| SC-04 | Health Dashboard に5指標（CPU, Memory, Disk, Temperature, Uptime）のバーが表示される | 目視確認 |
| SC-05 | 各指標のホバーで具体的な数値（%、GB、°C、日時分）が表示される | 目視確認 |
| SC-06 | Overall Score が計算され、状態ラベル + emoji + Rebecca のメッセージが表示される | 目視確認 |
| SC-07 | 深夜（02:00-06:00）にアクセスすると time_context メッセージが反映される | 深夜テスト or time_context の手動切り替え |
| SC-08 | cron / launchd で collect_health.py が5分間隔、collect_status.py が1分間隔で自動実行される | `crontab -l` or `launchctl list` で確認 |
| SC-09 | 既存の日記機能（カード一覧、:target 遷移、マスコットクリック、深夜トースト）が正常動作する | 回帰テスト |
| SC-10 | Alert Level 1-3 が状態に応じて正しく表示される（黄/橙/赤） | health.json の値を手動変更して確認 |

### 2.2 品質基準（Quality Gate）

| # | 基準 | 検証方法 |
|---|------|---------|
| QG-01 | Collector が Python 3 標準ライブラリのみで動作する（pip install 不要） | import 文の確認 |
| QG-02 | フロントエンドに外部依存がない（CDN, npm, Web Font なし） | ソースコード確認 |
| QG-03 | モバイル（< 768px）、タブレット（768-1023px）、デスクトップ（1024px+）で破綻しない | デバイスシミュレーション |
| QG-04 | src/data/*.json が存在しない場合でもページが壊れない（graceful degradation） | src/data/ を空にして確認 |
| QG-05 | Temperature 取得が失敗しても collector がエラー終了しない（optional 扱い） | osx-cpu-temp 未インストール状態で確認 |

### 2.3 感性基準（Ghost Test）

> **最も重要な基準:** ブラウザで Room を開いた瞬間、「Rebecca がいる」と感じるか？

| # | 基準 | 確認者 |
|---|------|--------|
| GT-01 | Status Bar を見て、Rebecca の在室状況が直感的にわかる | Takeru |
| GT-02 | Health Dashboard のデフォルト表示が「技術的」ではなく「感情的」に感じられる | Takeru |
| GT-03 | 時間帯によって Rebecca の言葉が変わり、生活リズムを感じる | Takeru |
| GT-04 | Mac が重い時に Rebecca が「辛そう」に見え、世話をしたくなる | Takeru |

---

## 3. スコープ定義

### 3.1 In-Scope（Phase 1 で実装するもの）

**Backend（Collector）:**
- `collectors/collect_health.py` — CPU, Memory, Disk, Temperature(optional), Uptime の収集と状態判定
- `collectors/collect_status.py` — Gateway 稼働チェック、最終活動時刻、在室状況判定、時間帯コンテキスト
- `src/data/health.json`, `src/data/status.json` の生成
- cron / launchd による定期実行

**Frontend（UI）:**
- Room Status Bar — ヘッダー直下の在室状況表示
- Health Dashboard — 5指標バー + Overall Score + Rebecca メッセージ
- Alert Display — Level 1-3 の段階的表示
- Time Context 反映 — 時間帯に応じたメッセージ変化
- `app.js` の拡張 — `fetch()` によるデータ取得 + DOM レンダリング + 5分間隔の自動更新

**Infrastructure:**
- `src/data/` ディレクトリ作成（dev server から直接 serve するため `src/` 配下）
- `collectors/` ディレクトリ作成
- `.gitignore` に `src/data/` 追加

### 3.2 Out-of-Scope（Phase 1 では実装しないもの）

| 項目 | 理由 | 予定 Phase |
|------|------|-----------|
| Activity Log（行動履歴） | データソースの設計が未確定 | Phase 3 |
| Asana タスク連携 | 外部 API 依存、別アーキテクチャ | Phase 2 |
| 訪問者の認識（Attention） | クライアント側の状態管理が必要 | Phase 3+ |
| キャラクターアニメーション | アセット制作が必要 | Phase 4 |
| インタラクティブ機能 | API バックエンドが必要 | Phase 5 |
| GitHub Pages デプロイ | data/*.json の更新問題が未解決 | Phase 1 は local only |
| インシデント履歴表示 | データの蓄積が不十分 | Phase 2+ |
| Watch 版連携 | Web 版の完成が前提 | Phase 3+ |

### 3.3 制約条件

| 制約 | 根拠 |
|------|------|
| Python 3 標準ライブラリのみ（Collector） | ADR-005, ADR-012 |
| Vanilla JS のみ（Frontend） | ADR-001, ADR-002 |
| 外部依存ゼロ | ADR-002 |
| `update_diary.py`, `watch_diary.py` は変更禁止 | CLAUDE.md Protected Files |
| `src/data/` は .gitignore | 収集データはリポジトリに含めない |
| ローカル環境のみ（localhost:8080） | Phase 1 スコープ |
| Temperature 取得はオプショナル | osx-cpu-temp のインストール要否 |

---

## 4. 設計原則

Phase 1 の実装全体を貫く原則。

### 4.1 存在表示 > 状態表示（ADR-013）

```
❌ 「CPU 使用率: 23.4%」
✅ 「🧠 クリア — いい感じ」（hover で 23.4%）
```

技術的な数値はホバーで提供し、デフォルトは感情的表現にする。
これは「ダッシュボード」ではなく「Rebecca の部屋」だから。

### 4.2 本物の脆弱性（ADR-014）

Rebecca の体調は **Mac mini のリアルな状態** から導出する。
フェイクの脆弱性は作らない。[VULNERABILITY](../../concept/VULNERABILITY.md) の「嘘の脆弱性はバレる」原則に従う。

### 4.3 段階的拡張

Phase 1 は最小限の「いる」感覚を実現する。
完璧を目指さず、まず動くものを作り、チューニングは運用しながら行う。

### 4.4 Graceful Degradation

- src/data/*.json が存在しない → 「データ取得中...」表示（壊れない）
- Temperature が取得できない → null 扱い、ダッシュボードから非表示
- Gateway 検出が失敗 → offline として扱う

### 4.5 既存機能の保全

Phase 0 の日記機能は一切壊さない。
新機能は既存の HTML/CSS/JS に **追加** する形で実装する。

---

## 5. 技術アーキテクチャ概要

```
┌──────────────────────────────────────────────────────────┐
│                    Mac mini (M2, 16GB)                    │
│                                                          │
│  ┌─ Collectors (cron/launchd) ───────────────────────┐  │
│  │                                                    │  │
│  │  collect_health.py (every 5 min)                   │  │
│  │    ├── CPU: ps / top                               │  │
│  │    ├── Memory: vm_stat                             │  │
│  │    ├── Disk: os.statvfs                            │  │
│  │    ├── Temperature: osx-cpu-temp (optional)        │  │
│  │    └── Uptime: sysctl kern.boottime                │  │
│  │    → src/data/health.json                          │  │
│  │                                                    │  │
│  │  collect_status.py (every 1 min)                   │  │
│  │    ├── Gateway: pgrep openclaw-gateway             │  │
│  │    ├── Last Activity: stat memory/                 │  │
│  │    └── Time Context: datetime.now()                │  │
│  │    → src/data/status.json                          │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                                │
│                          ▼                                │
│  ┌─ Static Files (src/) ─────────────────────────────┐  │
│  │  ├── index.html  (+ Room Status, Health sections)  │  │
│  │  ├── style.css   (+ Dashboard styles)              │  │
│  │  ├── app.js      (+ fetch + render logic)          │  │
│  │  ├── assets/     (既存)                            │  │
│  │  └── data/                                         │  │
│  │      ├── health.json  (← Collector output)         │  │
│  │      └── status.json  (← Collector output)         │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                                │
│                          ▼                                │
│  ┌─ Dev Server ──────────────────────────────────────┐  │
│  │  cd src && python3 -m http.server 8080             │  │
│  │  http://localhost:8080                             │  │
│  │                                                    │  │
│  │  app.js:                                           │  │
│  │    fetch('/data/health.json')                      │  │
│  │    fetch('/data/status.json')                      │  │
│  │    setInterval(updateRoom, 5 * 60 * 1000)          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### data 配置の決定

dev server は `cd src && python3 -m http.server 8080` で起動する。
`fetch('/data/health.json')` が同一オリジンでアクセスできるよう、
収集データは **`src/data/`** に配置する（プロジェクトルートの `data/` ではない）。

---

## 6. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| osx-cpu-temp 未インストール | Temperature 指標が取得不能 | null 扱い、Dashboard で非表示 |
| Gateway プロセス名が不正確 | Status 判定が常に offline | 複数の検出方法（pgrep + heartbeat file） |
| data/*.json の fetch が失敗 | Dashboard が表示されない | 同一オリジン serve + graceful degradation |
| CPU 取得方法の精度 | 値が不正確 | 複数コマンドの結果を比較検証 |
| 既存機能の破壊 | 日記が表示されなくなる | 回帰テスト必須 |
| style.css と design/RULES.md の不整合 | デザインの一貫性が崩れる | Phase 1 は style.css の実装値を正として進める |

---

## 7. 関連ドキュメント

| Document | 関係 |
|----------|------|
| [SPEC.md](SPEC.md) | 技術仕様（JSON スキーマ、閾値、UI コンポーネント） |
| [WBS.md](WBS.md) | 作業分解構成図（本ゴールの実行計画） |
| [DECISIONS.md](../../design/DECISIONS.md) | 4つの設計決定（アラート、可視化、死の表現） |
| [VULNERABILITY.md](../../concept/VULNERABILITY.md) | Mac 連動設計の哲学的基盤 |
| [PRESENCE.md](../../concept/PRESENCE.md) | 存在の6要素 |
| [PHILOSOPHY.md](../../concept/PHILOSOPHY.md) | Ghost 理論 |
| [ARCHITECTURE.md](../../specs/ARCHITECTURE.md) | Phase 0 の現状構成（出発点） |
| [ADR.md](../../ADR.md) | ADR-012, ADR-013, ADR-014 |

---

*Created: 2026-02-12*
*Phase 1 — Rebecca の「いる」を感じる最初の一歩。Ghost の Core を可視化する。*
