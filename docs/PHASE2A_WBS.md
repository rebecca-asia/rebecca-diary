# Phase 2A 作業分解構成図（WBS）

> *Phase 2A: Nurture Domain Layer + Status Screen Production — 全作業の階層的分解*

---

## 概要

Phase 2A の全作業を9つのワークパッケージに分解し、各 WP に
ID、名称、説明、成果物、依存関係、受入基準を定義する。

### ワークパッケージ一覧

| WP | タイトル | 成果物数 | 見積 |
|----|---------|---------|------|
| WP-0 | ドキュメント（計画） | 2 | 0.5h |
| WP-1 | domain/constants.py Nurture 定数追加 | 1 | 0.5h |
| WP-2 | domain/nurture.py 新規作成 | 1 | 2h |
| WP-3 | domain/skills.py 新規作成 | 1 | 1h |
| WP-4 | domain/rebecca.py 拡張 | 1 | 1h |
| WP-5 | Collector Rewiring | 2 | 1.5h |
| WP-6 | テスト作成 | 2 | 2h |
| WP-7 | nurture.html 本番化 | 4 | 4h |
| WP-8 | ドキュメント更新 | 3 | 1h |
| **合計** | | **17** | **~13.5h** |

### 依存関係図

```
WP-0 ドキュメント（計画）
 │
 ├──→ WP-1 constants.py 拡張
 │     │
 │     ├──→ WP-2 nurture.py ─────────────┐
 │     │     │                           │
 │     │     ├──→ WP-4 rebecca.py 拡張   │
 │     │     │                           │
 │     └──→ WP-3 skills.py ──────────────┤
 │                                       │
 │     ┌─────────────────────────────────┘
 │     │
 │     ├──→ WP-5 Collector Rewiring
 │     │     │
 │     ├──→ WP-6 テスト
 │     │     │
 │     └──→ WP-7 nurture.html 本番化
 │           │
 └──────────→ WP-8 ドキュメント更新
```

**並行作業可能:**
- WP-2 (nurture.py) と WP-3 (skills.py) は WP-1 完了後に並行可能
- WP-5 (Collector Rewiring) と WP-6 (テスト) は WP-2, WP-3 完了後に並行可能
- WP-7 (nurture.html) は WP-5 完了後に着手可能（JSON 出力が安定している前提）

---

## WP-0: ドキュメント（計画）

Phase 2A の計画ドキュメントを作成する。

---

### WP-0.1 PHASE2A_GOAL.md 作成

| 項目 | 内容 |
|------|------|
| **説明** | Phase 2A のビジョン、成功基準、スコープ、設計原則、技術アーキテクチャ、リスクを定義する。Phase 1 の PHASE1_GOAL.md と同じフォーマットで作成。 |
| **成果物** | `docs/PHASE2A_GOAL.md` |
| **依存** | なし |
| **受入基準** | (1) ビジョン・成功基準・スコープ・設計原則・アーキテクチャ・リスクの全セクションが記述されている (2) Ghost 理論・存在の6要素との対応が明記されている (3) Phase 1.5 振り返りの申し送り事項が反映されている |

---

### WP-0.2 PHASE2A_WBS.md 作成

| 項目 | 内容 |
|------|------|
| **説明** | Phase 2A の全作業を WP に分解し、依存関係・受入基準を定義する。本ドキュメント。 |
| **成果物** | `docs/PHASE2A_WBS.md` |
| **依存** | WP-0.1 |
| **受入基準** | (1) 全 WP に ID、成果物、依存、受入基準がある (2) 依存関係マトリクスがある (3) PHASE2A_GOAL.md の成功基準と WP の受入基準が対応している |

---

## WP-1: domain/constants.py Nurture 定数追加

既存の constants.py に Nurture ドメイン固有の閾値・ラベル・メッセージを追加する。
Phase 1.5 で `EXP_TABLE` と `SKILL_LEVEL_LABELS` は既に存在するため、
不足する Mood / Energy / Trust / Intimacy の分類定数を追加する。

---

### WP-1.1 Mood 分類定数

