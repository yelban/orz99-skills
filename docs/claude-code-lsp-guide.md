# Claude Code LSP 完整設定指南

> 啟用 LSP (Language Server Protocol) 讓 Claude Code 從文字 grep 升級到語意級程式碼理解。
> 適用版本：Claude Code v2.0.74+

## 為什麼要啟用 LSP

Claude Code 預設用 Grep/Glob 搜尋程式碼——純文字比對，無法區分定義 vs 引用、無法追蹤型別。

LSP 連接到與 VS Code 相同的語言伺服器，提供：

| 能力 | Grep（預設） | LSP |
|------|-------------|-----|
| 跳到定義 | 文字搜尋，可能找錯 | 精確定位 |
| 找所有引用 | `rg "functionName"` | 語意級 references |
| 即時型別錯誤 | 無（等你發現） | 每次編輯後自動推送 diagnostics |
| 呼叫鏈追蹤 | 不支援 | call hierarchy |
| 速度（大專案） | 30-60 秒 | ~50ms |

## 啟用方式

### 方式 1：settings.json（推薦，持久生效）

```json
// ~/.claude/settings.json
{
  "env": {
    "ENABLE_LSP_TOOL": "1"
  }
}
```

合併到你現有的 settings.json 即可，不需覆蓋其他設定。

### 方式 2：環境變數

```bash
# 加到 ~/.zshrc（macOS）或 ~/.bashrc
export ENABLE_LSP_TOOL=1
```

### 方式 3：單次啟動

```bash
ENABLE_LSP_TOOL=1 claude
```

## 安裝 LSP Server

啟用 `ENABLE_LSP_TOOL` 只是打開開關，還需要安裝對應語言的 LSP server。

### 方式 A：透過 Plugin Marketplace（推薦）

```bash
# 進入 Claude Code 後執行（注意：repo 名稱結尾有 s）
/plugin marketplace add Piebald-AI/claude-code-lsps

# 然後從 marketplace 安裝需要的語言
/plugin
# → Marketplaces → 選擇語言
```

> **HTTPS 認證失敗？** 先執行 `gh auth login` 再 `gh auth setup-git`，然後重試。

### 方式 B：手動安裝 binary

以下是所有支援語言的 LSP server 和安裝指令：

### Tier 1：常用語言

| 語言 | LSP Server | 安裝指令 |
|------|-----------|---------|
| **Python** | Pyright | `npm install -g pyright` 或 `pip install pyright` |
| **TypeScript/JavaScript** | vtsls | `npm install -g @vtsls/language-server typescript` |
| **Rust** | rust-analyzer | `rustup component add rust-analyzer` |
| **Go** | gopls | `brew install go`（若未安裝）→ `go install golang.org/x/tools/gopls@latest` |
| **C/C++** | clangd | `brew install llvm`（macOS）或 `apt install clangd`（Linux） |

### Tier 2：Web / Mobile

| 語言 | LSP Server | 安裝指令 |
|------|-----------|---------|
| **HTML/CSS/JSON** | vscode-langservers | `npm install -g vscode-langservers-extracted` |
| **Vue** | vue-volar | `npm install -g @vue/language-server@2` |
| **PHP** | phpactor | `composer global require phpactor/phpactor` |
| **Dart/Flutter** | dart | `brew install dart` 或 `brew install --cask flutter` |
| **Ruby** | ruby-lsp | `gem install ruby-lsp` |

### Tier 3：系統 / 企業

| 語言 | LSP Server | 安裝指令 |
|------|-----------|---------|
| **Java** | jdtls | `brew install jdtls` |
| **Kotlin** | kotlin-lsp | `brew install JetBrains/utils/kotlin-lsp` |
| **C#** | omnisharp | `brew install omnisharp/omnisharp-roslyn/omnisharp-mono` |
| **Scala** | metals | `coursier bootstrap org.scalameta:metals_2.13:1.6.5` |

### Tier 4：特殊用途

| 語言 | LSP Server | 安裝指令 |
|------|-----------|---------|
| **LaTeX** | texlab | `brew install texlab` |
| **Julia** | LanguageServer.jl | Julia: `Pkg.add("LanguageServer")` |
| **OCaml** | ocaml-lsp | `opam install ocaml-lsp-server` |
| **Solidity** | solidity-ls | `cargo install solidity-language-server` |
| **PowerShell** | editor-services | PowerShell 7+ 內建 |

## 快速安裝腳本（macOS, brew/npm）

按需複製貼上：

```bash
# === Tier 1: 常用語言 ===

# Python
npm install -g pyright

# TypeScript / JavaScript
npm install -g @vtsls/language-server typescript

# Rust
rustup component add rust-analyzer

# Go（需先安裝 Go runtime）
brew install go
go install golang.org/x/tools/gopls@latest

# C / C++
brew install llvm

# === Tier 2: Web / Mobile ===

# HTML / CSS / JSON（含 eslint）
npm install -g vscode-langservers-extracted

# Vue
npm install -g @vue/language-server@2

# PHP
composer global require phpactor/phpactor

# Ruby
gem install ruby-lsp

# Dart / Flutter
brew install dart

# === Tier 3: 系統 / 企業 ===

# Java
brew install jdtls

# Kotlin
brew install JetBrains/utils/kotlin-lsp

# C#
brew install omnisharp/omnisharp-roslyn/omnisharp-mono

# Scala
coursier bootstrap org.scalameta:metals_2.13:1.6.5

# === Tier 4: 特殊用途 ===

# LaTeX
brew install texlab

# OCaml
opam install ocaml-lsp-server

# Solidity
cargo install solidity-language-server
```

