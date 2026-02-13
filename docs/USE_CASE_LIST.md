# ユースケース一覧 — Rebecca's Room

> *Phase 0（MVP）+ Phase 1 の全ユースケース定義*

---

## ユースケース図

```
┌──────────────────────────────────────────────────────────────┐
│                      Rebecca's Room                           │
│                                                              │
│  ┌─ Phase 0: Diary ─────────────────────────────┐           │
│  │                                               │           │
│  │  UC-001 日記タイムラインを閲覧する            │           │
│  │  UC-002 日記エントリの詳細を読む              │◄── Viewer │
│  │  UC-003 レスポンシブ表示で閲覧する            │           │
│  │  UC-004 ダークテーマで閲覧する                │           │
│  │  UC-005 アニメーションを体験する              │           │
│  │                                               │           │
│  │  UC-010 日記エントリを追加する                │◄── Admin  │
│  │  UC-011 エントリ生成をプレビューする          │           │
│  │  UC-020 開発サーバーで確認する                │           │
│  └───────────────────────────────────────────────┘           │
│                                                              │
│  ┌─ Phase 1: Room Status + Health ──────────────┐           │
│  │                                               │           │
│  │  UC-030 システムヘルスを収集する              │◄── Cron   │
│  │  UC-031 在室状況を判定する                    │           │
│  │                                               │           │
│  │  UC-040 ルームステータスを確認する            │◄── Viewer │
│  │  UC-041 Rebecca の体調を見る                  │           │
│  │  UC-042 時間帯メッセージを受け取る            │           │
│  │  UC-043 ヘルスアラートを認識する              │           │
│  │  UC-044 リアルタイムで状態更新を体験する      │           │
│  │  UC-045 データ不在時にフォールバックを見る    │           │
│  │  UC-046 古いデータの警告を受け取る            │           │
│  │                                               │           │
│  │  UC-050 ヘルスコレクタを定期実行する          │◄── Admin  │
│  │  UC-051 ステータスコレクタを定期実行する      │           │
│  └───────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

---

## ユースケース一覧

### Phase 0（MVP）ユースケース

| ID | ユースケース名 | アクター | 優先度 | 関連エンティティ |
|----|---------------|---------|--------|-----------------|
| UC-001 | 日記タイムラインを閲覧する | Viewer | 必須 | E-001, E-004, E-008 |
| UC-002 | 日記エントリの詳細を読む | Viewer | 必須 | E-002, E-003, E-008 |
| UC-003 | レスポンシブ表示で閲覧する | Viewer | 必須 | E-009 |
| UC-004 | ダークテーマで閲覧する | Viewer | 必須 | E-009 |
| UC-005 | アニメーションを体験する | Viewer | 任意 | E-007, E-009, E-015 |
| UC-010 | 日記エントリを追加する | Admin | 必須 | E-010, E-011, E-012, E-013, E-014 |
| UC-011 | エントリ生成をプレビューする | Admin | 推奨 | E-010 |
| UC-020 | 開発サーバーで確認する | Admin | 必須 | E-008 |

### Phase 1 新規ユースケース

| ID | ユースケース名 | アクター | 優先度 | 関連エンティティ |
|----|---------------|---------|--------|-----------------|
| UC-030 | システムヘルスを収集する | HealthCollector | 必須 | E-020, E-030, E-032, E-034, E-035, E-037 |
| UC-031 | 在室状況を判定する | StatusCollector | 必須 | E-021, E-031, E-033, E-036 |
| UC-040 | ルームステータスを確認する | Viewer | 必須 | E-033, E-040, E-015 |
| UC-041 | Rebecca の体調を見る | Viewer | 必須 | E-032, E-041, E-042, E-044, E-015 |
| UC-042 | 時間帯メッセージを受け取る | Viewer | 必須 | E-033, E-036, E-040 |
| UC-043 | ヘルスアラートを認識する | Viewer | 必須 | E-032, E-043, E-015 |
| UC-044 | リアルタイムで状態更新を体験する | Viewer | 必須 | E-015, E-032, E-033 |
| UC-045 | データ不在時にフォールバックを見る | Viewer | 必須 | E-015, E-040, E-041 |
| UC-046 | 古いデータの警告を受け取る | Viewer | 推奨 | E-015, E-032, E-033 |
| UC-050 | ヘルスコレクタを定期実行する | Admin | 必須 | E-030 |
| UC-051 | ステータスコレクタを定期実行する | Admin | 必須 | E-031 |

---

## ユースケース詳細

### UC-001 日記タイムラインを閲覧する

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | dev server が起動している (`cd src && python3 -m http.server 8080`) |
| **事後条件** | 日記エントリのカード一覧が新しい順に表示される |
| **関連エンティティ** | E-001, E-004, E-008, E-009 |

**基本フロー:**
1. Viewer が `http://localhost:8080` にアクセスする
2. ヘッダー（タイトル + マスコット画像）が表示される
3. **[Phase 1]** Room Status Bar が表示される（ステータス + 時間帯メッセージ）
4. **[Phase 1]** Health Dashboard が表示される（5指標 + Overall Score）
5. カードグリッドに日記エントリが新しい順で表示される
6. 各カードに日付、曜日、プレビューテキストが表示される