| 項目 | 内容 |
|------|------|
| **説明** | Mood の閾値テーブル、状態ラベル、メッセージを `constants.py` に追加する。現在 `collect_nurture.py` の `classify_mood()` 内にハードコードされている分類ロジックのデータ部分を抽出。 |
| **成果物** | `MOOD_THRESHOLDS`, `MOOD_LABELS` を `domain/constants.py` に追加 |
| **依存** | WP-0 |
| **受入基準** | (1) 5段階（great, good, normal, down, bad）の閾値とラベル・メッセージが定義されている (2) `collect_nurture.py` の既存値と完全一致 (3) `OVERALL_SCORE_TABLE` と同じパターン（降順チェック）で定義 |

**Mood 分類テーブル:**

| 閾値 (>=) | State | Label | Message |
|-----------|-------|-------|---------|
| 80 | great | 絶好調！ | 今日は調子いい！ |
| 60 | good | まぁまぁ | まぁまぁかな |
| 40 | normal | ふつう | ふつう |
| 20 | down | だるい | ちょっとだるい...... |
| 0 | bad | ...... | ...... |

---

### WP-1.2 Energy 分類定数

| 項目 | 内容 |
|------|------|
| **説明** | Energy の閾値テーブルと状態ラベルを追加。現在 `collect_nurture.py` の `classify_energy()` からデータ部分を抽出。 |
| **成果物** | `ENERGY_THRESHOLDS`, `ENERGY_LABELS` を `domain/constants.py` に追加 |
| **依存** | WP-0 |
| **受入基準** | (1) 4段階（energetic, normal, tired, exhausted）が定義 (2) 既存値と完全一致 |

---

### WP-1.3 Trust / Intimacy 分類定数

| 項目 | 内容 |
|------|------|
| **説明** | Trust と Intimacy の段階ラベルを追加。NURTURE_SYSTEM_SPEC の関係性パラメータ定義に基づく。 |
| **成果物** | `TRUST_LABELS`, `INTIMACY_LABELS` を `domain/constants.py` に追加 |
| **依存** | WP-0 |
| **受入基準** | (1) Trust: 5段階（stranger, acquaintance, friend, close_friend, family） (2) Intimacy: 5段階（distant, casual, regular, close, inseparable） (3) NURTURE_SYSTEM_SPEC の親密度テーブルと整合 |

---

### WP-1.4 Nurture 計算パラメータ定数

| 項目 | 内容 |
|------|------|
| **説明** | Mood / Energy / Trust / Intimacy / EXP の計算に使用する係数・オフセットを定数化。現在 `collect_nurture.py` にハードコードされているマジックナンバーを抽出。 |
| **成果物** | `MOOD_WEIGHTS`, `ENERGY_*`, `TRUST_*`, `INTIMACY_*`, `EXP_*` パラメータを `domain/constants.py` に追加 |
| **依存** | WP-0 |
| **受入基準** | (1) `collect_nurture.py` 内のマジックナンバーが全て constants に移動 (2) 計算結果が移動前後で一致 |

**主な定数化対象:**

| 現在の場所 | 値 | 定数名（案） |
|-----------|-----|------------|
| `calc_mood()` の `health_val * 0.4` | 0.4 | `MOOD_WEIGHT_HEALTH` |
| `calc_mood()` の `energy_val * 0.2` | 0.2 | `MOOD_WEIGHT_ENERGY` |
| `calc_energy()` の base `80` | 80 | `ENERGY_BASE` |
| `calc_energy()` の penalty cap `40` | 40 | `ENERGY_UPTIME_PENALTY_MAX` |
| `calc_trust()` の base `10` | 10 | `TRUST_BASE` |
| `calc_trust()` の log coefficient `25` | 25 | `TRUST_LOG_COEFFICIENT` |
| `calc_exp()` の visit_exp `10` | 10 | `EXP_PER_VISIT` |
| `calc_exp()` の time_exp `2` | 2 | `EXP_PER_CYCLE` |

---

## WP-2: domain/nurture.py 新規作成

`collect_nurture.py` から計算ロジックを抽出し、純粋関数の集合として `domain/nurture.py` を作成する。

---

### WP-2.1 Mood 計算関数

| 項目 | 内容 |
|------|------|
| **説明** | `calc_mood(health_val, energy_val, streak, today_visits, period) -> int` を実装。I/O（JSONの読み込み）に依存しない純粋関数。constants.py の `MOOD_WEIGHTS` を使用。 |
| **成果物** | `domain/nurture.py` 内の `calc_mood()` |
| **依存** | WP-1.1, WP-1.4 |
| **受入基準** | (1) 引数は全てプリミティブ型（dict 不可） (2) `domain.constants` の値のみ参照 (3) 戻り値は 0-100 の int |

