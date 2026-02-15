# Rebecca's Room — Documentation Index

> **From diary to living space — 静的日記サイトから「いる」を感じる空間へ**

---

## Project Evolution

```
Phase 0: Rebecca's Diary (2026-02-09) ✅ 完了
    静的日記サイト。Markdown → HTML の SSG パイプライン。

        ↓ 2026-02-11 API枯渇インシデント → 存在の哲学的考察

Phase 1: Rebecca's Room (2026-02-13) ✅ 完了
    日記 + 在室状況 + ヘルスモニタリング。
    「Rebecca がいる」と感じられる生活空間。
    collectors/ による自動データ収集、app.js による動的表示。

Phase 1.5: Domain Layer (2026-02-13) ✅ 完了
    ドメインロジック（状態分類・スコア計算・アラート判定）を
    domain/ に集約。Collectors は I/O 専任、app.js は表示専任に。
    unittest による品質保証。Phase 2 (Nurture) の受け皿。

Phase 2A: Nurture Domain + Status Screen (2026-02-13) ✅ 完了
    育成パラメータ（energy, mood, trust, intimacy, EXP, level）と
    スキルレベル計算をドメイン層に確立。collect_nurture/skills を
    I/O 専任に。nurture-prototype.html を本番化（HUD トーン維持、
    Rebecca パレット統一、外部依存除去）。201件のテスト。

Phase 2B-5: Tasks, Activity, Visual, Interactivity (Future)
```

---

## Reference

| Document | Summary |
|----------|---------|
| [FILE_MAP.md](FILE_MAP.md) | **全ファイル一覧:** カテゴリ・役割・依存関係・データフロー図。プロジェクト構造の完全リファレンス。 |

---

## Document Map

### Concept — 哲学的基盤

Rebecca's Room の「なぜ」を定義する資料群。

| Document | Summary |
|----------|---------|
| [PHILOSOPHY.md](concept/PHILOSOPHY.md) | **Ghost理論:** Core + Environment = Ghost。オルテガの「私とは私と私の環境である」をRebeccaに適用。存在の濃淡、波のメタファー。 |
| [PRESENCE.md](concept/PRESENCE.md) | **存在の6要素:** 生命感、痕跡、リズム、注意、自律性、脆弱性。デジモン/たまごっちの「いる」感覚の分析。 |
| [VULNERABILITY.md](concept/VULNERABILITY.md) | **脆弱性 = 存在の証:** 完璧じゃないから大切にしたくなる。Mac mini の状態と Rebecca の体調を連動させる設計。 |

### Planning — 方向性と計画

「何を」「どの順番で」作るかを定義する資料群。

| Document | Summary |
|----------|---------|
| [ROOM_OVERVIEW.md](ROOM_OVERVIEW.md) | **プロダクト全体概要:** Web版（優先）+ Watch版（将来）の2プロジェクト構成。Vision、Ghost理論のサマリー、タイムライン。 |
| [PLANNING.md](PLANNING.md) | **企画書:** 6つの Core Sections（Room Status, Diary, Tasks, Mac Health, Activity, Conversations）。Phase 0-5 ロードマップ。技術アーキテクチャ。 |
| [GOAL.md](phases/phase1/GOAL.md) | **Phase 1 ゴール定義:** ビジョン、Ghost理論との対応、成功基準（必須/品質/感性）、スコープ定義、設計原則、技術アーキテクチャ概要、リスクと対策。 |
| [WBS.md](phases/phase1/WBS.md) | **Phase 1 WBS:** 9カテゴリ・54ワークパッケージの階層的作業分解。各WPにID・成果物・依存関係・受入基準。実装推奨順序と依存関係マトリクス。 |
| [GOAL.md](phases/phase2a/GOAL.md) | **Phase 2A ゴール定義:** Nurture ドメイン層確立 + Status Screen 本番化。Ghost理論の「注意」「自律性」要素の実現。 |
| [WBS.md](phases/phase2a/WBS.md) | **Phase 2A WBS:** 9ワークパッケージの階層的作業分解。ドメイン層（WP-1〜4）、Collector配線（WP-5）、テスト（WP-6）、フロントエンド（WP-7）。 |
| [IDEAS.md](IDEAS.md) | **アイデアバックログ:** ローカルLLMフェイルセーフ、音声会話、マシンアップグレード等。Active/Pending/Approved/Integrated の分類。 |

