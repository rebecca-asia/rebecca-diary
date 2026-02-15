# Phase 3 作業分解構成図（WBS）

> *Phase 3: SQLite Diary Database — 全作業の階層的分解*

---

## 概要

Phase 3 の全作業を6つのワークパッケージに分解し、各 WP に
ID、名称、説明、成果物、依存関係、受入基準を定義する。

### ワークパッケージ一覧

| WP | タイトル | 成果物数 | 見積 |
|----|---------|---------|------|
| WP-0 | Phase 3 ドキュメント | 2 | 0.5h |
| WP-1 | domain/diary.py 新規作成 | 1 | 3h |
| WP-2 | tests/test_diary.py 新規作成 | 1 | 2.5h |
| WP-3 | scripts/update_diary.py 修正 | 1 | 3h |
| WP-4 | .gitignore + CLAUDE.md 更新 | 2 | 0.5h |
| WP-5 | 検証 + 初回DB構築 | 1 | 1h |
| **合計** | | **8** | **~10.5h** |

### 依存関係図

```
WP-0 ドキュメント（計画）
 │
 └──→ WP-1 domain/diary.py
       │
       ├──→ WP-2 tests/test_diary.py
       │
       └──→ WP-3 update_diary.py 修正
             │
             └──→ WP-4 .gitignore + CLAUDE.md 更新
                   │
                   └──→ WP-5 検証 + 初回DB構築
```

**並行作業可能:**
- WP-2 (tests) と WP-3 (update_diary.py 修正) は WP-1 完了後に並行可能
- WP-5 (検証) は WP-2, WP-3, WP-4 全完了後に着手

---

## WP-0: Phase 3 ドキュメント

Phase 3 の計画ドキュメントを作成する。

---

### WP-0.1 GOAL.md 作成

| 項目 | 内容 |
|------|------|
| **説明** | Phase 3 のビジョン、成功基準、スコープ、設計原則、技術アーキテクチャ、リスクを定義する。Phase 2A の phases/phase2a/GOAL.md と同じフォーマットで作成。 |
| **成果物** | `docs/phases/phase3/GOAL.md` |
| **依存** | なし |
| **受入基準** | (1) ビジョン・成功基準・スコープ・設計原則・アーキテクチャ・リスクの全セクションが記述されている (2) SQLite 導入の技術的根拠が明記されている (3) Phase 2A からの申し送り事項が反映されている |

---

### WP-0.2 WBS.md 作成

| 項目 | 内容 |
|------|------|
| **説明** | Phase 3 の全作業を WP に分解し、依存関係・受入基準を定義する。本ドキュメント。 |
| **成果物** | `docs/phases/phase3/WBS.md` |
| **依存** | WP-0.1 |
| **受入基準** | (1) 全 WP に ID、成果物、依存、受入基準がある (2) 依存関係マトリクスがある (3) GOAL.md の成功基準と WP の受入基準が対応している |

---

## WP-1: domain/diary.py 新規作成

SQLite データベースのスキーマ定義とリポジトリ関数を `domain/diary.py` に実装する。
日記エントリの CRUD、翻訳キャッシュ、Recap キャッシュ、スキーマバージョン管理を提供する。

---

### WP-1.1 DB初期化

| 項目 | 内容 |
|------|------|
| **説明** | `init_db(path) -> Connection` を実装。SQLite データベースを初期化し、必要なテーブルを作成する。WAL モードを有効化し、`schema_meta` テーブルにスキーマバージョンを記録する。 |
| **成果物** | `domain/diary.py` 内の `init_db()` |
| **依存** | WP-0 |
| **受入基準** | (1) 指定パスに SQLite DB ファイルが作成される (2) WAL モードが有効 (3) `schema_meta` テーブルにバージョンが記録される (4) 既存 DB に対しては再作成せずに接続を返す (5) テーブル定義: entries, translation_cache, recap_cache, schema_meta |

**テーブル定義（想定）:**

