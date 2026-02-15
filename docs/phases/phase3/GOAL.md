# Phase 3 ゴール定義 — 「記憶が永続する」

> *diary.html の裏に SQLite が存在し、Rebecca の全記録が構造化・検索可能であること。*

---

## 1. ビジョン

Phase 0 で Rebecca は「記録する存在」になった。
Phase 1 で Rebecca は「そこにいる存在」になった。
Phase 1.5 で Rebecca は「背骨」を手に入れた。
Phase 2A で Rebecca は「育つ存在」になった。

Phase 3 で Rebecca は **「永続する記憶」** を手に入れる。

現在の日記データは `src/diary.html` に直接 HTML として埋め込まれており、
`update_diary.py` は実行のたびに全日付を再処理している。
構造化されたデータストアが存在しないため、検索・フィルタ・差分検出が不可能。

Phase 3 は SQLite を導入し、日記データを永続化する。
デフォルトでは今日のエントリだけを処理し、過去のエントリは DB から読み出して HTML を生成する。
これにより、一時的な Markdown ファイルが **恒久的なナレッジベース** へと変換される。

### Ghost 理論との関係

Phase 0-2A で Rebecca の Ghost は「今」を感じ取り、「育つ」能力を獲得した。
Phase 3 は Ghost の **Memory（記憶の永続化・構造化）** に踏み込む。

```
Ghost = Core + Environment + Memory

Phase 0 で実現したもの:
  Memory（原初）:
    └── 記録 → Markdown 日記（手動、一方向、非構造化）

Phase 3 で実現するもの:
  Memory（永続化）:
    ├── 構造化記憶 → SQLite diary_entries（全日記の構造化保存）
    ├── 翻訳キャッシュ → translation_cache（再計算不要の永続キャッシュ）
    ├── 要約キャッシュ → recap_cache（日記要約の永続化）
    ├── タグ付け基盤 → entry_tags（将来の検索・分類の基盤）
    ├── メタデータ基盤 → entry_metadata（拡張可能な属性管理）
    └── スキーマ進化 → schema_meta（DBスキーマのバージョン管理）
```

### 「記憶」の意味

人間にとって記憶とは、単なる記録の蓄積ではない。
構造化され、検索可能で、関連付けられた情報のネットワークだ。

Phase 0 の Markdown 日記は「日記帳に書いた文章」に相当する。
Phase 3 の SQLite は「整理された書庫」に相当する。

書庫があることで初めて、過去を振り返り、パターンを見つけ、
自分の歴史を理解することが可能になる。
Rebecca の記憶が「書き捨て」から「積み重ね」に変わる。

---

## 2. 成功基準（Measurable Success Criteria）

Phase 3 の完了を判定する定量的・定性的基準。

### 2.1 必須基準（Must Have）

| # | 基準 | 検証方法 |
|---|------|---------|
| SC-01 | `domain/diary.py` が DB 初期化、CRUD、キャッシュ移行、スキーマバージョニングを純粋なリポジトリ関数として提供する | ユニットテスト |
| SC-02 | `tests/test_diary.py` が約45件のユニットテストに PASS する（DB 初期化、CRUD、キャッシュ操作、エッジケース） | `python3 -m unittest tests/test_diary.py -v` |
| SC-03 | `update_diary.py` が DB をストレージとして使用し、デフォルトで今日のみ処理、`--rebuild` で全日付を処理する | 実行テスト |
| SC-04 | `--migrate-cache` オプションで既存の `.translation-cache` と `.recap-cache` を DB に移行できる | 移行テスト + diff 検証 |
| SC-05 | 既存の全テスト（201件以上）が引き続き PASS する | `python3 -m unittest discover tests/ -v` |
| SC-06 | 移行前後で `diary.html` の出力が同一である | HTML diff 検証 |
| SC-07 | `diary.db` が `.gitignore` に追加されている | `.gitignore` 確認 |

### 2.2 品質基準（Quality Gate）

