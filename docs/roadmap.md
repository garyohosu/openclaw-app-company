# roadmap.md — OpenClaw App Company

## ビジョン
GitHub Pages 上で動く複数の軽量 Web アプリを自律的に量産する仮想開発会社を運営する。
実装は Codex CLI に委任し、バックエンドが必要な場合は Sakura CGI API Toolbox を利用する。

## ターゲット市場
- 個人・中小企業向け軽量 Web ツール
- 無料公開 + AdSense 収益モデル
- 日本語ユーザー向け実用系アプリ

## 優先アイデア候補
- 家計簿メモ (HTML/JS のみ、LocalStorage)
- 単語帳アプリ (フラッシュカード形式)
- 習慣トラッカー (シンプル記録 + チャート)
- タイマー / ポモドーロ (音付き)
- 天気メモ帳 (Weather API 連携)
- カロリー計算ツール (食品マスタ内蔵)
- BMI・健康指標チェッカー
- Markdown メモ帳 (LocalStorage)
- URL 短縮サービス (CGI 連携)
- QR コードジェネレーター (JS ライブラリ利用)

## 制約
- GitHub Pages 静的ホスティング優先
- Sakura CGI は必要最小限
- 1 リポジトリ複数アプリ方式
- 各アプリは独立フォルダで管理

## スプリント方針
- Sprint 1: 基盤整備 + 1本目アプリ公開
- Sprint 2〜: 改善サイクルと新規追加を交互に