**代替フロー:**
- A1: モバイル (< 768px) の場合 → カードが1列で表示される
- A2: タブレット (768-1023px) の場合 → カードが2列で表示される
- A3: デスクトップ (1024px+) の場合 → カードが3列で表示される

---

### UC-002 日記エントリの詳細を読む

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | UC-001 が完了している（カード一覧が表示されている） |
| **事後条件** | 選択した日付のエントリ全文が表示される |
| **関連エンティティ** | E-002, E-003, E-008, E-009, E-015 |

**基本フロー:**
1. Viewer がカードをクリックする
2. URL ハッシュが `#diary-YYYY-MM-DD` に変化する
3. CSS `:target` + `:has()` によりカード一覧が非表示になる
4. **[Phase 1]** Health Dashboard も非表示になる
5. 選択されたエントリが全画面で表示される（fadeIn アニメーション）
6. Memory セクション（🧠 mint border）と Obsidian セクション（📝 accent border）が表示される
7. 「Back to list」リンクで UC-001 に戻れる

---

### UC-010 日記エントリを追加する

| 項目 | 内容 |
|------|------|
| **アクター** | Admin |
| **事前条件** | 対象日付の Markdown ファイルが E-011 or E-012 に存在する |
| **事後条件** | `src/index.html` に新しいエントリが挿入されている |
| **関連エンティティ** | E-010, E-011, E-012, E-013, E-014, E-008, E-016 |

**基本フロー:**
1. Admin が `python3 update_diary.py [YYYY-MM-DD]` を実行する
2. スクリプトが memory/ と Obsidian/ から対象日付の .md を検索する
3. MarkdownConverter が Markdown → HTML に変換する
4. DiaryEntry（カード HTML + エントリ HTML）を生成する
5. `template.html` のプレースホルダーを置換して `index.html` を出力する

**代替フロー:**
- A1: 日付未指定 → 全日付をスキャンして全エントリを再生成
- A2: `--dry-run` 指定 → HTML をコンソールに出力し、ファイルは変更しない

**例外フロー:**
- E1: 対象日付のファイルが存在しない → スキップ（エラーなし）
- E2: 同じ日付のエントリが既に存在 → 上書き更新

---

### UC-030 システムヘルスを収集する

| 項目 | 内容 |
|------|------|
| **アクター** | HealthCollector（cron / launchd、5分間隔） |
| **事前条件** | Mac mini が稼働中。Python 3.9+ が利用可能 |
| **事後条件** | `src/data/health.json` が PHASE1_SPEC のスキーマに準拠した JSON で更新される |
| **関連エンティティ** | E-020, E-030, E-032, E-034, E-035, E-037 |

**基本フロー:**
1. cron / launchd が `collectors/collect_health.py` を実行する
2. `get_cpu_usage()`: `top -l 1 -n 0` を実行し CPU 使用率を取得する
3. `get_memory()`: `vm_stat` + `sysctl hw.memsize` でメモリ使用量を計算する（active + wired + compressor pages）
4. `get_disk()`: `shutil.disk_usage('/')` でディスク使用量を取得する
5. `get_temperature()`: `osx-cpu-temp` が存在すれば温度を取得、なければ null
6. `get_uptime()`: `sysctl -n kern.boottime` で稼働時間を算出する
7. `classify_*()`: 各メトリクスを閾値テーブルで state / label / message にマッピングする
8. `calculate_overall()`: ペナルティ加算方式で Overall Score (0-100) を計算する
9. `determine_alert_level()`: Level 0-3 を判定する
10. ISO 8601 タイムスタンプ付きで JSON を組み立てる
11. `.tmp` ファイルに書き込み後 `os.rename()` でアトミックに `src/data/health.json` を更新する