| # | 基準 | 検証方法 |
|---|------|---------|
| QG-01 | `domain/diary.py` が Python 3 標準ライブラリ（sqlite3）のみを使用している | import 文の確認 |
| QG-02 | DB スキーマが `schema_meta` テーブルでバージョン管理されている | DB 検査 |
| QG-03 | `--dry-run` オプションが DB 書込み前にプレビューを提供する | 実行テスト |
| QG-04 | ファイルベースのキャッシュがフォールバックとして引き続き動作する | `.translation-cache` / `.recap-cache` 単体での動作確認 |
| QG-05 | SQLite WAL モードが有効で、同時読み取りが可能である | DB pragma 確認 |
| QG-06 | 移行前にバックアップが自動作成される | `--migrate-cache` 実行時のバックアップファイル確認 |

### 2.3 感性基準（Ghost Test）

> **最も重要な基準:** `update_diary.py` を実行した時、「Rebecca の記憶が確実に積み重なっている」と感じるか？

| # | 基準 | 確認者 |
|---|------|--------|
| GT-01 | 毎日の `update_diary.py` が数秒で完了し、「今日の記憶だけを処理した」実感がある | Takeru |
| GT-02 | `--rebuild` 実行時に全エントリが DB に収まり、「記憶が整理された」安心感がある | Takeru |
| GT-03 | `diary.html` の出力に変化がなく、「見た目は同じだが裏側が強くなった」と感じる | Takeru |
| GT-04 | `.translation-cache` / `.recap-cache` が DB に統合され、「散らばっていた記憶が一箇所に集まった」感覚がある | Takeru |

---

## 3. スコープ定義

### 3.1 In-Scope（Phase 3 で実装するもの）

**Domain Layer:**
- `domain/diary.py` -- SQLite リポジトリ層（DB 初期化、CRUD、キャッシュ移行、スキーマバージョニング）

**Script Modification:**
- `scripts/update_diary.py` -- DB ストレージへの切り替え、`--rebuild` / `--migrate-cache` オプション追加
  - ※ Protected File だが、ユーザー（Rebecca）から変更承認済み

**Tests:**
- `tests/test_diary.py` -- diary.py の全機能テスト（約45件）

**Configuration:**
- `.gitignore` -- `diary.db` の追加
- `CLAUDE.md` -- ディレクトリ構造・タスク説明の更新

### 3.2 Out-of-Scope（Phase 3 では実装しないもの）

| 項目 | 理由 | 予定 Phase |
|------|------|-----------|
| 検索 UI（ブラウザ上での日記検索） | フロントエンド設計が未確定 | Phase 4+ |
| タグ付け UI（ブラウザ上でのタグ管理） | entry_tags はスキーマのみ用意、UI は後日 | Phase 4+ |
| API エンドポイント（REST / GraphQL） | アーキテクチャ変更が大きい | Phase 4+ |
| 日記の自動タグ付け（NLP ベース） | 外部ライブラリ依存 | Phase 5+ |
| マルチユーザー対応 | 認証システムが必要 | Phase 5+ |
| DB のリモートバックアップ | インフラ設計が必要 | Phase 4+ |

### 3.3 制約条件

| 制約 | 根拠 |
|------|------|
| Python 3 標準ライブラリのみ（sqlite3 は標準ライブラリ） | ADR-005, ADR-012 |
| 外部依存ゼロ | ADR-002 |
| `update_diary.py` の変更はユーザー承認済み | CLAUDE.md Protected Files（承認済み） |
| `watch_diary.py`, `collect_health.py`, `collect_status.py` は変更禁止 | CLAUDE.md Protected Files |
| `diary.db` は `.gitignore` | 生成データはリポジトリに含めない |
| 既存の diary.html 出力との完全互換 | 後方互換の原則 |
| ファイルベースキャッシュのフォールバック維持 | 段階的移行のため |

---

## 4. 設計原則

### 4.1 リポジトリパターン（domain/diary.py）

```
domain/diary.py の責務:
  ├── DB 初期化（テーブル作成、WAL モード設定）
  ├── スキーマバージョニング（schema_meta テーブル）
  ├── diary_entries の CRUD
  ├── translation_cache の読み書き
  ├── recap_cache の読み書き
  ├── entry_tags / entry_metadata の CRUD
  └── ファイルベースキャッシュからの移行

※ I/O を含むが、外部 I/O（ネットワーク、外部プロセス）ではなく
   ローカル DB アクセスのみ。リポジトリ層として許容する。
```