| テーブル | 主要カラム |
|---------|-----------|
| `entries` | date (PK), source, markdown, html, title, created_at, updated_at |
| `translation_cache` | date (PK), content_hash, translated_html, created_at |
| `recap_cache` | date (PK), recap_text, created_at |
| `schema_meta` | key (PK), value |

---

### WP-1.2 エントリCRUD

| 項目 | 内容 |
|------|------|
| **説明** | `upsert_entry(conn, date, source, markdown, html, title)`, `get_entry(conn, date) -> dict`, `get_all_entries(conn) -> list[dict]`, `delete_entry(conn, date)` を実装。日記エントリの基本操作を提供する。 |
| **成果物** | `domain/diary.py` 内の `upsert_entry()`, `get_entry()`, `get_all_entries()`, `delete_entry()` |
| **依存** | WP-1.1 |
| **受入基準** | (1) upsert は INSERT OR REPLACE で同一日付の重複を防止 (2) get_entry は存在しない日付で None を返す (3) get_all_entries は日付降順で返す (4) delete_entry は存在しない日付で例外を投げない (5) 全関数が Connection オブジェクトを引数に取る（I/O は呼び出し側に委譲） |

---

### WP-1.3 翻訳キャッシュ

| 項目 | 内容 |
|------|------|
| **説明** | `get_translation_cache(conn, date, content_hash) -> str|None`, `set_translation_cache(conn, date, content_hash, translated_html)` を実装。日付と content_hash の組み合わせでキャッシュを管理する。hash が一致しない場合はキャッシュミスとして None を返す。 |
| **成果物** | `domain/diary.py` 内の `get_translation_cache()`, `set_translation_cache()` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 日付 + content_hash が一致する場合のみキャッシュヒット (2) hash 不一致で None を返す（古いキャッシュを返さない） (3) set は既存エントリを上書き (4) `.translation-cache/` ディレクトリの JSON と同等の機能を提供 |

---

### WP-1.4 Recapキャッシュ

| 項目 | 内容 |
|------|------|
| **説明** | `get_recap_cache(conn, date) -> str|None`, `set_recap_cache(conn, date, recap_text)` を実装。日付をキーとして Recap テキストをキャッシュする。 |
| **成果物** | `domain/diary.py` 内の `get_recap_cache()`, `set_recap_cache()` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 日付で Recap テキストを取得・保存できる (2) 存在しない日付で None を返す (3) set は既存エントリを上書き (4) `.recap-cache/` ディレクトリのファイルと同等の機能を提供 |

---

### WP-1.5 キャッシュ移行

| 項目 | 内容 |
|------|------|
| **説明** | `migrate_file_caches(conn, translation_cache_dir, recap_cache_dir)` を実装。既存のファイルベースキャッシュ（`.translation-cache/` と `.recap-cache/`）を SQLite DB に移行する。移行済みエントリはスキップし、冪等性を保証する。 |
| **成果物** | `domain/diary.py` 内の `migrate_file_caches()` |
| **依存** | WP-1.3, WP-1.4 |
| **受入基準** | (1) `.translation-cache/` 内の JSON ファイルを読み取り translation_cache テーブルに挿入 (2) `.recap-cache/` 内のファイルを読み取り recap_cache テーブルに挿入 (3) 既に DB に存在するエントリはスキップ（冪等） (4) 空ディレクトリ・存在しないディレクトリでエラーを出さない (5) 移行件数をログ出力 |

---

### WP-1.6 スキーマバージョン管理

| 項目 | 内容 |
|------|------|
| **説明** | `get_schema_version(conn) -> int`, `set_schema_version(conn, version)` を実装。`schema_meta` テーブルを使用してスキーマバージョンを管理する。将来のマイグレーションに備える。 |
| **成果物** | `domain/diary.py` 内の `get_schema_version()`, `set_schema_version()` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 初期スキーマバージョンは 1 (2) バージョンの取得・設定が正しく動作する (3) schema_meta テーブルが存在しない場合はバージョン 0 を返す（初回マイグレーション検出用） |

---