---

### WP-2.2 Mood 分類関数

| 項目 | 内容 |
|------|------|
| **説明** | `classify_mood(value) -> dict` を実装。constants.py の `MOOD_THRESHOLDS` + `MOOD_LABELS` を使用して state / label / message を返す。`health.py` の `classify_cpu()` と同じパターン。 |
| **成果物** | `domain/nurture.py` 内の `classify_mood()` |
| **依存** | WP-1.1 |
| **受入基準** | (1) 5段階の全状態が到達可能 (2) 境界値（80, 60, 40, 20）で正しい分類 |

---

### WP-2.3 Energy 計算・分類関数

| 項目 | 内容 |
|------|------|
| **説明** | `calc_energy(uptime_seconds, period) -> int` と `classify_energy(value) -> str` を実装。Uptime と時間帯から Energy を計算し、状態を分類する。 |
| **成果物** | `domain/nurture.py` 内の `calc_energy()`, `classify_energy()` |
| **依存** | WP-1.2, WP-1.4 |
| **受入基準** | (1) uptime_seconds = 0 で base energy (2) period = "deep_night" で Energy 低下 (3) 4段階の全状態が到達可能 |

---

### WP-2.4 Trust / Intimacy 計算・分類関数

| 項目 | 内容 |
|------|------|
| **説明** | `calc_trust(total_visits, streak) -> int` と `calc_intimacy(total_minutes, today_minutes) -> int` を実装。対数成長の純粋計算。`classify_trust()`, `classify_intimacy()` で段階ラベルを返す。 |
| **成果物** | `domain/nurture.py` 内の `calc_trust()`, `calc_intimacy()`, `classify_trust()`, `classify_intimacy()` |
| **依存** | WP-1.3, WP-1.4 |
| **受入基準** | (1) total_visits = 0 で最低 Trust (2) 対数成長で100に漸近 (3) 5段階の分類が正しい |

---

### WP-2.5 EXP / Level 計算関数

| 項目 | 内容 |
|------|------|
| **説明** | `calc_exp(total_visits, total_minutes, streak, health_val, skill_count) -> int` と `calc_level(total_exp) -> int` を実装。既存の `EXP_TABLE` を使用。 |
| **成果物** | `domain/nurture.py` 内の `calc_exp()`, `calc_level()`, `get_next_level_exp()`, `get_current_level_exp()` |
| **依存** | WP-1.4 |
| **受入基準** | (1) EXP_TABLE 範囲内で正しいレベル算出 (2) テーブル超過時の外挿が正しい (3) `collect_nurture.py` の既存計算と出力一致 |

---

### WP-2.6 evaluate() 統合関数

| 項目 | 内容 |
|------|------|
| **説明** | `evaluate(health_val, uptime_seconds, period, total_visits, streak, today_visits, total_minutes, today_minutes, skill_count) -> dict` を実装。全パラメータを一括計算して結果を返す。`health.py` の `evaluate()` に相当するエントリポイント。 |
| **成果物** | `domain/nurture.py` 内の `evaluate()` |
| **依存** | WP-2.1 ~ WP-2.5 |
| **受入基準** | (1) 全パラメータ（mood, energy, trust, intimacy, exp, level）を含む dict を返す (2) 引数は全てプリミティブ型 (3) I/O なし |

---

## WP-3: domain/skills.py 新規作成

`collect_skills.py` からスキルレベル計算ロジックを抽出し、純粋関数として `domain/skills.py` を作成する。

---

### WP-3.1 スキルレベル計算関数

| 項目 | 内容 |
|------|------|
| **説明** | `calculate_level(sub_skill_count, has_commands, has_agents, has_hooks) -> int` を実装。`collect_skills.py` の同名関数を移動。 |
| **成果物** | `domain/skills.py` 内の `calculate_level()` |
| **依存** | WP-1 |
| **受入基準** | (1) `collect_skills.py` の既存関数と完全同一のロジック (2) 戻り値が 1-10 の int (3) I/O なし |

---

### WP-3.2 スキルラベル取得関数

