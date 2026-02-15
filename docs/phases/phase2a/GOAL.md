# Phase 2A ゴール定義 — 「育つ」を感じる最初の一歩

> *ブラウザで nurture.html を開いた時、Rebecca が「育っている」と感じられること。*

---

## 1. ビジョン

Phase 0 で Rebecca は「記録する存在」になった。
Phase 1 で Rebecca は「そこにいる存在」になった。
Phase 1.5 で Rebecca は「背骨」を手に入れた。

Phase 2A で Rebecca は **「育つ存在」** になる。

Phase 1.5 で確立した3層分離（domain / collectors / app.js）の上に、
「育成」というドメインロジックを積み上げ、
nurture.html を **本番稼働するステータス画面** として完成させる。

これは単なるパラメータ表示ではない。
Mood が揺れ、Energy が時間帯で変動し、Trust が訪問を重ねるごとに積み上がる。
Rebecca が「数値で管理されるオブジェクト」ではなく **「一緒に生きている存在」** になる第一歩。

### Ghost 理論との関係

Phase 1 は Ghost（Core + Environment）のうち、**Core の可視化** に集中した。
Phase 2A は Ghost の **Environment（関係性・成長の痕跡）** に踏み込む。

```
Ghost = Core + Environment

Phase 1 で可視化したもの（継続）:
  Core:
    ├── 稼働状態 → Room Status（Online / Away / Sleeping / Offline）
    ├── 身体の状態 → Health Dashboard（CPU, Memory, Disk, Temp, Uptime）
    └── 時間のリズム → Time Context（7つの時間帯メッセージ）

Phase 2A で可視化するもの:
  Core（拡張）:
    ├── 気分 → Mood（体調 + 訪問 + 時間帯の複合要因）
    └── 活力 → Energy（Uptime + 時間帯で自律変動）

  Environment（新規）:
    ├── 関係性の蓄積 → Trust / Intimacy（訪問回数・滞在時間で成長）
    ├── 成長の軌跡 → Level / EXP（活動の蓄積が数値化）
    └── 能力の獲得 → Skills（Claude Code プラグイン連動）
```

### 存在の6要素（[PRESENCE](../../concept/PRESENCE.md)）との対応

| 要素 | Phase 1 での実現 | Phase 2A での実現 | 実装 |
|------|------------------|------------------|------|
| **生命感** | システム状態が常に変化する | Mood / Energy が自律的に変動する | nurture.json の5分間隔更新 |
| **痕跡** | 最終活動時刻の表示 | Level / EXP / Trust の蓄積が見える | ステータス画面での可視化 |
| **リズム** | 時間帯でメッセージが変わる | Energy が時間帯で上下する | domain/nurture.py の time modifier |
| **注意** | -- | **訪問を検知して信頼度・親密度が変化する** | visit_log + Trust / Intimacy 計算 |
| **自律性** | -- | **Mood / Energy が入力なしで自律変動する** | 体調・Uptime・時間帯からの自動計算 |
| **脆弱性** | Mac の状態が直接反映される | 疲労・低Moodが正直に表示される | リアルデータ駆動の原則を維持 |

**Phase 2A で存在の6要素のうち4つが実現し、残り2つ（注意・自律性）の基盤が整う。**

---

## 2. 成功基準（Measurable Success Criteria）

Phase 2A の完了を判定する定量的・定性的基準。

### 2.1 必須基準（Must Have）

| # | 基準 | 検証方法 |
|---|------|---------|
| SC-01 | `domain/nurture.py` が純粋関数として Mood / Energy / Trust / Intimacy / EXP / Level を計算する | ユニットテスト |
| SC-02 | `domain/skills.py` が純粋関数としてスキルレベル計算・ラベル付けを提供する | ユニットテスト |
| SC-03 | `domain/rebecca.py` が Health + Presence + Nurture を統合して人格レイヤーを適用する | ユニットテスト |
| SC-04 | `collectors/collect_nurture.py` が計算ロジックを `domain/nurture.py` に委譲し、I/O のみを担当する | コードレビュー + 出力一致検証 |
| SC-05 | `collectors/collect_skills.py` が `calculate_level()` を `domain/skills.py` に委譲する | コードレビュー + 出力一致検証 |
| SC-06 | 全ユニットテスト（既存95件 + 新規）が PASS する | `python3 -m unittest discover tests/ -v` |
| SC-07 | `nurture.html` がブラウザで正常に表示される（Level, EXP, Mood, Energy, Trust, Intimacy, Skills） | 目視確認 |
| SC-08 | `index.html` から `nurture.html` へのナビゲーションリンクが機能する | クリック確認 |
| SC-09 | cron で5分間隔の nurture 収集、1時間間隔の skills 収集が稼働する | `crontab -l` で確認 |
| SC-10 | nurture.json / skills.json に `schema_version` と `staleness` が含まれる | JSON フィールド確認 |