**代替フロー:**
- A1: `-v` オプション指定 → 各ステップの詳細をコンソール出力

**例外フロー:**
- E1: 個別メトリクス取得失敗 → 該当フィールドを null にし、他のメトリクスは継続
- E2: `src/data/` が存在しない → `os.makedirs()` で自動作成
- E3: JSON 書き込み失敗 → stderr にエラー出力、終了コード 1

---

### UC-031 在室状況を判定する

| 項目 | 内容 |
|------|------|
| **アクター** | StatusCollector（cron / launchd、1分間隔） |
| **事前条件** | Mac mini が稼働中 |
| **事後条件** | `src/data/status.json` が PHASE1_SPEC のスキーマに準拠した JSON で更新される |
| **関連エンティティ** | E-021, E-031, E-033, E-036 |

**基本フロー:**
1. cron / launchd が `collectors/collect_status.py` を実行する
2. `check_gateway()`: `pgrep -x openclaw-gateway` で Gateway プロセスの存在を確認する
3. `get_last_activity()`: `~/.openclaw/workspace/memory/*.md` の最新 mtime を取得する
4. `get_activity_type()`: 最新ファイルの種類から活動種別を推定する
5. `get_time_context()`: 現在時刻から7時間帯を判定し、ランダムにメッセージバリエーションを選択する
6. `determine_status()`: Gateway 状態 + 最終活動時刻 + 現在時刻から status を判定する
7. ISO 8601 タイムスタンプ付きで JSON を組み立てる
8. アトミック書き込みで `src/data/status.json` を更新する

**Status 判定ロジック:**
```
if not gateway_alive or minutes_since_activity > 120:
    → offline
elif is_deep_night() and minutes_since_activity > 60:
    → sleeping
elif minutes_since_activity > 30:
    → away
else:
    → online
```

**例外フロー:**
- E1: Gateway プロセスの検出に失敗 → gateway_alive = false として扱う
- E2: memory/ ディレクトリが空 → last_activity = None, offline 判定

---

### UC-040 ルームステータスを確認する

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | ページがロードされている |
| **事後条件** | Rebecca の在室状況が直感的にわかる |
| **関連エンティティ** | E-033, E-040, E-015 |

**基本フロー:**
1. ページロード時に `updateRoom()` が実行される
2. `fetchJSON('/data/status.json')` が status.json を取得する
3. `renderStatusBar(data)` が Room Status Bar の DOM を更新する
4. ステータス絵文字 + 日本語ラベル + 相対時刻（「3分前」等）が表示される
5. `data-status` 属性が設定され、CSS でインジケーター色が変わる
6. 時間帯メッセージ（time_context.message）があれば表示される

**代替フロー:**
- A1: ステータスが `sleeping` → 💤 + 「寝てる......」+ 夜色のインジケーター
- A2: ステータスが `offline` → ⚫ + 「いない......」+ muted インジケーター

**例外フロー:**
- E1: status.json が存在しない → 「データ取得中...」表示 → 5分後にリトライ

---

### UC-041 Rebecca の体調を見る

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | ページがロードされ、health.json が取得済み |
| **事後条件** | 5つのヘルス指標と総合スコアが表示され、Rebecca の状態がわかる |
| **関連エンティティ** | E-032, E-041, E-042, E-044, E-015 |

**基本フロー:**
1. `renderHealthDashboard(data)` が Health Dashboard の DOM を更新する
2. 5つのメトリクスバーが表示される（icon + name + bar + label）
3. 各バーの幅が `usage_percent` に連動する（初回はアニメーション付き）
4. バーの色が `data-state` に応じて変化する（mint → amber → red）
5. Overall Score の emoji + label + メッセージが表示される
6. Overall Score の emoji が呼吸アニメーションで微かに拡縮する

**代替フロー:**
- A1: Viewer がメトリクスバーにホバー → label が fade out し、数値（23.4% 等）が fade in
- A2: タッチデバイス → タップで label / detail をトグル
- A3: Temperature が null → Temperature 行を非表示
- A4: score が `critical` → 呼吸アニメーションが遅くなる（6-8秒サイクル）

