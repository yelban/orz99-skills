# Amanda Askell 寓言探索法——用故事學會任何領域的概念

> 來源：Amanda Askell（Anthropic Prompt Engineer / 哲學家）於 2026 年 4 月 Newcomer Pod 訪談
> 影片：https://www.youtube.com/watch?v=0GaKJ4Fp2x4（約 52:47–55:04）

---

## 一、她的原話（逐字稿整理）

訪談最後，主持人問 Amanda：「你跟模型的關係這麼深，如果要推薦大家花時間跟 Claude 做些什麼，你會建議什麼？」

Amanda 的回答：

> Yeah, there's a lot of little fun things. Honestly, one that I really like — and I do know why I like this, and I think I have posted about it before — is sometimes if I'm just, it's one of those like if you're bored and you want to do something that isn't just scroll the internet.
>
> I have this prompt, which is essentially: **I want you to take a concept from maybe grad school level in a given domain** — and I'll tell you the domain at the end — **and I want you to write me a parable that would fully explain that concept but in an indirect way, in the way that parables do.** And I want you to write it in such a way that **only towards the very end does it become sort of clear what the concept is.** And then after that, I want you to **just write an explanation for the concept that you were explaining and that you were using.**
>
> And I don't know why, but there's lots of just interesting domains that I don't know anything about or that I'm interested in. And this has just led to me having all of these stories in my head that explain — and sometimes I can't always remember the term — but there was one on import/export and why some goods you tend to import, and I was like, I have in my head this concept, and it's so nice to have all of these concepts from lots of different disciplines.

主持人的回應：

> This is the most deeply human thing I've ever heard. It's like: teach me — story is the fundamental way. We love a payoff at the end where there's a nice little twist. We love learning. You know how to structure it. Humans in some ways have been lazy in that we just teach people things in nonhuman ways. Make all the things I want to learn as human as possible.

---

## 二、提示詞（可直接複製使用）

### 英文版

```
I want you to select a concept at about the graduate-student level from the field of [YOUR FIELD HERE]. Then explain this concept completely by writing a parable — indirectly, the way parables do. Structure the story so that only toward the very end does it gradually become clear what the concept actually is. After the story, write a section that clearly explains the concept you were conveying.
```

### 中文版

```
我希望你從【你的領域】裡選一個大約研究所程度的概念。然後用寫寓言的方式，間接地把這個概念完整解釋出來。故事的結構要讓讀者一直到快結尾時，才慢慢意識到這個概念究竟是什麼。故事之後，再補一段清楚的解釋，說明你剛才真正要講的概念。
```

### 使用方式

把 `[YOUR FIELD HERE]`（或中文版的「你的領域」）替換成任何你好奇的學科，例如：

- 量子力學
- 行為經濟學
- 拓撲學
- 認知科學
- 國際貿易
- 演化生物學
- 賽局理論
- 語言學
- 神經科學
- 熱力學

---

## 三、具體操作流程

| 步驟 | 做法 |
|------|------|
| 1. 選領域 | 把提示詞中的領域欄位換成你好奇的學科 |
| 2. 送出 | 直接貼給 Claude（或任何 LLM）|
| 3. 讀故事 | 先讀寓言本身，試著自己猜背後的概念是什麼 |
| 4. 對答案 | 讀結尾的解釋段落，看自己猜對多少 |
| 5. 重複 | 同一個領域可以反覆送出，每次會選不同概念 |

---

## 四、為什麼有效

1. **故事記憶**：人腦天生擅長記故事，不擅長記定義。Amanda 自己說，有時她記不住術語，但概念本身透過故事牢牢記住了。

2. **間接理解**：寓言的本質是迫使讀者主動推理，而非被動接收。你讀的過程中會不斷猜測「這到底在講什麼」，這個推理過程本身就是深度學習。

3. **結尾揭曉**：類似推理小說的結構，產生「原來如此」的頓悟感（aha moment）。這種情緒高峰讓記憶更持久。

4. **跨域探索**：不需要任何前置知識。研究所程度的概念被故事「降維」成直覺可及的東西，讓你能輕鬆跨越學科邊界。

5. **累積效應**：反覆使用後，你的腦中會累積來自各學科的故事庫。就像 Amanda 說的：「it's so nice to have all of these concepts from lots of different disciplines.」

---

## 五、變體玩法

### 調整難度

```
# 降低難度——適合完全陌生的領域
我希望你從【領域】裡選一個大學入門課程中最反直覺的概念。
然後用寓言的方式間接解釋……（後面同上）

# 提高難度——適合有一定基礎的領域
我希望你從【領域】裡選一個該領域專家才會知道的非直覺概念。
然後用寓言的方式間接解釋……（後面同上）
```

### 批次學習

```
同上，但請連續寫 3 個不同概念的寓言，每個寓言後都附解釋。
概念之間盡量涵蓋該領域不同的子領域。
```

### 指定故事風格

```
# 中國古代寓言風格
……用先秦寓言的風格來寫（類似莊子、韓非子的筆法）

# 科幻短篇風格
……用科幻短篇的風格來寫，設定在未來世界

# 伊索寓言風格
……用伊索寓言的風格來寫，角色是動物

# 偵探故事風格
……用偵探推理的風格來寫，讓概念像案件的真相一樣在最後揭曉
```

### 互動版（先猜再揭曉）

```
我希望你從【領域】裡選一個大約研究所程度的概念，用寓言間接解釋。
但請分兩段回覆：
第一段只寫寓言故事本身，不要揭曉概念。寫完後停下來，等我猜。
等我回覆之後，再告訴我正確答案和完整解釋。
```

### 跨領域對比

```
請從【領域 A】和【領域 B】各選一個概念，這兩個概念在表面上看起來毫無關係，
但在深層結構上有相似之處。分別用寓言解釋，最後再寫一段說明它們的結構相似性。
```

---

## 六、Amanda 的使用情境

她在訪談中提到的具體脈絡：

- **使用時機**：無聊、不想只是滑手機的時候
- **替代對象**：取代無意識地滾動社群媒體
- **累積成果**：腦中建立了一個跨學科的「故事概念庫」
- **具體例子**：曾用這個方法學到國際貿易中「為什麼某些商品傾向進口」的經濟學概念
- **記憶特性**：有時記不住術語名稱，但概念本身透過故事牢牢記住

---

## 七、延伸：她的早期版本（2025 年 3 月）

Amanda 曾在 X（Twitter）上分享過類似但更結構化的版本，專門用於經濟學：

> 固定寫 3 段故事 + 結尾解釋

2026 年 4 月這個版本是她日常實際使用的通用版，更簡潔、更靈活，適用於任何領域。

---

*整理自 Newcomer Pod 訪談逐字稿，影片時間碼 52:47–55:04。*
