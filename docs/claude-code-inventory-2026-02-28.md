# Claude Code 安裝清單 — 2026-02-28

> 掃描來源：`~/.claude/`、`~/.claude.json`、`~/.agents/skills/`

---

## MCP Servers

| 名稱 | 層級 | 來源 / 指令 | 備註 |
|------|------|------------|------|
| `code-execution` | 全域 | `uvx --from git+https://github.com/elusznik/mcp-server-code-execution-mode` | podman bridge |
| `claude-in-chrome` | 全域 | Chrome Extension 內建 | 已安裝啟用 |
| `context7` | 專案層 | — | TextConceptAnalysis + .claude |
| `cloudflare` | 專案層 | — | blog + pages |

---

## Plugins（9 個）

| 名稱 | 來源 Marketplace | 版本 | 安裝日期 |
|------|-----------------|------|---------|
| `playwright` | claude-plugins-official | 55b58ec6 | 2026-01-19 |
| `typescript-lsp` | claude-plugins-official | 1.0.0 | 2026-01-19 |
| `commit-commands` | claude-plugins-official | 55b58ec6 | 2026-01-19 |
| `code-simplifier` | claude-plugins-official | 1.0.0 | 2026-01-19 |
| `ralph-loop` | claude-plugins-official | 55b58ec6 | 2026-01-19 |
| `agent-sdk-dev` | claude-plugins-official | 55b58ec6 | 2026-01-19 |
| `rust-analyzer-lsp` | claude-plugins-official | 1.0.0 | 2026-02-01 |
| `codex-orchestrator` | codex-orchestrator-marketplace | 1.0.0 | 2026-02-17 |
| `cartographer` | cartographer-marketplace | 2.0.0 | 2026-02-17 |

---

## Skills（38 個）

全部為 symlink，指向 `~/.agents/skills/`

### baoyu 系列（15 個）

| Skill | 安裝日期 |
|-------|---------|
| `baoyu-article-illustrator` | 2026-02-13 |
| `baoyu-comic` | 2026-02-13 |
| `baoyu-compress-image` | 2026-02-13 |
| `baoyu-cover-image` | 2026-02-13 |
| `baoyu-danger-gemini-web` | 2026-02-13 |
| `baoyu-danger-x-to-markdown` | 2026-02-13 |
| `baoyu-format-markdown` | 2026-02-13 |
| `baoyu-image-gen` | 2026-02-13 |
| `baoyu-infographic` | 2026-02-13 |
| `baoyu-markdown-to-html` | 2026-02-13 |
| `baoyu-post-to-wechat` | 2026-02-13 |
| `baoyu-post-to-x` | 2026-02-13 |
| `baoyu-slide-deck` | 2026-02-13 |
| `baoyu-url-to-markdown` | 2026-02-13 |
| `baoyu-xhs-images` | 2026-02-13 |

### orz99-skills 系列（11 個，本機開發）

| Skill | 安裝日期 |
|-------|---------|
| `cine-shot` | 2026-02-20 |
| `code-review` | 2026-02-19 |
| `codex-plan` | 2026-02-13 |
| `codex-review` | 2026-02-23 |
| `good-writing-zh` | 2026-02-13 |
| `humanizer-tw` | 2026-02-17 |
| `plan-review` | 2026-02-19 |
| `project-profiler` | 2026-02-16 |
| `reflect` | 2026-02-20 |
| `release-skills` | 2026-02-13 |
| `system-audit` | 2026-02-20 |

### 通用工具（12 個）

| Skill | 安裝日期 |
|-------|---------|
| `canvas-design` | 2026-02-16 |
| `cartographer` | 2026-02-24 |
| `codex-orchestrator` | 2026-02-24 |
| `doc-coauthoring` | 2026-02-16 |
| `docx` | 2026-02-16 |
| `frontend-design` | 2026-02-16 |
| `pdf` | 2026-02-16 |
| `plan-review` | 2026-02-19 |
| `pptx` | 2026-02-16 |
| `schematic` | 2026-02-17 |
| `skill-creator` | 2026-02-16 |
| `ui-ux-pro-max` | 2026-02-13 |
| `xlsx` | 2026-02-16 |