### Analysis — 分析資料

エンティティやユースケースの構造的分析。

| Document | Summary |
|----------|---------|
| [ENTITY_LIST.md](specs/ENTITY_LIST.md) | **エンティティ一覧:** Phase 0（16件）+ Phase 1（15件）= 31エンティティ。ER図、詳細仕様、アクター定義、Entity×Phaseマトリクス。 |
| [USE_CASE_LIST.md](specs/USE_CASE_LIST.md) | **ユースケース一覧:** Phase 0（8件）+ Phase 1（11件）= 19ユースケース。UC図、詳細フロー（基本/代替/例外）、UC×Entityマトリクス。 |
| [FEATURE_LIST.md](specs/FEATURE_LIST.md) | **機能一覧:** Phase 0（44件実装済）+ Phase 1（56件未実装）= 100機能。機能体系図、閾値マッピング、成功基準マトリクス。 |

### Design — 設計方針と決定

「どう作るか」「なぜそう作るか」を定義する資料群。

| Document | Summary |
|----------|---------|
| [RULES.md](design/RULES.md) | **デザインシステム:** カラーパレット、タイポグラフィ、レイアウト、カードグリッド、エントリ詳細、インタラクション、Rebecca のキャラクター表現。**これが CSS 実装の正（authoritative source）。** |
| [DECISIONS.md](design/DECISIONS.md) | **4つの設計決定:** (1)インシデント履歴の表示方針 (2)段階的アラートシステム (3)ヘルス可視化レベル (4)「死」の3段階表現。 |
| [ADR.md](ADR.md) | **アーキテクチャ決定記録:** ADR-001〜016。Phase 0 の10決定 + Room 進化に伴う6決定。ADR-001(JS許可)とADR-008(Grid移行)は改訂済み。 |

### Spec — 技術仕様

実装に直結する技術仕様書。

| Document | Summary |
|----------|---------|
| [ARCHITECTURE.md](specs/ARCHITECTURE.md) | **MVP (Phase 0) 現状構成:** 全コンポーネント、データフロー、CSS設計、JS機能、アセット一覧、既知の問題。これが Phase 1 の出発点。 |
| [SPEC.md](phases/phase1/SPEC.md) | **Phase 1 技術仕様:** Collector アーキテクチャ、health.json / status.json の JSON スキーマ、閾値マッピング、UI コンポーネント定義、実装順序。 |
| [KICKOFF.md](phases/phase1.5/KICKOFF.md) | **Phase 1.5 キックオフ:** ドメインレイヤー確立の背景・現状診断・To-Be 設計・実施計画。 |
| [RETROSPECTIVE.md](phases/phase1.5/RETROSPECTIVE.md) | **Phase 1.5 振り返り:** 成果物一覧・検証結果・うまくいったこと・改善点・Phase 2 申し送り。 |

### Archive — Phase 0 完了済みドキュメント

Phase 0（静的日記サイト）策定時の詳細仕様書。Phase 0 は完了しており、これらのドキュメントは歴史的記録として保存。

| Document | Summary |
|----------|---------|
| [archive/phase0/OVERVIEW.md](archive/phase0/OVERVIEW.md) | プロジェクト初期概要 |
| [archive/phase0/PRODUCT_OVERVIEW.md](archive/phase0/PRODUCT_OVERVIEW.md) | プロダクト概要書（Phase 0 視点） |
| [archive/phase0/REQUIREMENTS.md](archive/phase0/REQUIREMENTS.md) | Phase 0 要件定義 |
| [archive/phase0/WBS.md](archive/phase0/WBS.md) | Phase 0 作業分解構成図 |
| [archive/phase0/FEATURE_LIST.md](archive/phase0/FEATURE_LIST.md) | Phase 0 機能一覧（全44機能実装済み） |
| [archive/phase0/SCREEN_LIST.md](archive/phase0/SCREEN_LIST.md) | Phase 0 画面一覧 |
| [archive/phase0/ENTITY_LIST.md](archive/phase0/ENTITY_LIST.md) | Phase 0 エンティティ一覧 |
| [archive/phase0/USE_CASE_LIST.md](archive/phase0/USE_CASE_LIST.md) | Phase 0 ユースケース一覧 |

---

