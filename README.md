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
- 字數節奏：三字穩、四字順、五字緩、七字長
- 改寫技法：刪贅字、拆長句、砍開頭
- 自動檢查清單

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

使用 Codex 5.3（xhigh reasoning）建立詳細實作計畫。

**Triggers:**
- `/codex-plan <what you want to plan>`

**Features:**
- 自動詢問釐清問題（3-6 題）
- 使用 gpt-5.3-codex 模型 + xhigh 推理
- 輸出結構化計畫含 Phase/Task/依賴/測試策略

**Behavioral Constraints（[測試報告](https://skills.orz99.com/view/codex-plan-constraints-benchmark)）：**
- 防 scope drift — 只做被要求的事，簡單任務計畫可壓到 17 行
- 強制先讀 codebase — 先讀完相關檔案再寫計畫，輸出貼合現有架構
- 控制輸出格式 — bullet point 為主，避免冗長敘述
- 精簡推理摘要 — `model_reasoning_summary=concise` 省 ~30% token

## License

MIT
