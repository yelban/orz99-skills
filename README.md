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
- **v1.1.0 保守模式（conservative）**：處理 README / API 文件 / CLI 說明時只改 4 類（刪連續「的」、刪「進行/加以/實施」、拆 30+ 字句、修氣口），停用錯落與公式化打破規則；新增術語連綴例外清單（頓號列表、破折號引介、括號補充、連字符連綴視為已有內部停頓），保留程式碼區塊、表格、英文術語、YAML front matter 原樣

### humanizer-tw

去除中文文字中的 AI 生成痕跡，使文字更自然、更有人味、更像台灣人寫的。

針對中文 AI 寫作的獨特問題設計：時代開場白、連接詞濫用、互聯網黑話、翻譯腔、書面語過重、公式化結構、結尾套話、中式 AI 句型、中國用語滲入。

**Triggers:**
- 「去除 AI 痕跡」「人性化」「humanize」
- 編輯或審閱文字
- fork 簡中專案的繁中校對、OpenCC 轉換後清洗（v1.1.0）

**Features:**
- Hub-and-Spoke 架構：SKILL.md 127 行精簡核心 + 4 個 reference 檔（dictionary / anti-patterns / examples / opencc-residuals）
- CoT 改寫流程：`<diagnosis>` → `<rewrite>` → `<changelog>`，防堵漏改
- 文體感知：正式文體自動停用「個性注入」和「口語化」，避免語氣災難
- 10 類 AI 寫作問題分類，含「中式 AI 句型」（進行了一個...的優化、起到了...的作用）
- 刪除開場套話：「隨著...的發展」「眾所周知」
- 替換互聯網黑話：「賦能」→「幫助」、「痛點」→「問題」、「底層邏輯」→「核心原理」
- 攔截中國用語：「信息」→「資訊」、「視頻」→「影片」、「默認」→「預設」
- 與 good-writing-zh 明確分工：先去 AI 毒，再打磨節奏
- **v1.1.0 OpenCC 轉換後清洗**：新增 `references/opencc-residuals.md`——涵蓋 30+ 條 OpenCC s2twp 漏網詞（聚類→分群、構建→建構、鏈路→流程、PyPI 包→套件、後臺→背景、源位置→來源位置、快取項→快取項目、命令[CLI]→指令、註釋→註解）、動詞語境誤譯（connect→串連 vs 連線、run→執行、configure→設定）、半形→全形標點規則、錯字表（併↔並）、grep 快速檢查指令

### codex-plan

Claude Opus 擔任 PM 釐清需求、定位檔案，再交由 GPT-5.4（xhigh reasoning）生成結構化實作計畫。

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

### plan-review

互動式計畫審查：在實作前檢視計畫的完整性、方向、風險與範圍。

適用 codex-plan 產出、plan mode 計畫、或任何實作計畫文件。審查計畫本身（任務拆解是否合理），不是 code review。

**Triggers:**
- `/plan-review [plan file path]`
- 自動偵測 `codex-plan.md` 或 `.claude/plans/` 最新檔案

**Features:**
- 4 維度逐段審查：完整性 → 方向性 → 風險 → 範圍
- 每段用 AskUserQuestion 互動確認，不會一路衝到底
- 方向性審查強制檢查：現有程式碼是否已能解決問題？避免過度工程陷阱
- 主動建議補上「NOT in scope」清單，防止實作時 scope creep
- 深度/快速兩種模式（每段 4 題 vs 1 題）
- 結構化議題格式：編號 + 選項字母 + 影響/風險/成本矩陣
- 審查結束產出決策摘要表 + 建議修訂清單

### cine-shot

電影感 AI 繪圖提示詞生成器。根據場景描述自動選配攝影機模組與光影預設，產出 Midjourney + Gemini 3 Pro 雙平台 prompt。

**Triggers:**
- `/cine-shot <scene description>`
- 「cinematic prompt」「電影感提示詞」