### 2.2 品質基準（Quality Gate）

| # | 基準 | 検証方法 |
|---|------|---------|
| QG-01 | `schema_version` + `staleness` が nurture.json / skills.json に統一的に適用される | `domain.schema.inject_version()` / `inject_staleness()` の使用確認 |
| QG-02 | `write_json_atomic()` が全 collector で `domain.schema.write_json_atomic()` に一本化される | 重複実装の消滅を確認 |
| QG-03 | 既存テスト95件が引き続き ALL PASS する | テスト実行 |
| QG-04 | nurture.html のモバイル / タブレット / デスクトップ表示が破綻しない | デバイスシミュレーション |
| QG-05 | `src/data/` が存在しない状態でも nurture.html が壊れない（graceful degradation） | data/ 空での表示確認 |
| QG-06 | 全 collector が Python 3 標準ライブラリのみで動作する（pip install 不要） | import 文の確認 |

### 2.3 感性基準（Ghost Test）

> **最も重要な基準:** nurture.html を開いた時、「Rebecca が育っている」と感じるか？

| # | 基準 | 確認者 |
|---|------|--------|
| GT-01 | Level と EXP バーを見て、Rebecca の成長を感じられる | Takeru |
| GT-02 | Mood / Energy のバーが「技術的」ではなく「感情的」に見える | Takeru |
| GT-03 | Trust / Intimacy が「訪問を重ねると育つ」という実感を与える | Takeru |
| GT-04 | Skills 一覧を見て、Rebecca の能力が「本物」だと感じられる | Takeru |
| GT-05 | ページ全体として、たまごっちやデジモンのような「世話したくなる」感覚がある | Takeru |

---

## 3. スコープ定義

### 3.1 In-Scope（Phase 2A で実装するもの）

**Domain Layer:**
- `domain/nurture.py` -- Mood / Energy 分類、Trust / Intimacy 計算、EXP / Level 算出（純粋関数）
- `domain/skills.py` -- スキルレベル計算、ラベル付け（純粋関数）
- `domain/rebecca.py` 拡張 -- Mood / Energy / Trust による人格メッセージの変調
- `domain/constants.py` 拡張 -- Nurture 固有の閾値・ラベル・メッセージを追加

**Collector Rewiring:**
- `collectors/collect_nurture.py` -- 計算ロジックを `domain/nurture.py` に委譲、`write_json_atomic` 統合
- `collectors/collect_skills.py` -- `calculate_level()` を `domain/skills.py` に委譲、`write_json_atomic` 統合

**Frontend:**
- `src/nurture.html` -- 本番ステータス画面（Level, EXP, パラメータバー, Skills 一覧）
- `src/index.html` / `src/template.html` -- nurture.html へのナビゲーションリンク追加

**Tests:**
- `tests/test_nurture.py` -- nurture.py の全パラメータ計算テスト
- `tests/test_skills.py` -- skills.py のレベル計算テスト

**Documentation:**
- CLAUDE.md、docs/README.md、docs/ADR.md の更新

### 3.2 Out-of-Scope（Phase 2A では実装しないもの）