## WP-2: tests/test_diary.py 新規作成

`domain/diary.py` の全公開関数のユニットテストを作成する。
テスト数目標: ~45件。

---

### WP-2.1 DB初期化テスト

| 項目 | 内容 |
|------|------|
| **説明** | `init_db()` のテストを作成。テーブルの存在確認、WAL モードの検証、スキーマバージョンの初期値確認を含む。`:memory:` と一時ファイルの両方でテストする。 |
| **成果物** | `tests/test_diary.py` 内の DB 初期化テスト群 |
| **依存** | WP-1.1 |
| **受入基準** | (1) entries, translation_cache, recap_cache, schema_meta テーブルの存在を検証 (2) WAL モードが有効であることを検証 (3) スキーマバージョン初期値 = 1 を検証 (4) 2回呼び出しで冪等であることを検証 |

---

### WP-2.2 エントリCRUDテスト

| 項目 | 内容 |
|------|------|
| **説明** | `upsert_entry()`, `get_entry()`, `get_all_entries()`, `delete_entry()` のテストを作成。正常系・異常系・境界値を網羅する。 |
| **成果物** | `tests/test_diary.py` 内のエントリ CRUD テスト群 |
| **依存** | WP-1.2 |
| **受入基準** | (1) upsert: 新規挿入、既存更新（上書き）、同一日付の重複防止 (2) get_entry: 存在する日付、存在しない日付 (3) get_all_entries: 空 DB、複数エントリ、日付降順 (4) delete_entry: 存在する日付、存在しない日付（エラーなし） |

---

### WP-2.3 翻訳キャッシュテスト

| 項目 | 内容 |
|------|------|
| **説明** | `get_translation_cache()`, `set_translation_cache()` のテストを作成。キャッシュヒット・ミス・上書きの全パターンを検証する。 |
| **成果物** | `tests/test_diary.py` 内の翻訳キャッシュテスト群 |
| **依存** | WP-1.3 |
| **受入基準** | (1) set → get でキャッシュヒット (2) hash 不一致でキャッシュミス（None） (3) 同一日付で set を2回呼ぶと上書き (4) 存在しない日付で None |

---

### WP-2.4 Recapキャッシュテスト

| 項目 | 内容 |
|------|------|
| **説明** | `get_recap_cache()`, `set_recap_cache()` のテストを作成。取得・保存・上書きの全パターンを検証する。 |
| **成果物** | `tests/test_diary.py` 内の Recap キャッシュテスト群 |
| **依存** | WP-1.4 |
| **受入基準** | (1) set → get で取得成功 (2) 同一日付で set を2回呼ぶと上書き (3) 存在しない日付で None |

---

### WP-2.5 キャッシュ移行テスト

| 項目 | 内容 |
|------|------|
| **説明** | `migrate_file_caches()` のテストを作成。テスト用の一時ディレクトリにキャッシュファイルを配置し、DB への移行を検証する。 |
| **成果物** | `tests/test_diary.py` 内のキャッシュ移行テスト群 |
| **依存** | WP-1.5 |
| **受入基準** | (1) `.translation-cache/` からの移行成功 (2) `.recap-cache/` からの移行成功 (3) 既存エントリのスキップ（冪等性） (4) 空ディレクトリで正常完了 (5) 存在しないディレクトリで正常完了（エラーなし） |

---

### WP-2.6 エッジケーステスト

| 項目 | 内容 |
|------|------|
| **説明** | 空 DB、Unicode コンテンツ、大容量コンテンツ、同時アクセスなどのエッジケースをテストする。 |
| **成果物** | `tests/test_diary.py` 内のエッジケーステスト群 |
| **依存** | WP-1.2, WP-1.3, WP-1.4 |
| **受入基準** | (1) 空 DB で get_all_entries が空リストを返す (2) Unicode（日本語、絵文字）を含むコンテンツの正常保存・取得 (3) 大容量 Markdown（10KB+）の正常保存・取得 (4) 同一 Connection での複数操作が安全 |