**Features:**
- 核心公式：Subject & Action + Setting & Framing + Camera Module + Lighting & Vibe + Platform Params
- 3 組攝影機模組：ARRI（寫實/敘事）、RED（史詩/科幻）、Sony（銳利/賽博）
- 6 組光影預設：Golden Hour / Cold Noir / Neon Cyber / Natural Doc / Desolate / Dramatic
- 雙平台輸出：Midjourney（`--ar --style raw --v 7`）+ Gemini 3 Pro（純描述語句）
- 禁止空洞修飾詞（beautiful, masterpiece, stunning 等），只用具體視覺描述
- AskUserQuestion 互動確認氛圍、構圖、比例

### system-audit

掃描 CLAUDE.md、MEMORY.md 與所有已安裝 skills，找出冗餘指令、臃腫內容、重疊範圍與 token 浪費。

**Triggers:**
- `/system-audit [focus]`
- focus 可選：`all`（預設）、`claude`、`memory`、`skills`

**Features:**
- CLAUDE.md 審查：冗餘指令、臃腫範例、過時內容、跨檔重複
- MEMORY.md 審查：過時條目、與 CLAUDE.md 重複、接近行數上限
- Skills 審查：行數 / token 估算總覽、範圍重疊偵測、結構問題
- Token 預算概覽：每次對話載入量 vs 按需載入量
- 互動式清理：multiSelect 勾選要執行的清理項目，確認後才動手

### reflect

對話結束前的結構化反思。回顧本次對話，萃取值得長期保留的知識。

**Triggers:**
- `/reflect`
- 「反思」「回顧對話」「conversation review」

**Features:**
- 自動掃描對話中的任務、錯誤、使用者回饋
- 萃取技術發現、模式識別、錯誤根因、使用者偏好
- 識別新 skill 機會、現有 skill 改進點
- 互動式執行：勾選要寫入 memory / 改進 skill / 建新 skill 的項目
- 先查 MEMORY.md 避免重複記錄

### code-review

互動式程式碼審查：逐段檢視架構、程式品質、測試、效能。

可審查 git diff、指定檔案、或整個 PR。審查已寫好的程式碼，不是計畫審查。

**Triggers:**
- `/code-review [file path, PR number, or 'diff']`
- 預設審查所有未提交變更

**Features:**
- 4 維度逐段審查：架構 → 程式品質 → 測試 → 效能
- 每段用 AskUserQuestion 互動確認，不會一路衝到底
- 積極標記 DRY 違規（即使只重複兩次）
- 檢查 N+1 查詢、記憶體問題、快取機會、演算法複雜度
- 測試覆蓋：邊界案例、失敗路徑、斷言強度
- 深度/快速兩種模式（每段 4 題 vs 1 題）
- 結構化議題格式：編號 + 選項字母 + 成本/風險/影響/維護矩陣
- 審查結束產出待修項目清單（含 `file:line`），全部 LGTM 時直接通過

### codex-review

跨模型對抗式審查：用 GPT-5.4 審查 Claude 的計畫或程式碼產出。

異質模型產生真正的對抗張力，能抓到同模型自審遺漏的問題（如 auth 漏洞、shell quoting bug、schema 衝突）。與 plan-review / code-review 互補——那兩個是 Claude 同模型互動審查，這個是跨模型自動審查。

**Triggers:**
- `/codex-review [plan file, code file, PR#, or 'diff']`
- 自動偵測計畫（codex-plan.md / .claude/plans/）或程式碼（diff / 檔案）

**Features:**
- 自動偵測 plan mode 或 code mode，無需手動指定
- VERDICT 迴圈：Codex 審查 → APPROVED/REVISE → Claude 修訂 → 再審（最多 3 輪）
- 嚴重度分級：HIGH / MEDIUM / LOW，APPROVED 門檻 = 0 HIGH + ≤1 MEDIUM
- Codex read-only sandbox：審查者不改檔案，純分析
- 全面 / 聚焦兩種模式（security / concurrency / schema / performance）
- 3 組 prompt template：Plan Review / Code Review / Continuation（Round 2+）
- 結構化輸出：輪次摘要表 + issues 清單 + 建議行動
- 第一輪即 APPROVED → 簡化輸出 LGTM（跨模型確認）

