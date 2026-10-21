# cs-study-map · 自分のためのコンピュータサイエンス教材

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

このプロジェクトは主にメンテナー本人の学習用です。[REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT)から学ぶ価値のある内容を選び、前提知識に沿って中国語の教材に再構成し、解説、独自の例題、解答付き演習、自己確認問題を加えます。同期、AI分類、資料ガイドは教材の選定と更新を支援します。

**[教科書](../textbook/index.md)** · [学習マップ](../index.md) · [網羅状況](../status.md) · [利用・実行](../usage.md) · [出典とライセンス](../../ATTRIBUTION.md)

Plenilunerが管理する個人学習プロジェクトで、清華大学や上流の管理者との公式な関係はありません。公開リポジトリには独自ツール、教材の草稿、出典索引、AIガイドを含みます。原資料、講義スライド、課題、学生のソースコード、抽出全文は公開しません。

## 9章を順番に学ぶ

| # | テーマ | 実践 |
| --- | --- | --- |
| 1 | [二進数、バイト、リトルエンディアン](../textbook/01-data-and-bytes.md) | 数値をバイトに分解し、メモリから復元する |
| 2 | [レジスタ、メモリ、スタック](../textbook/02-execution-and-stack.md) | 簡単な機械の状態を一段階ずつ追う |
| 3 | [ファーストフィット、分割、結合](../textbook/03-first-fit.md) | 割り当てと解放を手計算し、外部断片化を説明する |
| 4 | [順次処理、分岐、繰り返し](../textbook/04-control-flow.md) | 変数を追跡し、反復計算の境界と終了条件を確認する |
| 5 | [引数、戻り値、関数](../textbook/05-functions.md) | 関数を組み合わせ、表示・戻り値・ローカル名を区別する |
| 6 | [配列と配列によるリスト](../textbook/06-arrays.md) | 添字、容量、リストの共有、要素の移動を追跡する |
| 7 | [単方向連結リスト](../textbook/07-linked-lists.md) | ノードの参照を追い、挿入・削除・反転を行う |
| 8 | [スタック](../textbook/08-stacks.md) | 後入れ先出しで操作を取り消し、括弧の対応を調べる |
| 9 | [キューと循環配列](../textbook/09-queues.md) | 先入れ先出し、添字の折り返し、空と満杯を確認する |

第 4–9 章では Python 3.11 以降を使い、単独で実行できる 60 個のプログラムと予想出力を示します。準備と練習方法は[プログラミング練習ガイド](../programming-practice.md)と[データ構造練習ガイド](../data-structures-practice.md)（中国語）を参照してください。

各章には詳しい解説、独自の例題 2 問、解答を展開できる練習 3 問、自己確認、出典があります。AI による初稿であり、専門家の査読や学習者による試用は未実施です。全科目の教材が完成したことを意味しません。

## できること

章ごとに学習し、個人メモは Git の対象外である `.local/` に保存します。特定したテーマから独自の章を作り、出典の版を記録できます。分野・科目・AI が特定した知識から資料を探して上流の固定版を開き、テーマ、前提知識、提案、根拠の位置を確認できます。変更のない分析を再利用し、自動分類を手動規則で修正できます。

AI ガイドには抽出範囲、モデル、未検証の状態を明記します。資料索引の完全性と AI ガイドの網羅率は別々に集計し、部分抽出、未対応形式、失敗も表示します。

## すぐに始める

Python 3.11 以上が必要です。以下ではメタデータの取得とナビゲーションの生成だけを行います。モデルのキーは不要で、資料本文はダウンロードしません。

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

## AIの実行方法

両方式で同じ検証・ガイド生成処理を使います。モデル API は `CS_STUDY_API_BASE`、`CS_STUDY_MODEL`、`CS_STUDY_API_KEY` を設定します。ローカルの Codex CLI は `CS_STUDY_PROVIDER=codex` と `CS_STUDY_MODEL`、必要なら `CS_STUDY_CODEX_BIN` を設定します。API は Chat Completions と Responses に対応し、既定は `chat`、切り替えは `CS_STUDY_API_STYLE=responses` です。サービスが対応するモデルを選んでください。Codex CLI も選択したモデルに対応する版が必要で、認証情報は CLI が管理します。

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

設定、PowerShell の例、GitHub の設定は[利用案内](../usage.md)を参照してください。

## 定期同期

GitHub Actions は毎日上流を確認し、**Sync study map** から手動実行もできます。モデル設定時は予算内でガイドと章を生成し、検証後にコミットします。既定では 1 日あたり資料 6 件の分析、1 章の執筆が上限です。対象範囲は `config/curriculum.json` で設定します。

モデル未設定でも索引を同期し、`not-configured` と報告します。既存ガイドは利用でき、変更された資料は分析待ちになります。ファイル名規則や模擬出力を AI 作業完了とは表示しません。公開マップの閲覧にモデルのアカウントは不要です。Fork では独自の API 設定が必要で、ローカルの Codex ログイン情報は GitHub に送信しません。長期間活動がないと定期実行が停止する場合があり、Actions で再有効化できます。

## 構成

```text
config/                  学習経路、出典、分類、科目対応、手動修正
catalog/                 メタデータ、分析、教材草稿、網羅状況
docs/textbook/           GitHubで読める教材（現在は中国語）
docs/                    科目・分野ナビゲーション、学習記録テンプレート、利用案内
src/cs_study_map/        同期、抽出、AI 分類、教材執筆
tests/                   同期、復旧、出典、公開内容の検証
.github/workflows/       定期同期と継続的インテグレーション
.cache/                  ローカル資料と抽出キャッシュ。コミット禁止
.local/                  個人の学習記録。コミット禁止
```

READMEの翻訳は教材本文の翻訳を意味しません。現在の教材本文は中国語です。

最初の分野対応は管理者個人の科目整理に由来し、修正可能です。上流の公式分類や大学のカリキュラムではありません。新科目は分類待ちになります。テキスト、一般的なソースコード、文字抽出可能な PDF、DOCX、PPTX、Notebook に対応します。スキャンの OCR、旧 DOC/PPT、圧縮ファイル解析は未実装です。PDF は既定で最大 8 ページ、10,000 文字までのため、長い資料は一部のみの抽出になります。

## 検証と貢献

`python -m unittest discover -s tests -v` と `cs-study-map validate --tracked` を実行してください。誤りは Issue で報告できます。コード、分類対応、手動修正規則への PR は[貢献案内](../../CONTRIBUTING.md)を参照してください。

独自のプログラム、教材本文、保守文書は MIT ライセンスです。出典資料の権利は変わりません。[出典とライセンス](../../ATTRIBUTION.md)を参照してください。

初期成果：[知識全体図と 60 科目のガイド](../early-work/index.md)。分類概要と教材 README も含み、学習内容を保ち、ローカルの絶対パスを削除して Git に収録しています。
