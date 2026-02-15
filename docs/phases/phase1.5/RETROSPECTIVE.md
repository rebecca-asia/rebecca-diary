# Phase 1.5 振り返り — ドメインレイヤー確立

> *「背骨」は通った。次は「心臓」を動かす番。*

---

## 0. サマリー

| 項目 | 内容 |
|------|------|
| 期間 | 2026-02-13（1セッション） |
| 目的 | ドメインロジックの集約・テスト可能化・Phase 2 受け皿 |
| 結果 | **全12ステップ完了** |
| テスト | 95件 ALL PASS |
| 本番影響 | cron 稼働中に無停止移行完了 |

---

## 1. 何をやったか

### 1.1 Before / After

```
Before (Phase 1):
┌─ collectors/*.py ──────────────────┐
│  計測 + 分類 + スコア + アラート    │  ← ドメイン混入
└────────────────────────────────────┘
┌─ app.js ───────────────────────────┐
│  表示 + staleness判定 + メッセージ  │  ← ドメイン漏れ
└────────────────────────────────────┘

After (Phase 1.5):
┌─ domain/ ──────────────────────────┐
│  constants  全閾値・ラベル・メッセージ│
│  health     分類・スコア・アラート    │
│  presence   在室判定・時間帯         │
│  schema     バージョン・鮮度・書込み  │
│  rebecca    Phase 2 スタブ          │
└────────────────────────────────────┘
         ↑ import           ↑ JSON フィールド参照
┌─ collectors/ ──┐  ┌─ app.js ──────────┐
│  計測 → 委譲    │  │  fetch → 表示のみ  │
└────────────────┘  └──────────────────┘
```

### 1.2 成果物一覧

**新規作成（10ファイル）:**

| ファイル | 行数 | 役割 |
|----------|------|------|
| `domain/__init__.py` | 3 | パッケージ + `__version__ = "1.0"` |
| `domain/constants.py` | 207 | 全閾値・ラベル・メッセージの **Single Source of Truth** |
| `domain/health.py` | 147 | ヘルス分類・スコア計算・アラート判定（純粋関数） |
| `domain/presence.py` | 90 | 在室状況・時間帯コンテキスト（純粋関数） |
| `domain/rebecca.py` | 20 | パーソナリティ層（Phase 2 スタブ） |
| `domain/schema.py` | 80 | バージョニング・staleness・バリデーション・原子書込み |
| `tests/test_health.py` | 195 | 境界値テスト・全状態網羅・evaluate 統合テスト |
| `tests/test_presence.py` | 107 | 全24時間・状態遷移・evaluate 統合テスト |
| `tests/test_constants.py` | 125 | 閾値昇順・ラベル網羅・24h カバー・EXP 昇順 |
| `tests/__init__.py` | 0 | テストパッケージ |

**修正（8ファイル）:**

| ファイル | 削除行 | 変更内容 |
|----------|--------|----------|
| `collectors/collect_health.py` | ~178行 | 6分類関数 + overall + alert を削除、`domain_health.evaluate()` に委譲 |
| `collectors/collect_status.py` | ~73行 | `TIME_MESSAGES` + `get_time_context()` + `determine_status()` + 閾値定数を削除 |
| `collectors/collect_nurture.py` | ~22行 | `EXP_TABLE` を `domain.constants` から参照 |
| `collectors/collect_skills.py` | ~12行 | `LEVEL_LABELS` を `domain.constants` から参照 |
| `src/app.js` | ~15行 | `checkStaleness()` + `alertMessages` を削除 |
| `CLAUDE.md` | — | Directory Structure, Architecture Decisions, Common Tasks 更新 |
| `docs/README.md` | — | Phase 1.5 エントリ + Directory Structure 追加 |
| `docs/ADR.md` | — | ADR-015 追加 |

### 1.3 JSON スキーマ変更

**health.json — 追加のみ（後方互換）:**
```json
{
  "schema_version": "1.0",
  "staleness": "fresh",
  "alert_message": "ちょっと重いかも..."
}
```

**status.json — 追加のみ（後方互換）:**
```json
{
  "schema_version": "1.0",
  "staleness": "fresh"
}
```

既存フィールドは全て同一値を出力。app.js は `data.staleness || 'stale'` で旧 JSON にもフォールバック。

---

## 2. 検証結果

### 2.1 ユニットテスト

```
$ python3 -m unittest discover tests/ -v
Ran 95 tests in 0.001s
OK
```

| テストファイル | テスト数 | カバー範囲 |
|---------------|----------|-----------|
| test_constants.py | 24 | 閾値昇順、ラベル網羅、24h カバー、EXP 昇順 |
| test_health.py | 40 | 境界値（19.99/20.0）、全5状態、overall、alert 0-3、evaluate |
| test_presence.py | 31 | online/away/sleeping/offline、deep_night 限定、全24時間 |

### 2.2 Collector 出力検証

**health.json diff（ライブメトリクスによる差異のみ）:**
- CPU usage: 17.9% → 14.4%（計測タイミング差）
- Memory: 64.9% → 63.6%（同上）
- Uptime: +336s（経過時間差）
- **分類状態・ラベル・メッセージ: 全一致**

**status.json diff:**
- time_context.message: ランダム選択のため変動
- **period, status, label, emoji: 全一致**

### 2.3 cron 連続運行

全 collector が cron 稼働中に無停止で移行完了。domain/ を先に作成してから collector を修正する手順により、import エラーなし。

---

## 3. うまくいったこと

### 3.1 計画の精度

キックオフ資料で立てた12ステップ計画がそのまま実行できた。特に以下の判断が有効だった：