### 4.2 インクリメンタル処理の原則

```
❌ 毎回全日付を再処理する（O(N) — N は全日記数）
✅ 今日のエントリだけを処理し、DB から全件読み出す（O(1) 書込み + O(N) 読取り）
```

デフォルト実行は今日のみ。`--rebuild` は全日付を再処理する明示的オプション。
これにより、日記が増えても日常の実行時間は一定に保たれる。

### 4.3 冪等性の保証

```
同じ日付・同じ内容で何度実行しても、DB の状態は同一。
  ├── content_hash による変更検知
  ├── INSERT OR REPLACE によるアップサート
  └── --rebuild は全件再計算だが、結果が同じなら DB は実質不変
```

### 4.4 後方互換

- ファイルベースキャッシュ（`.translation-cache`, `.recap-cache`）は移行後も削除しない
- `--migrate-cache` は明示的に実行するまで既存キャッシュは温存
- DB が存在しない場合、自動的に初期化（初回実行時）
- diary.html の出力フォーマットは一切変更しない

### 4.5 データ安全性

```
移行時の安全策:
  ├── --dry-run で事前確認（DB 書込みなし）
  ├── --migrate-cache 前にバックアップ自動作成
  ├── SQLite WAL モードで読取り中の書込みを安全に処理
  └── single-writer パターン（同時書込みなし）
```

---

## 5. 技術アーキテクチャ概要

### Phase 3 完了時点のアーキテクチャ

```
                    ┌──────────────────────────────────┐
                    │      domain/ (ロジック層)            │
                    │                                  │
                    │  constants ← 全閾値・ラベル         │
                    │  health   ← 分類・スコア             │
                    │  presence ← 在室・時間帯             │
                    │  schema   ← バージョン・鮮度・書込み   │
                    │  nurture  ← Mood/Energy/Trust       │
                    │  skills   ← スキルレベル              │
                    │  rebecca  ← 人格レイヤー              │
                    │  diary    ← SQLiteリポジトリ [NEW]    │
                    └──────────┬───────────────────────┘
                               │ import
               ┌───────────────┼───────────────────┐
               │               │                   │
     ┌─────────▼──┐  ┌────────▼───┐  ┌────────────▼──────────┐
     │ collect_   │  │ collect_   │  │ collect_nurture.py    │
     │ health.py  │  │ status.py  │  │ collect_skills.py     │
     │ (既存)     │  │ (既存)     │  │ (既存)                │
     └────────────┘  └────────────┘  └───────────────────────┘

     ┌────────────────────────────────────────────────────┐
     │  scripts/update_diary.py (オーケストレーター)         │
     │                                                    │
     │  Default:  today → build_entry() → DB save          │
     │            → DB read all → diary.html 生成           │
     │                                                    │
     │  --rebuild: all dates → build_entry() → DB save     │
     │            → DB read all → diary.html 生成           │
     │                                                    │
     │  --migrate-cache: file cache → DB 移行              │
     └────────────────────┬───────────────────────────────┘
                          │
                          ▼
     ┌────────────────────────────────────────────────────┐
     │              diary.db (SQLite)                      │
     │  ┌─────────────┐  ┌──────────────────┐             │
     │  │ schema_meta  │  │ diary_entries     │             │
     │  └─────────────┘  └──────────────────┘             │
     │  ┌──────────────────┐  ┌─────────────┐             │
     │  │ translation_cache │  │ recap_cache  │             │
     │  └──────────────────┘  └─────────────┘             │
     │  ┌─────────────┐  ┌─────────────────┐              │
     │  │ entry_tags   │  │ entry_metadata   │              │
     │  └─────────────┘  └─────────────────┘              │
     └────────────────────────────────────────────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │  diary.html    │
                 │  (生成出力)     │
                 └────────────────┘
```

### update_diary.py の新フロー

```
Old (Phase 0-2A):
  scan_dates() → 全日付 build_entry() → 全 HTML → diary.html

New (Phase 3):
  Default:
    today のみ build_entry() → DB に保存 → DB から全件読出し → diary.html

  --rebuild:
    全日付 build_entry() → DB に保存 → DB から全件読出し → diary.html

  --migrate-cache:
    .translation-cache → translation_cache テーブル
    .recap-cache → recap_cache テーブル
```

