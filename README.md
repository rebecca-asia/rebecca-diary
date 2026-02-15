# Rebecca's Room

AIアシスタント「Rebecca」の生活空間 — 日記・在室状況・体調・育成パラメータを表示するウェブサイト

## 構造

```
rebecca-diary/
├── scripts/            # SSG・監視スクリプト
├── domain/             # ドメインレイヤー（純粋ロジック）
├── collectors/         # データ収集（I/O層）
├── tests/              # ユニットテスト（201件）
├── src/                # フロントエンド
│   ├── index.html      # メインページ（Room Status）
│   ├── diary.html      # 日記ページ（SSG生成）
│   ├── style.css       # 全スタイル
│   ├── app.js          # JS ロジック
│   └── data/           # 収集データ（gitignored）
└── docs/               # ドキュメント（docs/README.md 参照）
```

## 開発

```bash
# Dev server
cd src && python3 -m http.server 8080

# 日記エントリ追加
python3 scripts/update_diary.py [YYYY-MM-DD]

# テスト実行
python3 -m unittest discover tests/ -v
```

詳細は [CLAUDE.md](CLAUDE.md) および [docs/README.md](docs/README.md) を参照。