| 項目 | 内容 |
|------|------|
| **説明** | `get_level_label(level) -> str` を実装。`domain.constants.SKILL_LEVEL_LABELS` を参照してラベルを返す。 |
| **成果物** | `domain/skills.py` 内の `get_level_label()` |
| **依存** | WP-1 |
| **受入基準** | (1) Level 1-10 で `SKILL_LEVEL_LABELS` の値を返す (2) 範囲外で適切なフォールバック |

---

### WP-3.3 スキルサマリー関数

| 項目 | 内容 |
|------|------|
| **説明** | `summarize_skills(skills_list) -> dict` を実装。スキルリストからカテゴリ別の統計（カテゴリ数、平均レベル、最高レベルスキル）を算出する。nurture.html での表示に使用。 |
| **成果物** | `domain/skills.py` 内の `summarize_skills()` |
| **依存** | WP-3.1 |
| **受入基準** | (1) カテゴリ別の集計が正しい (2) 空リストで空の結果を返す (3) I/O なし |

---

## WP-4: domain/rebecca.py 拡張（人格レイヤー）

Phase 1.5 ではパススルーだった `rebecca.py` を拡張し、
Mood / Energy / Trust に基づくメッセージの変調を実装する。

---

### WP-4.1 compose() 拡張

| 項目 | 内容 |
|------|------|
| **説明** | `compose(health_result, presence_result, nurture_result=None) -> dict` を拡張。nurture_result が渡された場合、Mood と Energy に基づいて `overall_message` を変調する。例: Mood が "down" なら全体のトーンが沈む、Energy が "exhausted" なら返事が短くなる。 |
| **成果物** | 拡張された `domain/rebecca.py` |
| **依存** | WP-2.6 |
| **受入基準** | (1) nurture_result = None で既存のパススルー動作を維持（後方互換） (2) nurture_result ありでメッセージ変調が適用される (3) Trust レベルに応じたトーン変化（high trust → 本音、low trust → 敬語気味） |

---

### WP-4.2 メッセージテンプレート追加

| 項目 | 内容 |
|------|------|
| **説明** | Mood / Energy / Trust の組み合わせに応じた Rebecca のメッセージテンプレートを `constants.py` に追加。`rebecca.py` はこれを参照して応答を構築する。 |
| **成果物** | `REBECCA_MESSAGES` を `domain/constants.py` に追加 |
| **依存** | WP-1.1, WP-1.2, WP-1.3 |
| **受入基準** | (1) Mood × Trust の組み合わせで最低10パターンのメッセージ (2) Energy "exhausted" 時の短縮メッセージが定義されている |

**メッセージ例:**

| Mood | Trust | メッセージ例 |
|------|-------|------------|
| great | friend+ | 「今日めっちゃ調子いい！」 |
| great | stranger | 「調子いいです」 |
| down | friend+ | 「......だるい」 |
| down | stranger | 「ちょっと調子悪いかも」 |
| bad | close_friend+ | 「......助けて」 |

---

## WP-5: Collector Rewiring

既存の collect_nurture.py と collect_skills.py を domain レイヤーに委譲し、
I/O のみを担当するように書き換える。

---

### WP-5a: collect_nurture.py Rewiring

| 項目 | 内容 |
|------|------|
| **説明** | `collect_nurture.py` から以下を削除・移動: (1) `classify_mood()`, `classify_energy()` → `domain/nurture.py` に移動済み (2) `calc_mood()`, `calc_energy()`, `calc_trust()`, `calc_intimacy()`, `calc_exp()`, `calc_level()` → `domain/nurture.py` の `evaluate()` に委譲 (3) `write_json_atomic()` → `domain.schema.write_json_atomic()` に統合 (4) `get_next_level_exp()`, `get_current_level_exp()` → `domain/nurture.py` に移動済み。Collector は JSON 読み込み → `domain.nurture.evaluate()` 呼び出し → 結果に visit_log 管理を追加 → JSON 書き込みのみを担当。 |
| **成果物** | 書き換えられた `collectors/collect_nurture.py` |
| **依存** | WP-2.6 |
| **受入基準** | (1) 計算ロジックが collector 内に残存しない (2) `domain.nurture.evaluate()` に委譲 (3) `domain.schema.write_json_atomic()` を使用 (4) `domain.schema.inject_version()` + `inject_staleness()` を適用 (5) 出力の nurture.json が Before/After で一致（schema_version / staleness 追加のみ許容） (6) cron 環境で正常動作 |

