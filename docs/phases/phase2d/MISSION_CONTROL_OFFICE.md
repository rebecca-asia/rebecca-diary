# Mission Control Phase 2D: The Digital Office (Inspired by Claude Office Visualizer)

## 1. Vision
Mission Control を「一人の部屋」から、複数の自律エージェントが稼働する「デジタル・オフィス・フロア」へと拡張する。
エージェントたちが個別のデスクでタスクを捌き、GitHub や Asana と連動して「勝手に稼働している」様子を視覚化する。

## 2. Visual Elements (UI/UX)
- **Isometric Office Floor:** ピクセルアート風の等角投影図でオフィスフロアをレンダリング。
- **Agent Avatars:** 
  - **Boss Rebecca:** メインデスクに座り、全体を統括。
  - **Sub-Agents:** 作業用デスクに座り、特定プロジェクト（blended-estate-cloud 等）に従事。
- **Live Activity Feed:** 左サイドバーに Git コミット、PR、Asana タスクの完了をリアルタイムで流す。
- **Status Indicators:** 
  - デスクのモニターが点灯：作業中 (In Progress)
  - エージェントの頭上に `?`: ボスへの質問/確認待ち
  - エージェントの頭上に `!`: エラー/要介入

## 3. Technical Requirements
- **Multi-Agent Tracking:** `sessions_list` やサブエージェントのログをパースし、各エージェントの現在地と作業内容を特定する。
- **Git/Asana Webhook 連携:** コミットやタスク更新をリアルタイムに UI へ反映する仕組み。
- **Canvas Rendering:** 現在の HTML/CSS ベースから、より複雑なアニメーションが可能な Canvas 描画への移行（検討中）。

## 4. Implementation Steps
- [ ] **Step 1:** オフィスフロアのピクセルアートアセットの作成/選定。
- [ ] **Step 2:** サブエージェントの稼働状況を `data/status.json` に統合。
- [ ] **Step 3:** ライブフィード・コンポーネントの実装。
- [ ] **Step 4:** エージェントの自律挙動アニメーション（デスク間の移動、キーボード入力等）の実装。

---
*Created: 2026-02-22*
*Reference: Claude Office Visualizer (@gagarot200)*