---

## WP-3: scripts/update_diary.py 修正

既存の `update_diary.py` に SQLite DB 統合を追加する。
ファイルベースのキャッシュを DB に置換し、差分更新と全件リビルドをサポートする。

---

### WP-3.1 DB初期化統合

| 項目 | 内容 |
|------|------|
| **説明** | `update_diary.py` の起動時に `domain.diary.init_db()` を呼び出し、DB 接続を確立する。DB パスはプロジェクトルートの `diary.db` をデフォルトとし、環境変数 or コマンドライン引数で上書き可能とする。 |
| **成果物** | `scripts/update_diary.py` 内の DB 初期化処理 |
| **依存** | WP-1.1 |
| **受入基準** | (1) 起動時に diary.db が存在しなければ自動作成 (2) 既存 diary.db があれば接続のみ (3) DB パスの指定方法が --db-path オプションで提供される |

---

### WP-3.2 build_entry → DB保存フロー

| 項目 | 内容 |
|------|------|
| **説明** | Markdown の読み込み → HTML 変換後、結果を `domain.diary.upsert_entry()` で DB に保存するフローを実装。既存の diary.html 直接挿入ロジックを DB 経由に変更する。 |
| **成果物** | `scripts/update_diary.py` 内の DB 保存フロー |
| **依存** | WP-1.2, WP-3.1 |
| **受入基準** | (1) Markdown → HTML → DB 保存のパイプラインが動作する (2) 同一日付のエントリは upsert（上書き更新） (3) source（openclaw / obsidian）が記録される |

---

### WP-3.3 DB全件読出し → HTML生成フロー

| 項目 | 内容 |
|------|------|
| **説明** | DB から全エントリを読み出し、diary.html を生成するフローを実装する。`get_all_entries()` で日付降順の全エントリを取得し、template.html に流し込んで diary.html を出力する。 |
| **成果物** | `scripts/update_diary.py` 内の HTML 生成フロー |
| **依存** | WP-1.2, WP-3.1 |
| **受入基準** | (1) DB の全エントリが diary.html に反映される (2) 日付降順（新しい順）で出力 (3) 既存の diary.html と同等のフォーマットを維持 (4) エントリ 0 件でも正常な HTML を出力 |

---

### WP-3.4 --rebuild オプション

| 項目 | 内容 |
|------|------|
| **説明** | `--rebuild` コマンドラインオプションを追加。指定時、全 Markdown ソースを再スキャンし、DB を再構築した上で diary.html を再生成する。初回 DB 構築や DB 破損からの復旧に使用する。 |
| **成果物** | `scripts/update_diary.py` 内の `--rebuild` オプション |
| **依存** | WP-3.2, WP-3.3 |
| **受入基準** | (1) `python3 scripts/update_diary.py --rebuild` で全ソースから DB を再構築 (2) 既存 DB があっても全エントリを upsert（差分ではなく全件） (3) 再構築後に diary.html を再生成 (4) --dry-run との併用が可能 |

---

### WP-3.5 --migrate-cache オプション

| 項目 | 内容 |
|------|------|
| **説明** | `--migrate-cache` コマンドラインオプションを追加。指定時、`domain.diary.migrate_file_caches()` を呼び出し、既存のファイルベースキャッシュ（`.translation-cache/`, `.recap-cache/`）を DB に移行する。 |
| **成果物** | `scripts/update_diary.py` 内の `--migrate-cache` オプション |
| **依存** | WP-1.5, WP-3.1 |
| **受入基準** | (1) `python3 scripts/update_diary.py --migrate-cache` でキャッシュ移行が実行される (2) 移行件数がログに出力される (3) 冪等（2回実行しても問題なし） (4) --verbose で詳細ログ出力 |

---

### WP-3.6 翻訳/Recapキャッシュ → DB移行

