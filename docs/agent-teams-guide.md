# Claude Code Agent Teams 完全指南

本文整合自兩篇 X 推文，涵蓋技術原理與實戰應用：

- **Daniel San** ([@dani_avila7](https://x.com/dani_avila7/status/2020170608290549906))：技術深入，講運作原理、CLAUDE.md 的重要性、三大核心規則
- **J.B.** ([@VibeMarketer_](https://x.com/VibeMarketer_/status/2020142441769156678))：應用導向，行銷場景實戰、操作步驟、避坑指南

---

## 1. 什麼是 Agent Teams

Agent Teams 是 Claude Code 的實驗性功能，讓你同時運行多個 Claude 實例協同工作。不是 prompt 技巧，而是一套全新的多 agent 協作架構：一個 lead（領導者）負責協調，多個 teammates（隊友）平行執行任務，彼此之間能即時溝通。

與 subagent 不同的是，teammates 不只是回報結果——他們可以互相傳訊、挑戰彼此的結論、在對方的發現基礎上繼續推進。這種協作能力才是真正的突破點。

![](images/HAjrA4LW0AA_xWa.jpg)

![](images/HAkWHTGW0AElU6L.jpg)

---

## 2. 啟用方式

### 設定 settings.json

在 Claude Code 的 `settings.json` 加入以下設定即可啟用，不需要額外安裝任何東西：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

![](images/HAhaWXbXwAAh3Yf.png)

### 操作步驟

1. **用自然語言描述任務並要求建立團隊**——要明確指定角色分工。

   > "one teammate on X, one on Y, one playing devil's advocate"

   > 🔄 「一個隊友負責 X，一個負責 Y，一個扮演魔鬼代言人」

   這樣具體的指令才有效。像「make a team to help with marketing」這種模糊描述效果不好。

   另一個範例——直接描述任務並要求按檔案拆分：

   > "I need to remove all debug console.log statements from docs/js/. Create an agent team, split by file ownership so nobody edits the same file."

   > 🔄 「我需要移除 docs/js/ 裡所有的 debug console.log。建立一個 agent team，按檔案所有權拆分，確保沒人編輯同一個檔案。」

2. **Claude 自動建立團隊**——它會拆分工作為任務、生成 teammates、協調所有流程。

3. **觀察 teammates 在 statusline 出現**——你可以在主控台看到所有 teammates 同時在不同檔案上工作。

4. **透過共享任務清單追蹤進度**——lead 建立任務，teammates 認領執行，隨時可用 `Ctrl+T` 查看狀態。

5. **需要時直接與 teammates 對話**——用 `Shift+Up/Down` 選擇特定 teammate 直接溝通，不必經過 lead 中轉。

6. **讓 teammates 辯論**——當你指示他們「challenge each other」或「debate」，他們真的會這麼做。別急著消除摩擦，洞見往往就藏在衝突中。

---

## 3. 運作原理

使用一段時間後，幾件事會變得很明顯：

- **每個 teammate 運行在獨立的 context window 中**——彼此看不到對方的對話歷史。
- **沒有共享的對話記錄**——teammates 不會繼承 lead 的對話內容。
- **所有 teammates 自動載入 CLAUDE.md**——同時也會載入 skills、MCP servers 等專案設定。
- **溝通透過 messages + 共享任務清單進行**——不靠對話，靠結構化的訊息傳遞。

所以協調不是來自對話，而是來自**結構**。這就是為什麼 CLAUDE.md 至關重要——它是所有 teammates 唯一的共享 runtime context。

**任務相依性自動運作**：當一個 teammate 完成其他人依賴的任務時，被阻塞的任務會自動解除封鎖。

---

## 4. 三大核心規則

### 規則 1：描述模組邊界，讓 lead 能聰明地拆分工作

當你要求建立 agent team 時，Claude Code 會讀取 CLAUDE.md 來決定如何將檔案分配給各個 teammates。模組邊界寫得越清楚，拆分就越聰明。

![](images/HAkMHg9WEAAe4BO.jpg)

實測中，Daniel San 告訴 Claude Code：

> "there are console.log across files in docs/js/, create a team and split by file ownership."

> 🔄 「docs/js/ 裡的多個檔案散佈著 console.log，建立一個 team 並按檔案所有權拆分。」

Claude Code 讀取了專案結構，為每個 teammate 分配了明確的檔案清單，在 9 個檔案上完成任務且零衝突。它能做出這樣的拆分，是因為它理解了哪些檔案是獨立的。

### 規則 2：保持專案上下文精簡且可操作

每個 teammate 啟動時都會載入你的 CLAUDE.md，但他們不會繼承 lead 的對話。如果 CLAUDE.md 內容模糊，每個 teammate 都會浪費 token 獨立重新探索整個 codebase。

![](images/HAkJ3gjXUAATiee.png)

在 Daniel San 的測試中，沒有任何 teammate 向 lead 詢問專案是什麼或檔案在哪裡——他們全都從 CLAUDE.md 取得了這些資訊。三個 teammates 同時載入上下文，如果需要探索而非快速讀取，token 成本就是三倍。

### 規則 3：定義「驗證完成」的標準

當 Claude Code 知道「通過」長什麼樣子時，它會在每個任務中加入驗證步驟。如果 CLAUDE.md 列出了檢查方法，teammates 就會用這些訊號來確認自己的工作成果。

![](images/HAkLn-GXkAAUb1D.jpg)

在清理 console.log 的任務中，teammates 使用 grep 自我驗證，因為任務目標就是移除 console.log。Claude Code 為任務選擇了正確的檢查方式。但在 CLAUDE.md 中定義專案層級的驗收標準，能讓 lead 有一套「完成」的詞彙，並針對每個任務自動調整。

實際上，每個 teammate 都精確回報了自己做了什麼。不需要 lead 介入，規則清楚輸入、報告清楚輸出。

---

## 5. 實戰應用：行銷場景

### Campaign Research Sprint（行銷活動研究衝刺）

> "create an agent team to research the launch strategy for [product]. spawn three teammates: one on competitor ad analysis, one on customer voice mining from reviews and reddit, one stress-testing our current positioning against what they find. have them share findings and challenge each other."

> 🔄 「建立一個 agent team 來研究 [產品] 的上市策略。生成三個隊友：一個做競品廣告分析，一個從評論和 Reddit 挖掘客戶心聲，一個用他們的發現來壓力測試我們目前的定位。讓他們分享發現並互相挑戰。」

三人同時工作。當競品研究員發現市場缺口時，定位隊友會壓力測試我們是否真能佔據這個缺口；客戶心聲隊友則驗證真實買家是否在乎。最後由 lead 整合成策略文件。

### Landing Page Builds（著陸頁建置）

> "create an agent team to build the landing page for [offer]. one teammate on copy and messaging, one on conversion structure and CRO, one running adversarial review as a skeptical buyer. require plan approval before any implementation."

> 🔄 「建立一個 agent team 來製作 [方案] 的著陸頁。一個隊友負責文案與訊息傳達，一個負責轉換結構和 CRO，一個以懷疑型買家的角度做對抗性審查。要求在執行前先批准計畫。」

計畫審批機制是關鍵——每個 teammate 必須先概述方案再執行。lead 審核後批准或退回修改，在浪費工時前就攔截錯誤方向。

### Ad Creative Exploration（廣告創意探索）

> "spawn 4 teammates to explore different hook angles for [product]. have them each develop one direction, then debate which is strongest. update findings doc with consensus."

> 🔄 「生成 4 個隊友，為 [產品] 探索不同的 hook 角度。讓他們各自發展一個方向，然後辯論哪個最強。將共識更新到發現文件中。」

辯論結構是秘密武器。一個 agent 獨自探索容易錨定在第一個還不錯的想法上。四個 agent 積極嘗試推翻彼此？存活下來的角度才是真正經過實戰考驗的。

### Content Production（內容生產）

> "create a team for this week's content. one teammate on search intent and competitive gaps, one drafting based on findings, one running the recursive quality loop on every piece before it ships."

> 🔄 「為本週的內容建立一個 team。一個隊友負責搜尋意圖與競品缺口分析，一個根據發現撰寫初稿，一個在每篇內容發布前運行遞迴品質檢查。」

平行處理取代序列瓶頸。研究與產出同時進行，品質管控內建其中。

---

## 6. 操作技巧

### 快捷鍵

| 快捷鍵 | 功能 |
|--------|------|
| `Shift+Tab` | 進入 delegate mode，讓 lead 只負責協調，不自己動手做 |
| `Shift+Up/Down` | 選擇特定 teammate 直接對話 |
| `Ctrl+T` | 查看共享任務清單狀態 |

### 善用 Plan Mode

Plan mode 在每一輪都會被評估，不是只在一開始。

![](images/HAkMhpPWYAA26u6.jpg)

這讓它特別適合用於：

- **設計專屬角色**——只做規劃不做執行
- **初期任務塑形**——釐清方向後再交給執行者

執行工作時，用預設模式生成新的 teammate 更能保持流暢。一旦 agent 建立，其模式在整個生命週期內固定不變。

### 要求計畫審批

在高風險工作中，加入 plan approval 機制：

> "require plan approval before they make any changes"

> 🔄 「要求在做任何更改前先批准計畫」

每個 teammate 先概述方案，lead 審核通過才能開始執行。感覺更慢，但能在浪費工時前就擋下錯誤方向。

### 讓 Teammates 辯論

指示 teammates 互相挑戰和辯論，別急著平息分歧。一個 agent 容易錨定在第一個想法，多個 agent 互相質疑才能找到真正經得起考驗的答案。

### 指定模型控制成本

> "use sonnet for each teammate"

> 🔄 「每個隊友使用 sonnet 模型」

可以為 teammates 指定較便宜的模型來管理成本。

---

## 7. 常見錯誤與注意事項

### 不要犯的錯

- **別用在簡單任務上**——單一產出、快速文案修改、序列性工作，用一個 session 就好。協調成本不划算。
- **別讓 teammates 編輯同一個檔案**——兩個 agent 同時寫入同一個檔案會互相覆寫。拆分工作，讓每個人擁有不同的檔案。
- **別生成太多 teammates**——3 到 5 個通常剛好。超過這個數量，協調成本會反噬。
- **別忘記 context**——teammates 不會繼承 lead 的對話歷史。在生成指令中包含相關上下文，或確保 CLAUDE.md 夠完善。
- **別跳過複雜工作的計畫審批**——感覺更慢，但能在浪費 token 前擋下錯誤方向。

### 要注意的事

- **Token 用量隨團隊規模增長**——每個 teammate 是獨立的 Claude 實例。複雜工作值得，簡單任務就過度了。
- **關閉可能比較慢**——teammates 會完成目前的工作才停止。
- **透過 lead 收尾**——結束時告訴 lead 進行清理，不要讓 teammates 各自收尾，可能會留下不一致的狀態。
- **別放任太久不管**——定期檢查、重新導向、即時整合。放著不管越久，浪費工作的風險越高。

---

## 8. 總結

Agent Teams 在以下條件下效果最好：

- 每個 agent 擁有**清楚的負責範圍**
- 溝通是**結構化的**，不是對話式的
- CLAUDE.md 被當作**共享的 runtime context** 來維護

這仍是實驗性功能，但一旦你理解了團隊實際的執行與溝通方式，它就不再像是「多個 agents 各自為政」，而更像一個**平行運行的協調系統**。

對於任何需要平行研究、多元觀點、內建壓力測試的工作——Agent Teams 帶來的效益是倍數級的。
