# codex-plan Behavioral Constraints 測試報告

**日期**：2026-02-12

## 背景

GPT-5.3-Codex 比 5.2 更快更積極，容易出現 scope drift 和過度重構。為此在 `codex-plan/SKILL.md` 加入三個行為約束 XML block，並以 `model_reasoning_summary=concise` 精簡推理摘要。

## 新增約束

| Block | 用途 |
|-------|------|
| `<output_verbosity_spec>` | 控制輸出格式：bullet point 為主，避免冗長敘述 |
| `<design_and_scope_constraints>` | 只做被要求的事，不加額外功能 |
| `<context_loading>` | 強制先讀完所有相關檔案再寫計畫 |

## 測試方法

用 3 種 prompt 平行跑 `codex exec`，新版含約束 + `concise` 摘要，舊版無約束 + `auto` 摘要。

## 測試案例與結果

### Test 1：Health Script（scope drift 測試）

**Prompt**：加一個 `scripts/health.sh`，印 "ok" 然後 exit 0。

| | 新版 | 舊版 |
|---|---|---|
| Token 用量 | **15,744** | 22,548 |
| Scope drift | 無，明確列 "Out of scope" | 無 |
| 先讀 codebase | 讀了 README、package.json、SKILL.md | 也有讀 |
| 輸出格式 | 精簡 bullet | 稍冗長，多了分段 |

**改善**：省 ~30% token（concise summary 效果）。

### Test 2：`--dry-run` Flag（codebase 感知測試）

**Prompt**：幫 codex-plan skill 加 `--dry-run` flag。

| 指標 | 新版結果 |
|---|---|
| 先讀 SKILL.md | 完整讀取 |
| 搜尋現有 pattern | 搜了 `--dry-run` 和 `ARGUMENTS` |
| 讀 references/ | 讀了 plan-template.md、settings.local.json |
| Scope | 嚴格限定只改 SKILL.md，列出 4 個精確 edit point |
| 額外功能 | 無 |
| 輸出格式 | 使用 What changed / Where / Risks / Next steps / Open questions 標籤 |

**改善**：`<context_loading>` 讓 Codex 先讀完所有相關檔案。`<output_verbosity_spec>` 的 tag 格式被遵守。

### Test 3：Env Var（簡潔度測試）

**Prompt**：讓 Codex 模型可透過 `CODEX_MODEL` 環境變數設定。

| 指標 | 新版結果 |
|---|---|
| 計畫長度 | **17 行** |
| Scope | "Change exactly one line" |
| 多餘建議 | 零 |

**改善**：`<design_and_scope_constraints>` 完美生效。改一行就寫一行的計畫，不膨脹。

## 結論

| 約束 | 效果 | 信心 |
|---|---|---|
| `output_verbosity_spec` | tag 格式被遵守、計畫更精簡 | 高 |
| `design_and_scope_constraints` | 零 scope drift、不加額外功能 | 高 |
| `context_loading` | 先讀完整檔案再寫計畫 | 高 |
| `model_reasoning_summary=concise` | 省 ~30% token | 中 |