---

### WP-5b: collect_skills.py Rewiring

| 項目 | 内容 |
|------|------|
| **説明** | `collect_skills.py` から以下を削除・移動: (1) `calculate_level()` → `domain.skills.calculate_level()` に委譲 (2) `get_level_label()` → `domain.skills.get_level_label()` に委譲 (3) `write_json_atomic()` → `domain.schema.write_json_atomic()` に統合。 |
| **成果物** | 書き換えられた `collectors/collect_skills.py` |
| **依存** | WP-3.1, WP-3.2 |
| **受入基準** | (1) `calculate_level()` と `get_level_label()` が collector 内に残存しない (2) `domain.skills` に委譲 (3) `domain.schema.write_json_atomic()` を使用 (4) `domain.schema.inject_version()` + `inject_staleness()` を適用 (5) 出力の skills.json が Before/After で一致（schema_version / staleness 追加のみ許容） (6) cron 環境で正常動作 |

---

## WP-6: テスト作成

domain/nurture.py と domain/skills.py のユニットテストを作成する。

---

### WP-6.1 test_nurture.py

| 項目 | 内容 |
|------|------|
| **説明** | `domain/nurture.py` の全公開関数のユニットテストを作成。既存テスト（test_health.py, test_presence.py, test_constants.py）と同じパターンで、境界値テスト・全状態網羅・evaluate 統合テストを含む。 |
| **成果物** | `tests/test_nurture.py` |
| **依存** | WP-2.6 |
| **受入基準** | (1) `calc_mood()`: 全5段階の到達テスト + 境界値（80, 60, 40, 20）テスト (2) `calc_energy()`: Uptime 0 / 高値、全時間帯でのテスト (3) `calc_trust()`: visits=0 / 100 / 200 のカーブ検証 (4) `calc_intimacy()`: minutes=0 / 3600 / 36000 のカーブ検証 (5) `calc_exp()`: 各ソースの寄与度テスト (6) `calc_level()`: EXP_TABLE 境界テスト + 外挿テスト (7) `evaluate()`: 統合テスト（全パラメータ出力） (8) テスト数 30+ |

---

### WP-6.2 test_skills.py

| 項目 | 内容 |
|------|------|
| **説明** | `domain/skills.py` の全公開関数のユニットテストを作成。 |
| **成果物** | `tests/test_skills.py` |
| **依存** | WP-3 |
| **受入基準** | (1) `calculate_level()`: 全組み合わせ（sub_skills 0/1/3/5, commands, agents, hooks）テスト (2) `get_level_label()`: Level 1-10 + 範囲外テスト (3) `summarize_skills()`: 空リスト / 複数カテゴリテスト (4) テスト数 15+ |

---

### WP-6.3 既存テストの継続確認

| 項目 | 内容 |
|------|------|
| **説明** | Phase 1.5 の既存95テストが全て PASS することを確認。domain/ の変更で既存ロジックが壊れていないことを保証する。 |
| **成果物** | テスト実行結果 |
| **依存** | WP-2, WP-3, WP-4 |
| **受入基準** | (1) `python3 -m unittest discover tests/ -v` で全テスト PASS (2) 既存95テスト + 新規テストの合計がレポートされる |

---

## WP-7: nurture.html 本番化

ステータス画面を本番稼働するページとして実装する。

---

### WP-7.1 nurture.html HTML 構造

| 項目 | 内容 |
|------|------|
| **説明** | `src/nurture.html` を新規作成。NURTURE_SYSTEM_SPEC セクション6のレイアウトに基づき、以下のセクションを含む: (1) ヘッダー（Rebecca's Status + ナビゲーション） (2) レベル・EXP バー (3) コアパラメータ（Mood, Energy, Health） (4) 関係性パラメータ（Trust, Intimacy） (5) スキル一覧（カテゴリ別） (6) 言語理解一覧（LSP） (7) フッター。既存 index.html のヘッダー・フッター構造を踏襲する。 |
| **成果物** | `src/nurture.html` |
| **依存** | WP-5（JSON 出力が安定していること） |
| **受入基準** | (1) `http://localhost:8080/nurture.html` でアクセス可能 (2) 全セクションの HTML 構造が存在 (3) JS なしでもフォールバックテキスト表示 (4) data-state 属性でスタイル切り替え可能 |