- **domain 先行作成 → collector 後修正** の順序により、cron 環境での import エラーを完全回避
- **sys.path 解決に `Path(__file__).resolve().parent.parent`** を使用。既存 collector の `PROJECT_ROOT` パターンと同じで、cron 環境でも動作保証
- **staleness の仕様書準拠（10/30min）** — `aging` は UI で区別されておらず、3値（fresh/stale/dead）で十分

### 3.2 後方互換の維持

- JSON 出力は「追加のみ」で後方互換を保証
- app.js は `data.staleness || 'stale'` で旧 JSON でもデグレなし
- alert は `health.alert_message` を直接使用し、フロント側のランダム選択を廃止（ドメインが選択責任を持つ）

### 3.3 テストの即時効果

テスト作成時に `test_all_states_reachable` で overall score の計算パラメータを間違えた。
penalty 計算を手で追って修正 → constants の値が正しいことの二重確認になった。
**テストを書く過程自体が仕様の検証プロセスとして機能した。**

---

## 4. 改善点・気づき

### 4.1 collect_health.py の cpu_data 構築

リファクタリング中に cpu_data の構築ロジックで一瞬デッドコードが混入した。
原因: 元コードが CPU 収集失敗時に `cpu_data = None` にする分岐を持っていたが、
domain layer では常にデフォルト値（0.0）で分類するため、条件分岐が不要になった。

**学び:** リファクタリング時、元コードの「失敗パス」が新設計で不要になるケースでは、
安易にコピーせず新設計に合わせて再構築すべき。

### 4.2 staleness の閾値変更

元の app.js: `5分 = aging, 15分 = stale, 60分 = dead`
新 domain/schema.py: `10分 = fresh, 30分 = stale, それ以降 = dead`

仕様書準拠で正しいが、`aging` 状態の消滅と閾値変更は実質的な仕様変更。
UI 上では `aging` と `fresh` は同じ扱いだったため影響なしだが、
明示的にこの差分をキックオフ資料に記載していた点が良かった。

### 4.3 write_json_atomic の重複

`domain/schema.py` に `write_json_atomic()` を新設したが、
`collect_nurture.py` と `collect_skills.py` は自前の `write_json_atomic()` を保持したまま。
Phase 2 で nurture のドメインロジックを domain/ に移す際に統合予定。

---

## 5. 定量データ

| 指標 | 値 |
|------|-----|
| 新規コード（domain/） | ~547行 |
| 新規テストコード | ~427行 |
| 削除コード（collectors + app.js） | ~300行 |
| テスト数 | 95 |
| テスト実行時間 | 0.001秒 |
| JSON 新規フィールド | health: 3, status: 2 |
| 後方互換破壊 | 0 |
| cron ダウンタイム | 0 |

---

## 6. Phase 2 への申し送り

### 6.1 すぐ使える受け皿

- `domain/rebecca.py` の `compose()` が Phase 2 のエントリポイント
  - 現在はパススルーだが、ここに mood / energy / trust によるメッセージ変調を実装する
- `domain/constants.py` に `EXP_TABLE`, `SKILL_LEVEL_LABELS` が既に存在
  - nurture 固有の閾値・分類をここに追加すれば constants.py が完全な単一ソースになる

### 6.2 Phase 2 で対処すべき残課題

| 課題 | 対応方針 |
|------|----------|
| `collect_nurture.py` の計算ロジックが collector 内に残存 | `domain/nurture.py` に移動 |
| `collect_skills.py` の `calculate_level()` が collector 内 | `domain/skills.py` に移動 |
| 3つの `write_json_atomic()` 実装が散在 | `domain.schema.write_json_atomic()` に統合 |
| nurture.json / skills.json に `schema_version` なし | inject_version 適用 |
| バー幅変換（temp clamp, uptime %）が app.js に残存 | プレゼンテーション責務として据え置き（正しい） |

### 6.3 アーキテクチャ図（Phase 1.5 完了時点）

```
                    ┌──────────────────────────┐
                    │      domain/ (純粋ロジック)  │
                    │                          │
                    │  constants ← 全閾値・ラベル  │
                    │  health   ← 分類・スコア    │
                    │  presence ← 在室・時間帯    │
                    │  schema   ← バージョン・鮮度 │
                    │  rebecca  ← [Phase 2 stub] │
                    └─────────┬────────────────┘
                              │ import
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼──┐  ┌────────▼───┐  ┌────────▼───┐
    │ collect_   │  │ collect_   │  │ collect_   │
    │ health.py  │  │ status.py  │  │ nurture.py │
    │ (I/O only) │  │ (I/O only) │  │ (constants │
    └─────┬──────┘  └─────┬──────┘  │  のみ参照)  │
          │               │         └─────┬──────┘
          ▼               ▼               ▼
    ┌─────────────────────────────────────────┐
    │           src/data/*.json                │
    │  health.json  status.json  nurture.json  │
    │  + schema_version, staleness             │
    └────────────────────┬────────────────────┘
                         │ fetch
                   ┌─────▼─────┐
                   │  app.js   │
                   │ (表示のみ)  │
                   └───────────┘
```

---

## 7. 所感

Phase 1.5 は「見た目が変わらないリファクタリング」だった。
ユーザーがブラウザでページを開いても、何も変わっていないように見える。

でも中身は違う。

- 閾値を変えたくなったら `constants.py` だけ触ればいい
- 新しい分類ロジックを追加したらテストで即検証できる
- Phase 2 で Rebecca に「気分」を持たせるとき、`rebecca.py` が待っている

キックオフ資料に書いた「背骨を通す」は達成できた。
次は Phase 2 で、この背骨に「心臓」を付ける番。

---

*作成: 2026-02-13*
*Phase 1.5 実施と同日*