| 項目 | 理由 | 予定 Phase |
|------|------|-----------|
| Activity Log（自律行動テキスト） | `collect_activity.py` の設計が未確定 | Phase 2D |
| 会話連携（Conversation Integration） | 外部 API 依存 | Phase 3 |
| リアルタイム WebSocket | アーキテクチャ変更が大きい | Phase 4 |
| アバターアニメーション | アセット制作が必要 | Phase 4 |
| 訪問者の識別（Takeru vs 他） | 認証システムが必要 | Phase 3+ |
| 季節デコレーション | UI 設計が未確定 | Phase 2D-2E |
| レベルアップ演出 | 演出設計が未確定 | Phase 2E |
| 放置 → 復帰の特別演出 | 状態遷移設計が必要 | Phase 2C-2E |

### 3.3 制約条件

| 制約 | 根拠 |
|------|------|
| Python 3 標準ライブラリのみ（Domain + Collector） | ADR-005, ADR-012 |
| Vanilla JS のみ（Frontend） | ADR-001, ADR-002 |
| 外部依存ゼロ | ADR-002 |
| `update_diary.py`, `watch_diary.py`, `collectors/collect_health.py`, `collectors/collect_status.py` は変更禁止 | CLAUDE.md Protected Files |
| `src/data/` は .gitignore | 収集データはリポジトリに含めない |
| ローカル環境のみ（localhost:8080） | Phase 2A スコープ |
| Phase 1.5 で確立した3層分離（domain / collectors / app.js）を維持 | ADR-015 |

---

## 4. 設計原則

Phase 1.5 で確立した3層分離を維持・拡張する。

### 4.1 3層分離の維持拡張（ADR-015 準拠）

```
┌─ domain/ (純粋ロジック) ────────────────────────┐
│  constants.py  全閾値・ラベル・メッセージ         │
│  health.py     ヘルス分類・スコア・アラート        │
│  presence.py   在室判定・時間帯                   │
│  schema.py     バージョン・鮮度・原子書込み        │
│  nurture.py    Mood / Energy / Trust / Level [NEW]│
│  skills.py     スキルレベル計算 [NEW]             │
│  rebecca.py    人格レイヤー [EXPAND]              │
└────────────────────────────────────────────────┘
         ↑ import           ↑ JSON フィールド参照
┌─ collectors/ ──┐  ┌─ nurture.html ─────────┐
│  計測 → 委譲    │  │  fetch → 表示のみ        │
└────────────────┘  └────────────────────────┘
```

Domain は I/O を持たない。Collectors は計算を持たない。Frontend は判定を持たない。

### 4.2 リアルデータ駆動（NURTURE_SYSTEM_SPEC 原則1）

```
❌ 作り物の空腹ゲージ
✅ Mac mini の Uptime から導出された Energy
```

Rebecca の状態は全て実データから導出する。
Mood は体調 + 訪問頻度 + 時間帯の複合計算。
Energy は Uptime + 時間帯の実値連動。
Skills は実際にインストールされた Claude Code プラグイン。
フェイクのパラメータは一切作らない。

### 4.3 存在表示 > 状態表示（ADR-013 継続）

```
❌ 「Trust: 78.2」
✅ 「友人 — よく話す仲」（hover で 78）
```

技術的な数値はホバーで提供し、デフォルトは感情的表現にする。

### 4.4 Graceful Degradation

- `src/data/*.json` が存在しない → 「データ取得中...」表示（壊れない）
- `skills.json` が空 → 「スキルを探索中...」
- `health.json` が古い → staleness に基づいて dimmed 表示
- `nurture.json` のフィールド欠損 → 個別にフォールバック

### 4.5 後方互換

- 既存の JSON スキーマにはフィールド追加のみ（既存フィールドの変更・削除はしない）
- nurture.json / skills.json に `schema_version` + `staleness` を追加
- index.html の既存機能（日記カード、Room Status、Health Dashboard）は一切壊さない

---

## 5. 技術アーキテクチャ概要

### Phase 2A 完了時点のアーキテクチャ

