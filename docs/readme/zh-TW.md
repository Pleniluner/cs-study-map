# cs-study-map · 給自己的計算機教材

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

本專案主要供維護者本人自學：從 [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) 找出可學習的知識，依先修關係重新編排為中文教材，補上概念講解、原創例題、練習解答與自我檢測。自動同步、AI 分類與資料導讀支援教材選材和更新。

**[教材](../textbook/index.md)** · [資料地圖](../index.md) · [涵蓋狀態](../status.md) · [使用與執行](../usage.md) · [來源與授權](../../ATTRIBUTION.md)

這是 Pleniluner 維護的個人學習專案，與清華大學及上游維護者沒有官方隸屬關係。公開儲存庫包含原創工具、教材草稿、來源索引和 AI 導讀；不發布原始教材、課件、作業、學生原始碼或擷取全文。

## 依十八章順序學習

| # | 主題 | 實作 |
| --- | --- | --- |
| 1 | [二進位、位元組與小端序](../textbook/01-data-and-bytes.md) | 把數值拆成位元組，再從記憶體還原 |
| 2 | [暫存器、記憶體與堆疊](../textbook/02-execution-and-stack.md) | 逐步追蹤簡化機器的狀態 |
| 3 | [首次適應、分割與合併](../textbook/03-first-fit.md) | 手算配置與釋放，解釋外部碎片 |
| 4 | [循序、分支與迴圈](../textbook/04-control-flow.md) | 追蹤變數、編寫重複計算，檢查邊界與停止條件 |
| 5 | [參數、回傳值與函式](../textbook/05-functions.md) | 組合函式，區分列印、回傳與區域名稱 |
| 6 | [陣列與循序串列](../textbook/06-arrays.md) | 追蹤索引、容量、串列共享與元素搬移 |
| 7 | [單向鏈結串列](../textbook/07-linked-lists.md) | 追蹤節點參照，完成插入、刪除與反轉 |
| 8 | [堆疊](../textbook/08-stacks.md) | 用後進先出處理復原歷史與括號配對 |
| 9 | [佇列與環狀陣列](../textbook/09-queues.md) | 核對先進先出、索引繞回及空滿狀態 |
| 10 | [演算法分析](../textbook/10-algorithm-analysis.md) | 計算操作次數，區分成長量級與額外空間 |
| 11 | [循序搜尋與二分搜尋](../textbook/11-searching.md) | 追蹤邊界，處理重複值與找不到的目標 |
| 12 | [選擇、插入與合併排序](../textbook/12-sorting.md) | 檢查順序、元素數量、穩定性與排序後搜尋 |
| 13 | [遞迴、回傳與呼叫堆疊](../textbook/13-recursion.md) | 追蹤基底情況、縮小量、總呼叫數與最高堆疊深度 |
| 14 | [分治與遞迴合併排序](../textbook/14-divide-and-conquer.md) | 拆分區間、組合答案，計算逆序對 |
| 15 | [快速排序與三路劃分](../textbook/15-quick-sort.md) | 檢查分區、重複值、最壞情況與堆疊深度 |
| 16 | [樹、二元樹與走訪](../textbook/16-trees.md) | 追蹤高度、走訪順序、鏡像與完全性 |
| 17 | [二元搜尋樹](../textbook/17-binary-search-trees.md) | 維護全域鍵值順序、刪除連結、範圍查詢與高度界限 |
| 18 | [二元堆積與優先佇列](../textbook/18-heaps.md) | 實作上浮、下沉、建堆與堆積排序，處理最大的 k 項與多路合併 |

第 4–18 章使用 Python 3.11 或更新版本，共提供 150 段可獨立執行的程式及預期輸出。練習方法見[程式練習指南](../programming-practice.md)、[資料結構練習指引](../data-structures-practice.md)與[演算法練習指引](../algorithms-practice.md)（簡體中文）。 [遞迴與分治練習指引（簡體中文）](../recursion-practice.md). [樹與堆積練習指引（簡體中文）](../trees-practice.md).