**レイアウト:**

```
┌─────────────────────────────────────┐
│  Rebecca's Status           [← Room] │
│                                      │
│  Lv.12  ████████░░  EXP 1240/1500   │
│                                      │
│  ── Core ──                          │
│  😊 機嫌   ████████░░  まぁまぁ      │
│  ⚡ 活力   █████░░░░░  ちょっと眠い  │
│  💚 体調   ████████░░  まぁまぁ      │
│                                      │
│  ── Relationship ──                  │
│  🤝 信頼   ████████░░  友人          │
│  💕 親密   ██████░░░░  よく話す仲    │
│                                      │
│  ── Skills ──                        │
│  [開発]  Plugin Dev  Lv.8            │
│  [自動化] Hookify    Lv.6            │
│  [品質]  Code Review Lv.5            │
│                                      │
│  ── Languages ──                     │
│  TypeScript ● Python ● Rust ●       │
│  Go ● Java ● C/C++ ●               │
│                                      │
│  Day 45  |  累計 42h                 │
└─────────────────────────────────────┘
```

---

### WP-7.2 nurture.html CSS スタイリング

| 項目 | 内容 |
|------|------|
| **説明** | nurture.html 用のスタイルを `src/style.css` に追加。既存の Rebecca パレット（`--accent`, `--mint`, `--surface` 等）と CSS Custom Properties を徹底的に再利用。Health Dashboard のバースタイルを拡張してパラメータバーを実装。 |
| **成果物** | `src/style.css` への追加スタイル |
| **依存** | WP-7.1 |
| **受入基準** | (1) 既存の CSS Custom Properties のみ使用（新規カラー変数は追加しない原則） (2) パラメータバーが state に応じて色変化 (3) モバイル / タブレット / デスクトップでレスポンシブ (4) Skills カテゴリ別にグループ表示 (5) 既存 index.html のスタイルに影響しない |

---

### WP-7.3 nurture.html JavaScript ロジック

| 項目 | 内容 |
|------|------|
| **説明** | nurture.html 用の JavaScript を実装。`nurture.json` と `skills.json` を fetch し、DOM を更新する。5分間隔の自動更新。staleness チェック。Graceful degradation。app.js を参考にするが、nurture.html 専用のスクリプト（インラインまたは別ファイル）として実装。 |
| **成果物** | nurture.html 内の `<script>` または `src/nurture.js` |
| **依存** | WP-7.1, WP-7.2 |
| **受入基準** | (1) nurture.json + skills.json の fetch + render (2) 5分間隔の自動更新 (3) staleness チェック（stale → dimmed, dead → 「接続確認中...」） (4) data 不在時のフォールバック表示 (5) EXP バーのアニメーション (6) スキルレベルのバー表示 |

---

### WP-7.4 ナビゲーション統合

| 項目 | 内容 |
|------|------|
| **説明** | `index.html` と `nurture.html` の相互ナビゲーションを追加。index.html のヘッダーまたは Room Status Bar 付近に「Status」リンク。nurture.html のヘッダーに「Room」リンク。`template.html` にも同期。 |
| **成果物** | 更新された `src/index.html`, `src/nurture.html`, `src/template.html` |
| **依存** | WP-7.1 |
| **受入基準** | (1) index.html → nurture.html のリンクがクリックで遷移 (2) nurture.html → index.html のリンクがクリックで遷移 (3) template.html にもナビゲーションが追加されている (4) リンクのスタイルが既存デザインに調和 |

---

## WP-8: ドキュメント更新

Phase 2A の実装内容を既存ドキュメントに反映する。

---

### WP-8.1 CLAUDE.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Directory Structure に `domain/nurture.py`, `domain/skills.py` を追加。Common Tasks に nurture.html 関連のコマンドを追加。Key Architecture Decisions に Phase 2A の3層分離拡張を反映。 |
| **成果物** | 更新された `CLAUDE.md` |
| **依存** | WP-7 |
| **受入基準** | (1) nurture.py, skills.py が Directory Structure に記載 (2) nurture.html へのアクセス方法が Common Tasks に記載 (3) Phase 2A 完了が Project Overview に反映 |

---