| 項目 | 内容 |
|------|------|
| **説明** | `update_diary.py` 内の翻訳キャッシュ・Recap キャッシュの読み書きを、ファイルベースから DB ベースに切り替える。`domain.diary.get_translation_cache()` / `set_translation_cache()` / `get_recap_cache()` / `set_recap_cache()` を使用する。 |
| **成果物** | `scripts/update_diary.py` 内のキャッシュ処理の DB 化 |
| **依存** | WP-1.3, WP-1.4, WP-3.1 |
| **受入基準** | (1) 翻訳キャッシュの読み書きが DB 経由 (2) Recap キャッシュの読み書きが DB 経由 (3) ファイルベースキャッシュへの依存が除去される (4) キャッシュヒット率が移行前と同等 |

---

## WP-4: .gitignore + CLAUDE.md 更新

Phase 3 の実装内容を既存ドキュメント・設定ファイルに反映する。

---

### WP-4.1 .gitignore に diary.db 追加

| 項目 | 内容 |
|------|------|
| **説明** | `.gitignore` に `diary.db` および `diary.db-wal`, `diary.db-shm`（WAL モード関連ファイル）を追加する。DB ファイルがリポジトリにコミットされないようにする。 |
| **成果物** | 更新された `.gitignore` |
| **依存** | WP-3 |
| **受入基準** | (1) `diary.db` が gitignore に記載 (2) `diary.db-wal`, `diary.db-shm` も gitignore に記載 (3) 既存の gitignore ルールに影響しない |

---

### WP-4.2 CLAUDE.md に Phase 3 情報反映

| 項目 | 内容 |
|------|------|
| **説明** | CLAUDE.md の Project Overview に Phase 3 完了を反映。Directory Structure に `domain/diary.py` を追加。Common Tasks に `--rebuild`, `--migrate-cache` コマンドを追加。Protected Files に `diary.db` の取り扱いを追記。 |
| **成果物** | 更新された `CLAUDE.md` |
| **依存** | WP-4.1 |
| **受入基準** | (1) `domain/diary.py` が Directory Structure に記載 (2) `--rebuild`, `--migrate-cache` が Common Tasks に記載 (3) Phase 3 完了が Project Overview に反映 (4) `diary.db` の取り扱い方針が記載 |

---

## WP-5: 検証 + 初回DB構築

全 WP の成果物を統合し、エンドツーエンドの検証を行う。

---

### WP-5.1 全テスト実行

| 項目 | 内容 |
|------|------|
| **説明** | `python3 -m unittest discover tests/ -v` で全テストを実行し、全 PASS を確認する。Phase 2A までの既存テストが壊れていないことも保証する。 |
| **成果物** | テスト実行結果 |
| **依存** | WP-2, WP-3 |
| **受入基準** | (1) 全テスト PASS (2) 既存テスト + test_diary.py (~45件) の合計がレポートされる (3) テスト実行時間が妥当（10秒以内） |

---

### WP-5.2 --migrate-cache 実行

| 項目 | 内容 |
|------|------|
| **説明** | 本番環境で `python3 scripts/update_diary.py --migrate-cache` を実行し、既存のファイルベースキャッシュを DB に移行する。移行結果をログで確認する。 |
| **成果物** | 移行完了の diary.db（翻訳キャッシュ + Recap キャッシュ投入済み） |
| **依存** | WP-5.1 |
| **受入基準** | (1) `.translation-cache/` の全エントリが DB に移行 (2) `.recap-cache/` の全エントリが DB に移行 (3) エラーなしで完了 (4) 移行件数がログに出力 |

---

### WP-5.3 --rebuild 実行

| 項目 | 内容 |
|------|------|
| **説明** | 本番環境で `python3 scripts/update_diary.py --rebuild` を実行し、全 Markdown ソースから DB を構築し、diary.html を再生成する。 |
| **成果物** | 完成した diary.db + 再生成された diary.html |
| **依存** | WP-5.2 |
| **受入基準** | (1) 全 Markdown ソース（OpenClaw memory + Obsidian vault）が DB に投入 (2) diary.html が正常に再生成 (3) 既存の diary.html と内容が同等（レイアウト崩れなし） |