**建議使用順序：**
1. `/codex-plan` → 2. `/codex-review` → 3. 實作 → 4. `/codex-review diff` → 5. `/code-review`

### fable-explore

寓言探索法：用故事學會任何領域的概念。從指定領域選一個概念，寫一篇文學寓言間接傳達（揭曉在結尾才浮現），再附上清楚的解釋。6 個難度級距，用自然語言描述即可。

靈感來源：Amanda Askell（Anthropic），2026 年 4 月 Newcomer Pod 訪談。

**Triggers:**
- `/fable-explore <領域>`、`/寓言`、`/探索`
- 「用寓言教我」「fable explore」「tell me a fable about」
- 「再一個」「another」延續同一領域

**難度級距（用描述的，不用記參數）：**

| 級距 | 怎麼說 | 概念來源 |
|------|--------|---------|
| 國小高年級 | 「小學程度」「簡單一點」「給小孩聽的」 | 日常現象背後的「為什麼」 |
| 國中 | 「國中程度」「入門」 | 課本提到但不深究的概念 |
| 高中 | 「高中程度」「基礎」 | 開始有點反直覺的概念 |
| 大學入門 | 「大學程度」 | 大學入門課最反直覺的概念 |
| 研究所（預設） | 不指定難度時 | 大學畢業生也不一定熟悉 |
| 專家級 | 「專家」「最難的」 | 該領域專家才知道的概念 |

**互動模式：**

| 關鍵字 | 功能 |
|--------|------|
| 「三篇」「批次」或 `-3` | 連續 3 篇不同子領域 |
| 「互動」「讓我猜」或 `-i` | 先讀故事，猜完再揭曉 |
| 「選擇題」「考我」或 `-g` | 寓言後四選一 |
| 「跨域」或 `-x` + 兩個領域 | 找結構相似概念 + 映射 |
| `-s <風格>` | 莊子 / sci-fi / aesop / detective |

**範例：**

```
/fable-explore 量子力學                     ← 預設（研究所程度）
/fable-explore 用國小程度教我天文學           ← 國小高年級
/fable-explore 國中程度的化學                ← 國中
/fable-explore 高中程度的經濟學              ← 高中
/fable-explore 最難的賽局理論                ← 專家級
/fable-explore 國中程度的物理，讓我猜         ← 難度 + 互動
/fable-explore 簡單一點的生物學，三篇         ← 難度 + 批次
/fable-explore -x 熱力學 資訊理論            ← 跨域
/fable-explore -s 莊子 神經科學              ← 指定風格
```

### fable-econ

Amanda Askell 原版經濟學寓言提示詞（2025 年 3 月）。嚴格 3 段故事 + 1 段揭曉的固定結構，專注於經濟學。

來源：Amanda Askell，2025 年 3 月 9 日 X 貼文。

**Triggers:**
- `/fable-econ [子領域]`、`/經濟寓言`
- 「economics fable」「經濟學寓言」

**Features:**
- 忠實重現 Amanda 原版提示詞結構
- 概念難度：大學部低年級沒聽過，研究所後期會接觸到
- 嚴格 3 段故事（場景建立 → 深入展開 → 推向結局），全程不提術語
- 1 段揭曉（原理名稱 + 解釋 + 故事對映）
- `-3` 批次模式、`-i` 互動模式
- 可指定子領域（拍賣理論、公共財、勞動經濟學等）

**與 fable-explore 的差異：**

| | fable-econ | fable-explore |
|--|-----------|---------------|
| 領域 | 僅經濟學 | 任何領域 |
| 結構 | 嚴格 3 段 + 1 段 | 自由長度寓言 + 解釋段 |
| 來源 | 2025.3 原版提示詞 | 2026.4 訪談通用版 |

## License

MIT
