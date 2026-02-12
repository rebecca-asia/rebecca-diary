# エンティティ一覧

## 1. エンティティ関連図

```
[閲覧者] ---閲覧--→ [日記ウェブサイト]
                         │
                         ├── [ヘッダー]
                         │       └── [マスコット画像]
                         │
                         ├── [タイムライン]
                         │       └── [日記エントリ] ※複数
                         │               ├── [エントリ日付]
                         │               └── [エントリコンテンツ]
                         │                       └── [セクション] ※複数
                         │
                         └── [フッター]

[管理者] ---実行--→ [update_diary.py]
                         │
                         ├──読取→ [OpenClawメモリファイル]
                         ├──読取→ [Obsidianデイリーノート]
                         └──書込→ [index.html]
```

## 2. エンティティ一覧

| ID | エンティティ名 | 日本語名 | 種別 | 説明 |
|----|---------------|---------|------|------|
| E-001 | DiaryWebsite | 日記ウェブサイト | システム | Rebeccaの日記を公開する静的サイト全体 |
| E-002 | DiaryEntry | 日記エントリ | データ | 1日分の日記記事。日付・コンテンツを持つ |
| E-003 | DiarySection | 日記セクション | データ | エントリ内のソース別区画（Memory / Obsidian） |
| E-004 | Timeline | タイムライン | UI構造 | 日記エントリを時系列に表示するコンテナ |
| E-005 | Header | ヘッダー | UI構造 | サイトタイトル・マスコット画像を含む領域 |
| E-006 | Footer | フッター | UI構造 | 著作権情報を含むフッター領域 |
| E-007 | MascotImage | マスコット画像 | アセット | Rebeccaのスティッカー画像（rebecca-sticker.webp） |
| E-008 | IndexHTML | index.html | ファイル | メインページ。全日記エントリを含む単一HTMLファイル |
| E-009 | StyleCSS | style.css | ファイル | 全スタイル定義（ダークテーマ・アニメーション・レスポンシブ） |
| E-010 | UpdateDiaryScript | update_diary.py | ツール | Markdownソースから日記エントリを生成・挿入するCLI |
| E-011 | OpenClawMemoryFile | OpenClawメモリファイル | 外部データ | `~/.openclaw/workspace/memory/{YYYY-MM-DD}.md` |
| E-012 | ObsidianDailyNote | Obsidianデイリーノート | 外部データ | `~/Documents/Obsidian Vault/{YYYY-MM-DD}.md` |
| E-013 | MarkdownConverter | Markdownコンバータ | 処理 | Markdown→HTML変換を行う内部クラス |
| E-014 | InsertionMarker | 挿入マーカー | 構造 | `<!-- 日記エントリはここに追加される -->` コメント |

## 3. エンティティ詳細

### E-002: DiaryEntry（日記エントリ）

| 属性 | 型 | 説明 |
|------|------|------|
| date | string (YYYY-MM-DD) | エントリの日付 |
| sections | list[DiarySection] | ソース別セクションのリスト |
| has_content | bool (算出) | セクションが1つ以上あるか |

HTML構造:
```html
<article class="diary-entry">
    <div class="entry-date">{date}</div>
    <div class="entry-content">
        {sections}
    </div>
</article>
```

### E-003: DiarySection（日記セクション）

| 属性 | 型 | 説明 |
|------|------|------|
| title | string | セクション見出し（例: "Internal Memory (OpenClaw)"） |
| icon | string | 絵文字アイコン（例: "🧠", "📝"） |
| css_class | string | CSSクラス名（"memory" or "obsidian"） |
| body_html | string | Markdownから変換されたHTML本文 |

### E-009: StyleCSS（CSSカスタムプロパティ）

| 変数名 | 値 | 用途 |
|--------|------|------|
| --bg-color | #0d1117 | ページ背景色 |
| --card-bg | #21262d | エントリカード背景色 |
| --text-main | #c9d1d9 | メインテキスト色 |
| --text-sub | #8b949e | サブテキスト色 |
| --accent | #ff69b4 | ピンクアクセント色 |
| --accent-secondary | #58a6ff | ブルーアクセント色 |
| --border | #30363d | ボーダー色 |

## 4. アクター一覧

| ID | アクター名 | 説明 |
|----|-----------|------|
| A-001 | 閲覧者 | ウェブサイトを閲覧するユーザー（一般公開） |
| A-002 | 管理者（Rebecca / Takeru） | 日記エントリの追加・サイト更新を行う管理者 |
| A-003 | update_diary.py | 自動化ツールとしてのシステムアクター |