---

## 磁碟佔用

| 路徑 | 大小 | 說明 |
|------|------|------|
| `~/.claude/projects/` | 1.1 GB | 99 個專案的對話 session（.jsonl） |
| `~/.claude/history.jsonl` | 980 KB | CLI 指令歷史 |
| `~/.claude/tasks/` | 344 KB | Task 清單 |
| `~/.claude/` 總計 | 1.8 GB | — |

---

## 備份與重裝指南

### 資料儲存位置

| 資料 | 位置 | 說明 |
|------|------|------|
| 對話 session 內容 | `~/.claude/projects/<slug>/<uuid>.jsonl` | `--resume` 靠這個，非 `.claude.json` |
| CLI 輸入歷史 | `~/.claude/history.jsonl` | — |
| 全域 MCP 設定 | `~/.claude.json` → `mcpServers` | 重裝後需手動還原 |
| 專案層 MCP 設定 | `~/.claude.json` → `projects[].mcpServers` | 4 個有設定的專案 |
| 最後一次 session ID | `~/.claude.json` → `projects[].lastSessionId` | 僅用於 `claude`（不帶參數），`--resume <uuid>` 不需要 |
| Auth 憑證 | macOS Keychain | 不需要備份，重裝後 OAuth 登入即恢復 |

### `claude --resume` 運作機制

```
claude --resume <uuid>
  ↓
直接讀取 ~/.claude/projects/<slug>/<uuid>.jsonl
  ↓
完全不依賴 ~/.claude.json 的任何欄位
```

`lastSessionId` 只在 `claude`（不帶參數）時使用，對 `--resume <uuid>` 無影響。

### 備份範圍

```bash
# 兩個位置互相獨立，都需要備份
mv ~/.claude ~/.claude-backup-2026-02-28    # session 歷史 + CLAUDE.md + settings
cp ~/.claude.json ~/.claude.json.bak        # 全域/專案層 MCP 設定
```

### 重裝後需複製回來的項目

| 路徑 | 必要性 | 說明 |
|------|--------|------|
| `~/.claude/projects/` | ★★★ | `--resume` 需要 |
| `~/.claude/CLAUDE.md` | ★★★ | 個人設定 |
| `~/.claude/settings.json` | ★★ | plugin 啟用清單 |
| `~/.claude/commands/` | ★★ | 自訂指令 |
| `~/.claude/plans/` | ★ | codex-plan 計畫存檔 |
| `~/.claude/tasks/` | ★ | Task 清單 |
| `~/.claude/history.jsonl` | ★ | CLI 歷史 |
| `~/.claude/statusline-command.sh` | ★ | Statusline 腳本 |
| `~/.claude.json` | ★★ | 建議整份複製回來，恢復 MCP 設定 |

### 不需要複製（讓新安裝重建）

`plugins/`、`skills/`、`cache/`、`statsig/`、`telemetry/`、`debug/`、
`session-env/`、`shell-snapshots/`、`paste-cache/`、`stats-cache.json`

### 重裝後需手動重裝

- **Plugins**：照本清單用 marketplace 重裝（9 個）
- **Skills**：`npx skills install yelban/orz99-skills --all -g` + baoyu 系列
- **全域 MCP**：若直接複製 `~/.claude.json` 則自動恢復；否則手動設定 `code-execution`

---

## Context 佔用分析

| 來源 | 每次對話是否載入 | 大小 |
|------|----------------|------|
| `~/.claude/CLAUDE.md` | ✅ 全部載入 | 273 行 / 7.6 KB |
| `~/.claude/projects/.../memory/MEMORY.md` | ✅ 全部載入 | ~200 行 |
| Skills system prompt（38 個描述） | ✅ 全部注入 | 每個 skill 約 2-5 行 |
| Project CLAUDE.md（如有） | ✅ 全部載入 | 視專案而定 |