每章包含詳細講解、2 個原創例題、3 道附可展開解答的練習、自我檢測與選題來源。目前是 AI 初稿，尚未經學科專家審查或學習者試學，不代表所有課程都已完成教材。

## 可以做什麼

依章節學習，將私人筆記保存在 Git 忽略的 `.local/`；從已識別主題建立原創章節並記錄來源版本；依領域、課程或 AI 知識點查找資料，開啟上游固定版本；查看主題、先修知識、建議與證據位置；檢查來源變更並重用未變的分析；以人工規則修正自動分類。

AI 導讀註明擷取範圍、模型與未人工核驗狀態。索引完整度與 AI 導讀涵蓋率分別統計；部分擷取、不支援的格式及失敗均如實呈現。

## 快速開始

需要 Python 3.11 以上。以下步驟只取得中繼資料並建立導覽，不需要模型金鑰，也不下載來源全文。

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

## AI 執行方式

兩種方式共用驗證與導讀流程。模型 API 設定 `CS_STUDY_API_BASE`、`CS_STUDY_MODEL`、`CS_STUDY_API_KEY`；本機 Codex CLI 設定 `CS_STUDY_PROVIDER=codex` 與 `CS_STUDY_MODEL`，可另設 `CS_STUDY_CODEX_BIN`。API 支援 Chat Completions 與 Responses，預設為 `chat`；使用 `CS_STUDY_API_STYLE=responses` 可切換。請選擇服務實際支援的模型。Codex CLI 版本須支援所選模型，並自行管理登入憑據。

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

設定、PowerShell 範例與 GitHub 設置詳見[使用說明](../usage.md)。

## 定期同步

GitHub Actions 每天檢查上游，也可手動執行 **Sync study map**。設定模型後，工作流會在預算內產生導讀和章節，驗證後提交更新。預設每天最多分析 6 份資料、編寫 1 章；範圍由 `config/curriculum.json` 設定。

未設定模型時仍同步目錄，並回報 `not-configured`；既有導讀仍可閱讀，來源變更則等待分析。檔名規則和模擬輸出不會標成已完成的 AI 工作。瀏覽公開地圖不需模型帳號；Fork 須自行設定模型 API，本機 Codex 登入不會上傳至 GitHub。長期無活動時，GitHub 可能停用排程，可在 Actions 重新啟用。

## 專案結構

```text
config/                  學習路線、來源、分類、課程映射與人工修正
catalog/                 中繼資料、分析結果、教材草稿與涵蓋統計
docs/textbook/           GitHub 可閱讀的教材（目前為中文）
docs/                    課程與領域導覽、學習紀錄範本與使用說明
src/cs_study_map/        同步、擷取、AI 分類與教材編寫
tests/                   同步、復原、來源追溯與發布檢查
.github/workflows/       定期同步與持續整合
.cache/                  本機原始檔及擷取快取；禁止提交
.local/                  個人學習紀錄；禁止提交
```

README 的翻譯不代表教材正文也已翻譯；目前教材正文為中文。

初始領域映射來自維護者的個人課程整理，可再修正，並非上游官方分類或學校課程規劃。新課程標為待分類。支援文字、常見原始碼、可擷取文字的 PDF、DOCX、PPTX 與 Notebook；尚未實作掃描件 OCR、舊 DOC/PPT 或壓縮檔分析。PDF 預設最多擷取 8 頁及 10,000 字元，長篇講義可能只讀取部分內容。

## 驗證與貢獻

執行 `python -m unittest discover -s tests -v` 與 `cs-study-map validate --tracked`。請以 Issue 回報錯誤；PR 可改善程式、映射與人工修正規則，詳見[貢獻說明](../../CONTRIBUTING.md)。

原創程式、教材文字與維護文件採 MIT 授權；不改變來源材料的權利，詳見[來源與授權](../../ATTRIBUTION.md)。

早期成果：[總知識圖與 60 份課程指南](../early-work/index.md)，另含分類總覽及教材 README；既有文件已保留學習內容、移除本地絕對路徑後補錄至 Git。
