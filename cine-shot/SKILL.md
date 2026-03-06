---
name: cine-shot
description: |
  電影感 AI 繪圖提示詞生成器。根據使用者的場景描述，自動選配攝影機模組、光影預設，
  產出 Midjourney 與 Gemini 3 Pro 雙平台格式的 cinematic prompt。

  觸發詞：/cine-shot、cinematic prompt、電影感提示詞、電影風格圖片
user_invocable: true
argument_hint: "<scene description>"
---

## 核心公式

每組 prompt 由 5 段拼裝：

```
[Subject & Action] + [Setting & Framing] + [Camera Module] + [Lighting & Vibe] + [Platform Params]
```

## 攝影機模組

根據場景氛圍自動選配，使用者可覆寫。

### Module A — ARRI（寫實 / 敘事 / 文藝冷峻）

- ARRI ALEXA Mini, Zeiss Master Prime 35mm lens
- shallow depth of field, natural skin tones, organic film grain
- 適用：劇情片、人物肖像、日常敘事、獨立電影

### Module B — RED（史詩 / 科幻 / 寬銀幕張力）

- RED Weapon Dragon 6K, Panavision Anamorphic 35mm lens
- anamorphic lens flare, wide cinematic framing, epic scale
- 適用：科幻場景、戰爭片、壯闊風景、歷史史詩

### Module C — Sony（銳利 / 賽博 / 極高反差）

- Sony CineAlta F65, Panavision Primo Prime 35mm lens
- razor-sharp detail, high dynamic range, clinical precision
- 適用：賽博龐克、未來都市、科技感場景、霓虹夜景

## 光影預設

根據氛圍自動匹配，不再固定單一光影。

| 預設 | 關鍵詞 | 適用場景 |
|------|--------|----------|
| Golden Hour | warm golden light, long shadows, amber tones, soft rim lighting | 溫暖 / 懷舊 / 田園 |
| Cold Noir | cool blue-steel tones, low-key lighting, deep shadows, muted palette | 黑色電影 / 懸疑 |
| Neon Cyber | neon-drenched, high contrast, saturated colors, electric glow, rain-slicked reflections | 賽博龐克 / 夜景 |
| Natural Doc | natural available light, neutral color grading, organic shadows, photojournalistic feel | 紀錄片 / 寫實 |
| Desolate | low contrast, muted desaturated tones, overcast diffused light, desolate atmosphere | 廢土 / 末日 |
| Dramatic | harsh directional spotlight, deep chiaroscuro, strong rim light, theatrical contrast | 戲劇 / 肖像 |

## 平台參數對照

| 項目 | Midjourney | Gemini 3 Pro |
|------|-----------|--------------|
| 尾綴參數 | `--ar {ratio} --style raw --v 7` | 不加參數，保持純描述語句 |
| 比例格式 | `--ar 16:9` | 寫入描述：`in 16:9 cinematic aspect ratio` |
| 風格控制 | `--style raw` 避免過度風格化 | 直接在描述中指定風格關鍵詞 |

## 禁止清單

以下空洞修飾詞禁止出現在產出的 prompt 中：

> beautiful, masterpiece, amazing, stunning, gorgeous, breathtaking, perfect, incredible, wonderful, magnificent

這些詞不提供視覺資訊，只佔 token。用具體描述取代。

## 工作流程

### Step 1 — 解析 ARGUMENTS

讀取使用者提供的場景描述。如果描述過短（< 10 字），直接進 Step 2 補足細節。

### Step 2 — 確認偏好

用 AskUserQuestion 一次問 3 題：

**問題 1：氛圍與光影**
- Golden Hour（溫暖金色光）
- Cold Noir（冷調懸疑）
- Neon Cyber（霓虹賽博）
- Dramatic（戲劇性強光）

> 使用者可選 Other 自訂，或指定 Natural Doc / Desolate

**問題 2：構圖與景別**
- 特寫（close-up, face detail）
- 中景（medium shot, waist-up）
- 全景（wide shot, full environment）
- 低角度仰拍（low angle, looking up, heroic perspective）

> 使用者可選 Other 輸入鳥瞰、荷蘭角等

**問題 3：畫面比例**
- 16:9 電影（標準寬螢幕）
- 2.35:1 寬銀幕（電影院比例）
- 1:1 方形（社群媒體）
- 9:16 直式（手機 / Stories）

### Step 3 — 場景擴寫 + 模組選配

根據 Step 1-2 的資訊：

1. **擴寫場景**：將簡短描述擴展為具體視覺細節（動作、環境、材質、色彩）
2. **選配攝影機模組**：依氛圍自動匹配（寫實→A, 史詩→B, 賽博→C），或遵從使用者指定
3. **選配光影預設**：依 Step 2 氛圍選擇對應預設關鍵詞
4. **禁詞檢查**：確認無禁止清單中的空洞修飾詞

### Step 4 — 組裝輸出

產出雙平台格式，使用以下結構：

```
## 🎬 Midjourney Prompt

[Subject & Action], [Setting & Framing], shot on [Camera Module equipment],
[Lighting keywords], [additional mood/texture descriptors],
cinematic composition, film grain --ar {ratio} --style raw --v 7

---

## 🎨 Gemini 3 Pro Prompt

[Subject & Action], [Setting & Framing], shot on [Camera Module equipment],
[Lighting keywords], [additional mood/texture descriptors],
cinematic composition, film grain, in {ratio} cinematic aspect ratio
```

兩組 prompt 的核心描述相同，只有尾綴參數不同。

## 輸出範例

輸入：`一個孤獨的太空人站在火星表面`
氛圍：Desolate / 全景 / 2.35:1

```
## 🎬 Midjourney Prompt

A lone astronaut in a weathered EVA suit standing motionless on the
rust-red Martian surface, endless barren plains stretching to a hazy
horizon, distant dust devils spiraling in thin atmosphere, boot prints
trailing behind in fine regolith, shot on RED Weapon Dragon 6K with
Panavision Anamorphic 35mm lens, low contrast, muted desaturated tones,
overcast diffused light, desolate atmosphere, anamorphic lens flare,
wide cinematic framing, subtle film grain --ar 2.35:1 --style raw --v 7

---

## 🎨 Gemini 3 Pro Prompt

A lone astronaut in a weathered EVA suit standing motionless on the
rust-red Martian surface, endless barren plains stretching to a hazy
horizon, distant dust devils spiraling in thin atmosphere, boot prints
trailing behind in fine regolith, shot on RED Weapon Dragon 6K with
Panavision Anamorphic 35mm lens, low contrast, muted desaturated tones,
overcast diffused light, desolate atmosphere, anamorphic lens flare,
wide cinematic framing, subtle film grain, in 2.35:1 cinematic aspect ratio
```
