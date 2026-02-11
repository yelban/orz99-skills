# Claude Code Agent Teams 完全指南

這篇整合了兩則 X 推文，角度剛好互補：

- **Daniel San** ([@dani_avila7](https://x.com/dani_avila7/status/2020170608290549906))——拆解運作原理，講 CLAUDE.md 為什麼是靈魂，歸納三條規則
- **J.B.** ([@VibeMarketer_](https://x.com/VibeMarketer_/status/2020142441769156678))——行銷人視角，四種實戰場景、操作步驟、踩過的坑

---

## 1. 什麼是 Agent Teams

Claude Code 的實驗性功能。你可以同時跑多個 Claude 實例，讓它們協同工作。

一個 lead（領導者）負責調度，多個 teammates（隊友）平行執行，彼此即時溝通。不是什麼 prompt 技巧——是一整套多 agent 協作架構。

跟 subagent 差很多。subagent 做完回報就結束了，teammates 會互相傳訊、挑戰對方結論、接著對方的發現繼續往下做。差別在這裡。

![](images/HAjrA4LW0AA_xWa.jpg)

![](images/HAkWHTGW0AElU6L.jpg)

---

## 2. 啟用方式

### 設定 settings.json

在 `settings.json` 加一行，不用裝別的東西：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

![](images/HAhaWXbXwAAh3Yf.png)

### 操作步驟

1. **用自然語言描述任務，要求建立團隊**——角色分工要講清楚。

   > "one teammate on X, one on Y, one playing devil's advocate"

   > 🔄 「一個隊友負責 X，一個負責 Y，一個扮演魔鬼代言人」

   這種程度的具體才有用。「make a team to help with marketing」太模糊，出來的東西不會好。

   再一個範例——直接講任務，要求按檔案拆分：

   > "I need to remove all debug console.log statements from docs/js/. Create an agent team, split by file ownership so nobody edits the same file."

   > 🔄 「我需要移除 docs/js/ 裡所有的 debug console.log。建立一個 agent team，按檔案所有權拆分，確保沒人編輯同一個檔案。」

2. **Claude 自動組隊**——把工作拆成任務、生成 teammates、協調流程，你不用手動設定。

3. **看 statusline**——teammates 會陸續出現，主控台可以看到它們同時在不同檔案上動工。

4. **共享任務清單追蹤進度**——lead 開任務，teammates 認領，`Ctrl+T` 隨時看狀態。

5. **直接跟 teammates 講話**——`Shift+Up/Down` 選人，不必透過 lead 轉達。

6. **讓它們吵**——你說「challenge each other」或「debate」，它們真的會吵。別急著消除摩擦，好東西往往吵出來的。

---

## 3. 運作原理

用一陣子之後，你會注意到：

- **每個 teammate 各有獨立 context window**——看不到彼此的對話歷史。
- **對話記錄不共享**——teammates 不知道 lead 跟你聊了什麼。
- **所有 teammates 自動載入 CLAUDE.md**——skills、MCP servers 這些專案設定也會載。
- **溝通靠 messages + 共享任務清單**——不是聊天，是結構化訊息。

重點來了：協調靠**結構**，不靠對話。CLAUDE.md 是所有 teammates 唯一共享的 runtime context，寫得好不好直接決定團隊表現。

另外，任務有相依性的話會自動處理——A 完成後，被 A 擋住的 B 自動解鎖，不用你盯。

---

## 4. 三大核心規則

### 規則 1：描述模組邊界，讓 lead 拆得漂亮

建 agent team 時，Claude Code 讀 CLAUDE.md 決定怎麼分工。你的模組邊界寫得越清楚，它拆得越聰明。

![](images/HAkMHg9WEAAe4BO.jpg)

Daniel San 實測時跟 Claude Code 說：

> "there are console.log across files in docs/js/, create a team and split by file ownership."

> 🔄 「docs/js/ 裡的多個檔案散佈著 console.log，建立一個 team 並按檔案所有權拆分。」

結果：Claude Code 讀完專案結構，給每個 teammate 分了明確的檔案清單。9 個檔案，零衝突。它拆得準，因為它讀懂了哪些檔案彼此獨立。

### 規則 2：CLAUDE.md 要精簡、能直接用

每個 teammate 啟動時會載入 CLAUDE.md，但不知道 lead 跟你的對話。CLAUDE.md 寫得含糊，每個 teammate 就得自己花 token 去探索 codebase——三個 teammates 就是三倍浪費。

![](images/HAkJ3gjXUAATiee.png)

Daniel San 的測試裡，沒有任何 teammate 回頭問 lead「這專案在幹嘛」「檔案在哪」——全從 CLAUDE.md 拿到了。寫好 CLAUDE.md 就是在省錢。

### 規則 3：定義「做完」長什麼樣

Claude Code 知道怎樣算通過，就會在任務裡加驗證步驟。你在 CLAUDE.md 寫好檢查方法，teammates 自己會拿來驗收。

![](images/HAkLn-GXkAAUb1D.jpg)

清 console.log 那次，teammates 自己跑 grep 驗證——目標明確，驗證手段也就跟著明確。CLAUDE.md 裡定義好驗收標準，等於給 lead 一套「完成」的語言，它會針對不同任務自動調整用法。

每個 teammate 做完都精確回報了做了什麼。不用 lead 追。規則清楚進，報告清楚出。

---

## 5. 實戰應用：行銷場景

### Campaign Research Sprint（行銷活動研究衝刺）

> "create an agent team to research the launch strategy for [product]. spawn three teammates: one on competitor ad analysis, one on customer voice mining from reviews and reddit, one stress-testing our current positioning against what they find. have them share findings and challenge each other."

> 🔄 「建立一個 agent team 來研究 [產品] 的上市策略。生成三個隊友：一個做競品廣告分析，一個從評論和 Reddit 挖掘客戶心聲，一個用他們的發現來壓力測試我們目前的定位。讓他們分享發現並互相挑戰。」

三人同時跑。競品那邊發現市場缺口，定位隊友馬上測能不能佔住；客戶心聲隊友去看真實買家到底在不在乎。lead 收尾整合成一份策略文件。

### Landing Page Builds（著陸頁建置）

> "create an agent team to build the landing page for [offer]. one teammate on copy and messaging, one on conversion structure and CRO, one running adversarial review as a skeptical buyer. require plan approval before any implementation."

> 🔄 「建立一個 agent team 來製作 [方案] 的著陸頁。一個隊友負責文案與訊息傳達，一個負責轉換結構和 CRO，一個以懷疑型買家的角度做對抗性審查。要求在執行前先批准計畫。」

這裡的重點是 plan approval——每個 teammate 先講打算怎麼做，lead 點頭了才動手。方向錯了當場退回，不會做完才發現白忙。

### Ad Creative Exploration（廣告創意探索）

> "spawn 4 teammates to explore different hook angles for [product]. have them each develop one direction, then debate which is strongest. update findings doc with consensus."

> 🔄 「生成 4 個隊友，為 [產品] 探索不同的 hook 角度。讓他們各自發展一個方向，然後辯論哪個最強。將共識更新到發現文件中。」

一個 agent 自己想，很容易抓到第一個還行的點子就不放了。四個 agent 互相挑毛病？活下來的那個角度，是真的禁得起打。

### Content Production（內容生產）

> "create a team for this week's content. one teammate on search intent and competitive gaps, one drafting based on findings, one running the recursive quality loop on every piece before it ships."

> 🔄 「為本週的內容建立一個 team。一個隊友負責搜尋意圖與競品缺口分析，一個根據發現撰寫初稿，一個在每篇內容發布前運行遞迴品質檢查。」

不再是研究做完才寫、寫完才審。三件事同時跑，QA 從頭到尾都在。

---

## 6. 操作技巧

### 快捷鍵

| 快捷鍵 | 功能 |
|--------|------|
| `Shift+Tab` | delegate mode——lead 只調度不動手 |
| `Shift+Up/Down` | 選 teammate 直接對話 |
| `Ctrl+T` | 看任務清單 |

### Plan Mode 的妙用

Plan mode 每一輪都會重新評估，不是設一次就定了。

![](images/HAkMhpPWYAA26u6.jpg)

很適合拿來做：

- **純設計角色**——只規劃不執行
- **前期任務塑形**——想清楚再交給別人做

要做事的 teammate 就用預設模式生成，跑起來比較順。agent 建立後模式就固定了，沒辦法中途切換。

### 要求計畫審批

高風險工作記得加 plan approval：

> "require plan approval before they make any changes"

> 🔄 「要求在做任何更改前先批准計畫」

teammate 先講方案，lead 同意才動手。多花幾分鐘審，能省幾小時重做。

### 讓 Teammates 吵架

前面提過，值得再強調：叫它們「challenge each other」或「debate」，它們會認真吵。別怕衝突，一個人想容易卡死，一群人吵反而吵出好東西。

### 指定模型省錢

> "use sonnet for each teammate"

> 🔄 「每個隊友使用 sonnet 模型」

不是每個 teammate 都需要最強模型。簡單任務用 Sonnet，省下來的 token 拿去做更重要的事。

---

## 7. 常見錯誤與注意事項

### 別踩的坑

- **簡單任務別用 Agent Teams**——一個 session 能搞定的事，開團隊就是浪費。協調成本比你想的高。
- **別讓 teammates 碰同一個檔案**——兩個 agent 同時寫，互相覆寫，白做工。一人一份，不要重疊。
- **teammates 別開太多**——3 到 5 個最順。再多，光是協調就消耗掉增加的產能。
- **context 要給夠**——teammates 不知道你跟 lead 聊了什麼。生成指令裡該帶的背景要帶，CLAUDE.md 該寫的要寫。
- **複雜工作別跳過 plan approval**——多花一點時間審方案，少花很多時間返工。

### 留意的地方

- **Token 吃很兇**——每個 teammate 是獨立 Claude 實例。值不值得開團隊，先想一下。
- **關閉不是即時的**——teammates 會把手上的事做完才停，急不來。
- **收尾交給 lead**——讓 lead 統一清理。teammates 各自收，容易留爛攤子。
- **定期去看一下**——放著不管越久，偏離目標的風險越大。偶爾探頭看看，即時修正。

---

## 8. 總結

Agent Teams 什麼時候好用？

- 每個 agent 有**明確的地盤**
- 溝通走**結構化管道**，不是自由聊天
- CLAUDE.md 有在維護，是真正的**共享 runtime context**

功能還在實驗階段。但一旦搞懂它們怎麼協作、怎麼溝通，你會發現這不是「好幾個 agent 各做各的」——而是一個平行運行的系統，有分工、有協調、有驗收。

平行研究、多元觀點、內建壓力測試——你的工作如果需要這些，Agent Teams 會讓你覺得一個人用 Claude 的日子回不去了。