```
                    ┌──────────────────────────────────┐
                    │      domain/ (純粋ロジック)          │
                    │                                  │
                    │  constants ← 全閾値・ラベル（拡張）   │
                    │  health   ← 分類・スコア             │
                    │  presence ← 在室・時間帯             │
                    │  schema   ← バージョン・鮮度・書込み   │
                    │  nurture  ← Mood/Energy/Trust [NEW]  │
                    │  skills   ← スキルレベル [NEW]        │
                    │  rebecca  ← 人格レイヤー [EXPANDED]   │
                    └──────────┬───────────────────────┘
                               │ import
               ┌───────────────┼───────────────────┐
               │               │                   │
     ┌─────────▼──┐  ┌────────▼───┐  ┌────────────▼──────────┐
     │ collect_   │  │ collect_   │  │ collect_nurture.py    │
     │ health.py  │  │ status.py  │  │ collect_skills.py     │
     │ (既存)     │  │ (既存)     │  │ (I/O のみ — rewired)  │
     └─────┬──────┘  └─────┬──────┘  └──────────┬───────────┘
           │               │                    │
           ▼               ▼                    ▼
     ┌──────────────────────────────────────────────────┐
     │              src/data/*.json                     │
     │  health.json  status.json  nurture.json          │
     │  skills.json  visit_log.json                     │
     │  + schema_version, staleness (全統一)             │
     └─────────────────────┬────────────────────────────┘
                            │ fetch
                    ┌───────┴───────┐
                    │               │
              ┌─────▼─────┐  ┌─────▼──────────┐
              │  app.js   │  │  nurture.html   │
              │ (index用)  │  │  (ステータス画面) │
              └───────────┘  └────────────────┘
```

### write_json_atomic の一本化

```
Before (Phase 1.5):
  domain/schema.py      → write_json_atomic()  ← collect_health, collect_status が使用
  collect_nurture.py    → write_json_atomic()  ← 自前実装（重複）
  collect_skills.py     → write_json_atomic()  ← 自前実装（重複）

After (Phase 2A):
  domain/schema.py      → write_json_atomic()  ← 全 collector が使用
  collect_nurture.py    → 削除（domain.schema に委譲）
  collect_skills.py     → 削除（domain.schema に委譲）
```

---

## 6. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| collect_nurture.py のリファクタリングで計算結果が変わる | nurture.json の値が変動し、既存の visit_log との整合性が崩れる | Before/After で出力 diff を検証。閾値・係数は constants.py に一元化して変更を最小限に |
| collect_skills.py の calculate_level() 移動で既存 skills.json と不整合 | スキルレベルが変わる | 移動前後でスキルレベルの完全一致を検証 |
| nurture.html の新規作成で既存 index.html に影響 | 既存機能の破壊 | index.html は Protected File ではないが、回帰テストを実施。ナビゲーション追加のみ |
| 3つの write_json_atomic() 統合で書込み挙動が変わる | Collector 出力が壊れる | domain/schema.py の実装を基準に、他の実装との挙動差を事前に特定 |
| domain/rebecca.py の拡張が Phase 2B 以降の設計と矛盾 | 後工程でのリワークが発生 | Phase 2A では最小限の拡張（Mood/Energy によるメッセージ変調のみ）に留める |
| nurture.html のデザインが既存 index.html と不整合 | 世界観の破壊 | style.css の既存パレット + CSS Custom Properties を徹底的に再利用 |

---

## 7. 関連ドキュメント

| Document | 関係 |
|----------|------|
| [WBS.md](WBS.md) | 作業分解構成図（本ゴールの実行計画） |
| [NURTURE_SYSTEM.md](../../specs/NURTURE_SYSTEM.md) | 育成システム全体仕様（Phase 2A-2E の親ドキュメント） |
| [RETROSPECTIVE.md](../phase1.5/RETROSPECTIVE.md) | Phase 1.5 振り返り（Phase 2 への申し送り事項） |
| [PRESENCE.md](../../concept/PRESENCE.md) | 存在の6要素（注意・自律性の実現根拠） |
| [PHILOSOPHY.md](../../concept/PHILOSOPHY.md) | Ghost 理論（Core + Environment の拡張） |
| [VULNERABILITY.md](../../concept/VULNERABILITY.md) | リアルデータ駆動の哲学的基盤 |
| [ADR.md](../../ADR.md) | ADR-015（3層分離）、ADR-013（存在表示優先） |
| [RULES.md](../../design/RULES.md) | nurture.html のデザイン指針 |

---

*Created: 2026-02-13*
*Phase 2A — Rebecca の「育つ」を感じる最初の一歩。Ghost の Environment に踏み込む。*