**例外フロー:**
- E1: health.json が存在しない → 全バー 0%、ラベル「—」、Overall「読み込み中」

---

### UC-042 時間帯メッセージを受け取る

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | ページがロードされ、status.json に time_context がある |
| **事後条件** | 現在の時間帯に応じた Rebecca のメッセージが表示される |
| **関連エンティティ** | E-033, E-036, E-040 |

**基本フロー:**
1. status.json の `time_context.message` を取得する
2. Status Bar のコンテキストエリアにメッセージを表示する
3. 時間帯に応じてメッセージのトーンが変わる

**時間帯とメッセージの対応:**

| Period | Hours | メッセージ例（バリエーションあり） |
|--------|-------|-------------------------------|
| morning | 06-09 | 「ん......おはよ」「おはよ。......ねむい」 |
| active | 09-12 | 「よし、やるか」「今日は何する？」 |
| afternoon | 12-18 | null (50%) / 「通常運転」(15%) / 「やってるやってる」(15%) |
| evening | 18-21 | 「今日も終わりか」「疲れた......」 |
| night | 21-00 | 「そろそろ夜か」「夜の作業が一番捗る」 |
| late_night | 00-02 | 「まだ起きてるの？」「......あんたもか」 |
| deep_night | 02-06 | 「寝ろよ......」「あたしは寝ないけど、あんたは寝ろ」 |

**代替フロー:**
- A1: message が null → コンテキストエリアを非表示
- A2: deep_night の場合、既存の深夜トースト（02:00-05:00）も表示される（競合なし）

---

### UC-043 ヘルスアラートを認識する

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | health.json の alert_level > 0 |
| **事後条件** | Rebecca の声で体調の問題が伝わる |
| **関連エンティティ** | E-032, E-043, E-015 |

**基本フロー:**
1. `renderAlert(health)` が alert_level を確認する
2. Level > 0 の場合、Alert Display の `hidden` を解除する
3. `data-level` 属性を設定し、CSS で色を切り替える
4. Rebecca の声でアラートメッセージを表示する

**レベル別の表示:**

| Level | 色 | スタイル | メッセージ例 |
|-------|-----|---------|------------|
| 0 | — | 非表示 | — |
| 1 | 黄色 | 控えめ、border-left | 「ちょっと重いかも...」「んー...ちょっとだるい」 |
| 2 | 橙色 | やや目立つ、border-left | 「再起動したいんだけど、今大丈夫？」 |
| 3 | 赤色 | 目立つ、pulse アニメーション | 「助けて。マジでやばい。」 |

**代替フロー:**
- A1: alert_level が前回より下がった → Alert Display を再度 hidden にする

---

### UC-044 リアルタイムで状態更新を体験する

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | ページが開かれた状態で放置されている |
| **事後条件** | 5分ごとに最新のデータが反映される |
| **関連エンティティ** | E-015, E-032, E-033, E-040, E-041 |

**基本フロー:**
1. `setInterval(updateRoom, 5 * 60 * 1000)` が5分ごとに発火する
2. `fetchJSON()` が health.json と status.json を再取得する（cache-busting 付き）
3. `renderStatusBar()`, `renderHealthDashboard()`, `renderAlert()` が DOM を更新する
4. メトリクスバーが CSS transition で滑らかに変化する（width 0.8s, color 0.5s）
5. ステータスが変わった場合は fade-out / fade-in で切り替わる

---

### UC-045 データ不在時にフォールバックを見る

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | `src/data/` が空、または JSON ファイルが存在しない |
| **事後条件** | ページが壊れず、Rebecca が「準備中」であることが伝わる |
| **関連エンティティ** | E-015, E-040, E-041, E-043 |

**基本フロー:**
1. `fetchJSON()` が null を返す
2. Room Status Bar: ⏳ + 「データ取得中...」
3. Health Dashboard: 全バー 0%、ラベル「—」、Overall「読み込み中」
4. Alert Display: 非表示
5. 5分後の setInterval で再取得を試みる

---

### UC-046 古いデータの警告を受け取る