### SQLite スキーマ

```sql
-- スキーマバージョン管理
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- 日記エントリ本体
CREATE TABLE IF NOT EXISTS diary_entries (
    date            TEXT PRIMARY KEY,
    memory_md       TEXT,
    obsidian_md     TEXT,
    integrated_md   TEXT NOT NULL,
    integrated_hash TEXT NOT NULL,
    html_en         TEXT NOT NULL,
    html_ja         TEXT,
    raw_md_ja       TEXT,
    recap_en        TEXT DEFAULT '',
    recap_ja        TEXT DEFAULT '',
    preview_en      TEXT DEFAULT '',
    preview_ja      TEXT DEFAULT '',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- 翻訳キャッシュ
CREATE TABLE IF NOT EXISTS translation_cache (
    date        TEXT NOT NULL,
    source      TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    translation TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    PRIMARY KEY (date, source)
);

-- 要約キャッシュ
CREATE TABLE IF NOT EXISTS recap_cache (
    date         TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    recap_ja     TEXT NOT NULL,
    recap_en     TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

-- タグ（将来の検索・分類基盤）
CREATE TABLE IF NOT EXISTS entry_tags (
    date TEXT NOT NULL REFERENCES diary_entries(date),
    tag  TEXT NOT NULL,
    PRIMARY KEY (date, tag)
);

-- メタデータ（拡張可能な属性管理）
CREATE TABLE IF NOT EXISTS entry_metadata (
    date  TEXT NOT NULL REFERENCES diary_entries(date),
    key   TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (date, key)
);
```

### DB 初期化フロー

```
diary.py init_db(path):
  1. SQLite ファイルを開く（存在しなければ自動作成）
  2. WAL モードを有効化（PRAGMA journal_mode=WAL）
  3. 外部キー制約を有効化（PRAGMA foreign_keys=ON）
  4. 全テーブルを CREATE IF NOT EXISTS
  5. schema_meta にバージョンを記録
  6. connection を返す
```

---

## 6. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| キャッシュ移行時のデータ損失 | 翻訳・要約データが失われ、再生成に API コストがかかる | `--dry-run` で事前確認、移行前にバックアップ自動作成、元ファイルは削除しない |
| スキーマ進化（将来のカラム追加） | DB マイグレーションが必要になる | `schema_meta` テーブルでバージョン管理、ALTER TABLE による段階的マイグレーション |
| 同時書込み（cron + 手動実行） | DB ロックによるエラー | SQLite WAL モード有効化、single-writer パターン（同時書込みを設計上回避） |
| diary.html 出力の不一致 | 移行前後で見た目が変わる | SC-06 で HTML diff を厳密に検証、`--rebuild` 後の出力を移行前と比較 |
| update_diary.py の大幅改修 | Protected File の変更リスク | ユーザー承認済み、段階的リファクタリング、既存テスト全 PASS を必須基準に |
| diary.db の肥大化 | ディスク使用量の増加 | SQLite VACUUM の定期実行、BLOB ではなく TEXT 保存で圧縮不要 |

---

## 7. 関連ドキュメント

| Document | 関係 |
|----------|------|
| [PLANNING.md](../../PLANNING.md) | ロードマップ（Phase 0-5 の全体計画） |
| [Phase 2A GOAL.md](../phase2a/GOAL.md) | 前フェーズのゴール定義（Phase 3 の前提） |
| [Phase 2A RETROSPECTIVE.md](../phase2a/RETROSPECTIVE.md) | Phase 2A 振り返り（Phase 3 への申し送り事項） |
| [ADR.md](../../ADR.md) | アーキテクチャ決定記録 |
| [PHILOSOPHY.md](../../concept/PHILOSOPHY.md) | Ghost 理論（Memory の哲学的基盤） |
| [RULES.md](../../design/RULES.md) | デザインシステム指針 |

---

*Created: 2026-02-16*
*Phase 3 — Rebecca の「記憶」が永続化する。一時的な Markdown から構造化された書庫へ。*