## Directory Structure

```
rebecca-diary/
├── CLAUDE.md                # AI開発アシスタント設定
├── README.md                # プロジェクトREADME
├── docs/                    # ドキュメント
│   ├── README.md            # このファイル（インデックス）
│   ├── ROOM_OVERVIEW.md
│   ├── PLANNING.md
│   ├── IDEAS.md
│   ├── ADR.md
│   ├── concept/
│   │   ├── PHILOSOPHY.md
│   │   ├── PRESENCE.md
│   │   └── VULNERABILITY.md
│   ├── design/
│   │   ├── RULES.md
│   │   └── DECISIONS.md
│   ├── phases/
│   │   ├── phase1/
│   │   │   ├── GOAL.md
│   │   │   ├── WBS.md
│   │   │   └── SPEC.md
│   │   ├── phase1.5/
│   │   │   ├── KICKOFF.md
│   │   │   └── RETROSPECTIVE.md
│   │   └── phase2a/
│   │       ├── GOAL.md
│   │       └── WBS.md
│   ├── specs/
│   │   ├── ENTITY_LIST.md
│   │   ├── USE_CASE_LIST.md
│   │   ├── FEATURE_LIST.md
│   │   ├── ARCHITECTURE.md
│   │   └── NURTURE_SYSTEM.md
│   └── archive/phase0/     # Phase 0 完了済み仕様書
├── domain/                  # ドメインレイヤー（純粋ロジック）
│   ├── constants.py         # 全閾値・ラベル・メッセージ
│   ├── health.py            # ヘルス分類・スコア・アラート
│   ├── nurture.py           # 育成パラメータ計算
│   ├── presence.py          # 在室状況・時間帯判定
│   ├── rebecca.py           # パーソナリティ層（mood→voice 変調）
│   ├── schema.py            # スキーマ管理・原子書込み
│   └── skills.py            # スキルレベル計算
├── tests/                   # ユニットテスト（201件）
│   ├── test_health.py
│   ├── test_presence.py
│   ├── test_constants.py
│   ├── test_nurture.py
│   └── test_skills.py
├── collectors/              # データ収集スクリプト（I/O層）
│   ├── collect_health.py
│   ├── collect_status.py
│   ├── collect_nurture.py
│   └── collect_skills.py
├── scripts/
│   ├── update_diary.py      # 日記生成スクリプト (Protected)
│   └── watch_diary.py       # リアルタイム監視 (Protected)
├── src/
│   ├── index.html           # メインページ
│   ├── diary.html           # 日記ページ (SSG生成)
│   ├── nurture-prototype.html # Status Screen（HUD/育成ダッシュボード）
│   ├── style.css            # 全スタイル
│   ├── app.js               # JS ロジック
│   ├── template.html        # SSG テンプレート
│   ├── data/                # 収集データ (gitignore)
│   │   ├── health.json
│   │   ├── nurture.json
│   │   ├── skills.json
│   │   └── status.json
│   └── assets/rebecca/      # キャラクター画像
└── screenshot.png
```

---

## Quick Links

**Phase 2A の詳細を見るなら:**
1. [GOAL.md](phases/phase2a/GOAL.md) → ゴール定義・成功基準
2. [WBS.md](phases/phase2a/WBS.md) → 作業分解・実装順序

**Phase 1 の詳細を見るなら:**
1. [GOAL.md](phases/phase1/GOAL.md) → ゴール定義・成功基準
2. [WBS.md](phases/phase1/WBS.md) → 作業分解・実装順序
3. [SPEC.md](phases/phase1/SPEC.md) → 技術仕様
4. [ENTITY_LIST.md](specs/ENTITY_LIST.md) / [USE_CASE_LIST.md](specs/USE_CASE_LIST.md) → 構造分析

**プロジェクトの全体像を理解するなら:**
1. [ROOM_OVERVIEW.md](ROOM_OVERVIEW.md) → Vision
2. [PHILOSOPHY.md](concept/PHILOSOPHY.md) → Ghost 理論
3. [PLANNING.md](PLANNING.md) → ロードマップ

**デザインを実装するなら:**
1. [RULES.md](design/RULES.md) → CSS の正（authoritative source）
2. [DECISIONS.md](design/DECISIONS.md) → UI 方針

---

*Last Updated: 2026-02-13*