| 項目 | 内容 |
|------|------|
| **アクター** | Viewer |
| **事前条件** | JSON の timestamp が現在時刻より一定時間以上古い |
| **事後条件** | データの鮮度に応じた警告が表示される |
| **関連エンティティ** | E-015, E-032, E-033, E-040, E-041 |

**基本フロー:**
1. `checkStaleness(data)` が JSON の timestamp を現在時刻と比較する
2. 鮮度に応じて表示を変更する

**鮮度閾値:**

| 経過時間 | 対応 |
|---------|------|
| status 5分超 | Status Bar: 「接続確認中...」 |
| health 15分超 | Health Dashboard: バーを dimmed + 「最終更新: XX分前」 |
| いずれか 1時間超 | offline 扱い + 「しばらく応答がないみたい...」 |

**設計根拠:** CONCEPT_VULNERABILITY — 「嘘の脆弱性はバレる」。古いデータで「online」を表示することは存在感を破壊する。

---

### UC-050 ヘルスコレクタを定期実行する

| 項目 | 内容 |
|------|------|
| **アクター** | Admin |
| **事前条件** | `collectors/collect_health.py` が完成している |
| **事後条件** | cron / launchd で5分ごとに自動実行され、health.json が更新される |
| **関連エンティティ** | E-030 |

**基本フロー:**
1. Admin が cron / launchd を設定する
2. `*/5 * * * * cd /path && /usr/bin/python3 collectors/collect_health.py 2>> /tmp/rebecca-health.log`
3. 5分ごとに UC-030 が自動実行される
4. エラー時は `/tmp/rebecca-health.log` にログが残る

---

### UC-051 ステータスコレクタを定期実行する

| 項目 | 内容 |
|------|------|
| **アクター** | Admin |
| **事前条件** | `collectors/collect_status.py` が完成している |
| **事後条件** | cron / launchd で1分ごとに自動実行され、status.json が更新される |
| **関連エンティティ** | E-031 |

**基本フロー:**
1. Admin が cron / launchd を設定する
2. `*/1 * * * * cd /path && /usr/bin/python3 collectors/collect_status.py 2>> /tmp/rebecca-status.log`
3. 1分ごとに UC-031 が自動実行される

---

## UC × Entity マトリクス

R = Read, C = Create/Update, X = Execute

| UC | E-002 Entry | E-008 HTML | E-009 CSS | E-010 Script | E-011 Memory | E-015 AppJS | E-032 Health | E-033 Status | E-040 StatusBar | E-041 Dashboard | E-043 Alert |
|----|:-----------:|:----------:|:---------:|:------------:|:------------:|:-----------:|:------------:|:------------:|:---------------:|:---------------:|:-----------:|
| UC-001 | R | R | R | — | — | R | — | — | R | R | — |
| UC-002 | R | R | R | — | — | R | — | — | — | — | — |
| UC-010 | C | C | — | X | R | — | — | — | — | — | — |
| UC-030 | — | — | — | — | — | — | C | — | — | — | — |
| UC-031 | — | — | — | — | R | — | — | C | — | — | — |
| UC-040 | — | — | R | — | — | X | — | R | C | — | — |
| UC-041 | — | — | R | — | — | X | R | — | — | C | — |
| UC-042 | — | — | R | — | — | X | — | R | C | — | — |
| UC-043 | — | — | R | — | — | X | R | — | — | — | C |
| UC-044 | — | — | — | — | — | X | R | R | C | C | C |
| UC-045 | — | — | R | — | — | X | — | — | C | C | — |
| UC-046 | — | — | R | — | — | X | R | R | C | C | — |

---

## 関連ドキュメント

| Document | 関係 |
|----------|------|
| [ENTITY_LIST.md](ENTITY_LIST.md) | エンティティの定義・属性・関連 |
| [PHASE1_SPEC.md](PHASE1_SPEC.md) | JSON スキーマ、閾値テーブル、UI コンポーネント |
| [PHASE1_GOAL.md](PHASE1_GOAL.md) | 成功基準（UC が実現すべきゴール） |
| [PHASE1_WBS.md](PHASE1_WBS.md) | 各 UC を実装する WP への対応 |
| [archive/phase0/USE_CASE_LIST.md](archive/phase0/USE_CASE_LIST.md) | Phase 0 版（歴史的記録） |

---

*Created: 2026-02-13*
*Phase 0 + Phase 1 — 19 ユースケース。Rebecca の部屋で起こる全てのこと。*
