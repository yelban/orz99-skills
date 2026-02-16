# orz99-skills

Yelban's collection of Claude Code / Codex skills.

## Installation

```bash
# List available skills
npx skills add yelban/orz99-skills --list

# Install specific skill
npx skills add yelban/orz99-skills -s good-writing-zh

# Install all skills
npx skills add yelban/orz99-skills --all

# Global install (recommended)
npx skills add yelban/orz99-skills -s good-writing-zh -g
```

## Available Skills

### good-writing-zh

中文好寫作指南：提升中文寫作品質與改寫既有文章。

基於 Paul Graham〈Good Writing〉，融合余光中、王鼎鈞的中文寫作智慧。

**Triggers:**
- `/good-writing`、`/潤稿`
- 「幫我潤稿」「改寫這段」「讓文字更順」
- 「寫好一點」「高品質中文」

**Features:**
- 量化節奏規則：氣口（標點間 ≤ 20 字）、錯落（相鄰句長差 > 5 字）、句尾類型控制
- 5 項改寫技法：刪贅字、拆長句、砍開頭、還原強動詞（余光中去名詞化理論）
- CoT 改寫流程：`<diagnosis>` → `<planning>` → `<rewrite>`，確保改寫全面一致
- 10+ 組 before/after 範例驅動 in-context learning
- 7 項檢查清單（30 字軟限制，排比句/條件句可豁免）
- 與 humanizer-tw 明確分工：先去機器味，再打磨節奏

### humanizer-tw

去除中文文字中的 AI 生成痕跡，使文字更自然、更有人味、更像台灣人寫的。

針對中文 AI 寫作的獨特問題設計：時代開場白、連接詞濫用、互聯網黑話、翻譯腔、書面語過重、公式化結構、結尾套話、中國用語滲入。

**Triggers:**
- 「去除 AI 痕跡」「人性化」「humanize」
- 編輯或審閱文字

**Features:**
- 刪除開場套話：「隨著...的發展」「眾所周知」
- 減少連接詞：「此外」「與此同時」
- 替換互聯網黑話：「賦能」→「幫助」、「痛點」→「問題」
- 修正翻譯腔：連續「的」字拆開
- 口語化：「予以」→「給」、「該」→「這個」
- 攔截中國用語：「信息」→「資訊」、「視頻」→「影片」、「數據」→「資料」

### codex-plan

Claude Opus 擔任 PM 釐清需求、定位檔案，再交由 Codex 5.3（xhigh reasoning）生成結構化實作計畫。

**Triggers:**
- `/codex-plan <what you want to plan>`

**Features:**
- 動態釐清問題（1-5 題，依任務複雜度調整）
- Fast-path：極簡任務跳過 Codex，Opus 直接產計畫
- PM/Locator 角色分工：Opus 找檔案路徑，Codex 深度推理寫計畫
- Target Files 交接：精確傳遞檔案清單給 Codex，避免盲讀
- 品質閘門（Step 6）：自動檢查產出結構，失敗重試一次
- Mermaid 依賴圖：機器可解析的任務依賴 DAG
- 反碎片化：防止 Codex 過度拆分微型 Task

**Behavioral Constraints（[測試報告](./docs/codex-plan-constraints-benchmark.md)）：**
- 防 scope drift — 只做被要求的事，簡單任務計畫可壓到 17 行
- 精確上下文載入 — 從 Target Files 開始讀，再展開到相依檔案
- 控制輸出格式 — bullet point 為主，避免冗長敘述
- 精簡推理摘要 — `model_reasoning_summary=concise` 省 ~30% token

### project-profiler (v2.0)

為任意 git 專案生成 LLM 專用側寫文件（`docs/{project-name}.md`）。

不把整包程式碼塞給大模型，而是透過 Map-Reduce pipeline 將專案「語意壓縮」成帶有架構判斷的高密度上下文——400k tokens 的 codebase 壓成 5k tokens 的側寫，讓未來的 LLM 拿到的是心智模型，不是原始碼搜尋結果。

讀者是未來在不同對話中接觸此專案的 LLM，需快速理解：核心抽象是什麼？架構怎麼設計？用了哪些技術棧？加功能動哪些模組？關鍵設計決策及 trade-off？

**Triggers:**
- `/project-profiler`
- 「profile this project」「為專案建側寫」

**Pipeline:**
- 6-phase 工作流：掃描 → 社群資料 → 平行 subagent 分析 → 條件式區塊偵測 → 合成 → 品質閘門
- 小專案（≤80k tokens）direct mode：跳過 subagent，Opus 直讀
- 大專案自動分配 2-3 個 Sonnet subagent 平行分析（A: Core+Design, B: Architecture+Patterns, C: Usage+Deployment）
- Monorepo 感知：偵測 workspace 後按 package 垂直分派，不切碎子專案

**Scanner:**
- `--format summary` 預設輸出（壓縮 context token，大專案省 2 萬+ tokens）
- 自動偵測 conditional sections（從依賴清單 + 檔案存在判斷，取代舊版 grep 全專案）
- Monorepo workspace 偵測（pnpm / npm workspaces / lerna / Cargo workspace / Go workspace）
- 技術棧偵測：Node / Python / Rust / Go / Java / C# / PHP
- `.ipynb` 解析（只取 source cells，濾除 output）

**Output:**
- 10 章節模板（含 Section 8.5 Code Quality & Patterns）+ 6 條件式區塊
- Mermaid 圖表 + 結構化依賴清單雙格式並列（人類可讀 + LLM 可解析）
- Core Abstractions 限制 10-15 個（按 fan-in 排序，避免 token 污染）
- 證據格式 `file:SymbolName`（符號名穩定，不會因下次 commit 失效）

**品質閘門:**
- 中英文雙語禁主觀語言（22 英文 + 14 中文禁詞）
- 數字必須 from code、符號驗證、結構驗證
- 4 核心問題測試 + 證據稽核

## License

MIT