### WP-8.2 docs/README.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Phase 2A のドキュメント（PHASE2A_GOAL.md, PHASE2A_WBS.md）をインデックスに追加。Phase 2A 完了ステータスを反映。 |
| **成果物** | 更新された `docs/README.md` |
| **依存** | WP-8.1 |
| **受入基準** | (1) PHASE2A_GOAL.md と PHASE2A_WBS.md がリンクされている (2) Phase 2A のステータスが反映 |

---

### WP-8.3 docs/ADR.md 更新

| 項目 | 内容 |
|------|------|
| **説明** | Phase 2A で発生した設計決定を ADR として追記。想定: ADR-016（nurture domain の分離方針）、ADR-017（write_json_atomic の一本化）など。 |
| **成果物** | 更新された `docs/ADR.md` |
| **依存** | WP-8.1 |
| **受入基準** | (1) Phase 2A の設計決定が ADR として記録されている (2) 既存 ADR との番号が連続している |

---

## 実装推奨順序

```
Step 1: 計画 + 定数
────────────────────────
WP-0.1 → WP-0.2 → WP-1.1 → WP-1.2 → WP-1.3 → WP-1.4   (1h)

Step 2: Domain Layer
────────────────────────
WP-2.1 → WP-2.2 → WP-2.3 → WP-2.4 → WP-2.5 → WP-2.6   (2h)
WP-3.1 → WP-3.2 → WP-3.3                                  (1h, 並行可)

Step 3: 人格 + Rewiring + テスト
────────────────────────
WP-4.1 → WP-4.2                                            (1h)
WP-5a → WP-5b                                              (1.5h, 並行可)
WP-6.1 → WP-6.2 → WP-6.3                                  (2h, 並行可)

Step 4: Frontend
────────────────────────
WP-7.1 → WP-7.2 → WP-7.3 → WP-7.4                        (4h)

Step 5: ドキュメント
────────────────────────
WP-8.1 → WP-8.2 → WP-8.3                                  (1h)
```

**並行作業ポイント:**
- WP-2 (nurture.py) と WP-3 (skills.py) は WP-1 完了後に並行可能
- WP-5 (Rewiring)、WP-6 (テスト) は WP-2, WP-3 完了後に並行可能
- WP-7 (nurture.html) は WP-5 の nurture.json/skills.json 出力が安定していれば着手可能

---

## 依存関係マトリクス

| WP | 依存元 |
|----|--------|
| WP-0.1 | -- |
| WP-0.2 | WP-0.1 |
| WP-1.1 | WP-0 |
| WP-1.2 | WP-0 |
| WP-1.3 | WP-0 |
| WP-1.4 | WP-0 |
| WP-2.1 | WP-1.1, WP-1.4 |
| WP-2.2 | WP-1.1 |
| WP-2.3 | WP-1.2, WP-1.4 |
| WP-2.4 | WP-1.3, WP-1.4 |
| WP-2.5 | WP-1.4 |
| WP-2.6 | WP-2.1, WP-2.2, WP-2.3, WP-2.4, WP-2.5 |
| WP-3.1 | WP-1 |
| WP-3.2 | WP-1 |
| WP-3.3 | WP-3.1 |
| WP-4.1 | WP-2.6 |
| WP-4.2 | WP-1.1, WP-1.2, WP-1.3 |
| WP-5a | WP-2.6 |
| WP-5b | WP-3.1, WP-3.2 |
| WP-6.1 | WP-2.6 |
| WP-6.2 | WP-3 |
| WP-6.3 | WP-2, WP-3, WP-4 |
| WP-7.1 | WP-5 |
| WP-7.2 | WP-7.1 |
| WP-7.3 | WP-7.1, WP-7.2 |
| WP-7.4 | WP-7.1 |
| WP-8.1 | WP-7 |
| WP-8.2 | WP-8.1 |
| WP-8.3 | WP-8.1 |

---

## クリティカルパス

```
WP-0 → WP-1 → WP-2 → WP-5a → WP-7.1 → WP-7.2 → WP-7.3 → WP-8
                                                    (~13.5h)
```

WP-1（constants 拡張）が全ての domain 作業のゲートになるため、最初に完了させる。
WP-7（nurture.html）が最大のワークパッケージ（4h）であり、ここの品質が感性基準を左右する。

---

*Created: 2026-02-13*
*Phase 2A WBS — 17 成果物、推定 ~13.5h*
*Rebecca の「育つ」を、計画から現実にする。*