裝完後一次驗證：

```bash
for cmd in pyright vtsls rust-analyzer gopls clangd jdtls; do
  which $cmd 2>/dev/null && echo "✓ $cmd" || echo "✗ $cmd not found"
done
```

## LSP 提供的操作

Claude Code 啟用 LSP 後可使用以下功能：

- **Go to Definition** — 精確跳到函式/類別定義位置
- **Find References** — 找出所有引用某符號的位置
- **Hover Information** — 取得型別資訊和文件
- **Workspace Symbols** — 搜尋整個專案的符號
- **Call Hierarchy** — 分析函式呼叫鏈（誰呼叫它、它呼叫誰）
- **Diagnostics** — 即時推送型別錯誤和警告（每次編輯後自動觸發）

## 驗證 LSP 是否生效

### 方法 1：問 Claude（最快）

在對話中直接問：「我有沒有 LSP 工具可用？」

Claude 會用 `ToolSearch` 載入 LSP 工具並回報。如果回傳工具描述就代表 LSP 已生效。

> **注意**：`latest` symlink 在**當前 session 啟動時**才更新，因此用 debug log 驗證時需要另開一個 session。

#### LSP 工具的載入機制（Deferred Tools）

LSP 是 **deferred tool**，每次新對話開始時需手動載入：

```
ToolSearch: select:LSP
```

- **每次新對話**：需要載入一次
- **同一對話內**：載入後可直接呼叫，不需重複載入

**Context 佔用**：

| 階段 | 說明 |
|------|------|
| `ToolSearch` 載入工具 | 僅加入 tool schema，固定且極小的開銷 |
| 實際呼叫 LSP 工具 | 回傳的診斷/補全/符號等結果才佔用 context |
| 語言 plugin 本身 | 語言伺服器是系統 process，影響 CPU/RAM，不影響 Claude context |

**重要**：一次 LSP 查詢針對單一檔案，一個檔案只對應一個語言伺服器。
啟用多種語言不會增加單次查詢的 context 佔用，多語言支援互不干擾。

### 方法 2：檢查 debug 日誌

```bash
# 另開終端機啟動 Claude Code，再從這裡查
grep -i "Total LSP servers loaded" ~/.claude/debug/latest
```

看到 `N > 0` 表示成功。看到 `0 servers` 表示沒有伺服器載入（重啟通常可解決）。

### 方法 3：在會話中測試

```bash
# 進入 Claude Code
claude

# 按 Ctrl+O 查看 LSP diagnostics
# 如果有即時錯誤/警告顯示 = LSP 正常
```

### 方法 4：檢查 plugin 狀態

在 Claude Code 中執行 `/plugin`：
- **Installed** 標籤：已安裝的語言外掛應列出且無錯誤
- **Errors** 標籤：若顯示「Executable not found in $PATH」= binary 未安裝

### 方法 5：確認 binary 在 PATH 中

```bash
# 逐一確認你安裝的 LSP server
which pyright
which vtsls
which rust-analyzer
which gopls
```

## 已知問題與解法

### Claude 不用 LSP，仍用 Grep

**問題**：即使 LSP 設定完成，Claude 仍傾向用 Grep/Read/Glob。

**解法**：在專案 `CLAUDE.md` 加入指引：

```markdown
## Code Navigation
- 搜尋定義和引用時，優先使用 LSP 工具（如可用），再退回到 Grep
- 編輯後查看 LSP diagnostics 確認無型別錯誤
```

### LSP 插件載入 0 個伺服器

**問題**：Race condition — LSP Manager 在插件載入完成前就初始化。
（[Issue #13952](https://github.com/anthropics/claude-code/issues/13952)）

**解法**：重啟 Claude Code 通常可解決。如持續發生，檢查 `~/.claude/debug/latest` 日誌。

### Executable not found in $PATH

**問題**：語言伺服器裝了但 Claude Code 找不到。

**解法**：確認 `~/.zshrc` 中的 PATH 包含 binary 位置：

```bash
# 常見路徑
export PATH="$HOME/.cargo/bin:$PATH"          # Rust
export PATH="$HOME/go/bin:$PATH"              # Go
export PATH="$HOME/.local/bin:$PATH"          # pip install --user
```

### LSP API 限制

LSP 協定要求傳遞 `file:line:column` 座標，不能直接問「Foo.bar 定義在哪」。
Claude Code 內部會先用 Grep 定位符號位置，再透過 LSP 精確跳轉。
這是設計限制，不影響使用。

## 快速安裝（Python + TypeScript）

大部分使用者只需這兩個：

```bash
# 安裝 LSP servers
npm install -g pyright @vtsls/language-server typescript

# 驗證安裝
which pyright && which vtsls && echo "LSP servers ready"

# 確認 settings.json 有啟用（應已設定）
cat ~/.claude/settings.json | grep ENABLE_LSP
```

重啟 Claude Code 即可生效。

## 參考連結

- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Piebald-AI/claude-code-lsps](https://github.com/Piebald-AI/claude-code-lsps) — LSP Plugin Marketplace
- [Issue #15619: Enable LSP tool](https://github.com/anthropics/claude-code/issues/15619)
- [Issue #14803: LSP plugins not recognized](https://github.com/anthropics/claude-code/issues/14803)
- [Enable LSP in Claude Code — Scott Spence](https://scottspence.com/posts/enable-lsp-in-claude-code)
- [Claude Code LSP Complete Setup Guide](https://www.aifreeapi.com/en/posts/claude-code-lsp)