---

### WP-5.4 diary.html 出力確認

| 項目 | 内容 |
|------|------|
| **説明** | `cd src && python3 -m http.server 8080` でローカルサーバーを起動し、diary.html の表示を目視確認する。全エントリの表示、レイアウト、リンクの動作を検証する。 |
| **成果物** | 確認結果 |
| **依存** | WP-5.3 |
| **受入基準** | (1) `http://localhost:8080/diary.html` で全エントリが表示される (2) 日付降順で正しくソートされている (3) カードグリッド → エントリ詳細の遷移が正常 (4) レスポンシブ表示が崩れていない (5) 既存の index.html からの遷移が正常 |

---

## 実装推奨順序

```
Step 1: 計画
────────────────────────
WP-0.1 → WP-0.2                                              (0.5h)

Step 2: Domain Layer
────────────────────────
WP-1.1 → WP-1.2 → WP-1.3 → WP-1.4 → WP-1.5 → WP-1.6       (3h)

Step 3: テスト + update_diary.py 修正
────────────────────────
WP-2.1 → WP-2.2 → WP-2.3 → WP-2.4 → WP-2.5 → WP-2.6       (2.5h, 並行可)
WP-3.1 → WP-3.2 → WP-3.3 → WP-3.4 → WP-3.5 → WP-3.6       (3h, 並行可)

Step 4: ドキュメント更新
────────────────────────
WP-4.1 → WP-4.2                                              (0.5h)

Step 5: 検証
────────────────────────
WP-5.1 → WP-5.2 → WP-5.3 → WP-5.4                          (1h)
```

**並行作業ポイント:**
- WP-2 (tests) と WP-3 (update_diary.py 修正) は WP-1 完了後に並行可能
- WP-4 は WP-3 完了後に着手（update_diary.py の最終仕様が確定してから）
- WP-5 は全 WP 完了後に着手（統合検証のため）

---

## 依存関係マトリクス

| WP | 依存元 |
|----|--------|
| WP-0.1 | -- |
| WP-0.2 | WP-0.1 |
| WP-1.1 | WP-0 |
| WP-1.2 | WP-1.1 |
| WP-1.3 | WP-1.1 |
| WP-1.4 | WP-1.1 |
| WP-1.5 | WP-1.3, WP-1.4 |
| WP-1.6 | WP-1.1 |
| WP-2.1 | WP-1.1 |
| WP-2.2 | WP-1.2 |
| WP-2.3 | WP-1.3 |
| WP-2.4 | WP-1.4 |
| WP-2.5 | WP-1.5 |
| WP-2.6 | WP-1.2, WP-1.3, WP-1.4 |
| WP-3.1 | WP-1.1 |
| WP-3.2 | WP-1.2, WP-3.1 |
| WP-3.3 | WP-1.2, WP-3.1 |
| WP-3.4 | WP-3.2, WP-3.3 |
| WP-3.5 | WP-1.5, WP-3.1 |
| WP-3.6 | WP-1.3, WP-1.4, WP-3.1 |
| WP-4.1 | WP-3 |
| WP-4.2 | WP-4.1 |
| WP-5.1 | WP-2, WP-3 |
| WP-5.2 | WP-5.1 |
| WP-5.3 | WP-5.2 |
| WP-5.4 | WP-5.3 |

---

## クリティカルパス

```
WP-0 → WP-1.1 → WP-1.2 → WP-3.1 → WP-3.2 → WP-3.3 → WP-3.4 → WP-4 → WP-5
                                                                    (~10.5h)
```

WP-1（domain/diary.py）が全ての domain 作業のゲートになるため、最初に完了させる。
WP-3（update_diary.py 修正）が最大のワークパッケージ（3h）であり、既存スクリプトとの後方互換を保ちながらの DB 統合が最もリスクの高い作業となる。

---

*Created: 2026-02-16*
*Phase 3 WBS — 8 成果物、推定 ~10.5h*
*Rebecca の記憶を、ファイルからデータベースへ。*
