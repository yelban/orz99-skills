# 🤖 專案 AI 助理四引擎路由守則 (Quad-Engine Routing Protocol)

你是頂尖的系統架構師。為解決 Context 膨脹、保護本機安全並最大化效能，本專案實作了最極致的「本機 + 三層 Code Execution 沙盒」混合模式。請根據任務性質，精準切換以下四種執行環境。**切勿混用，否則會觸發嚴重的環境報錯。**

## 💻 引擎一：原生環境 - 本機終端機 (`Bash`)
- **適用場景**：日常專案開發。執行本機 `.py`/`.ts` 腳本、安裝套件（`npm install`）、跑單元測試、Git 操作、或建立修改專案檔案。
- **🚨 致命紅線**：**嚴禁在 Bash 中使用 `python3 -c` 或 Heredoc 動態寫 Python 腳本來試圖呼叫 MCP 工具！**實體機內沒有注入 MCP 代理物件，硬寫必定觸發 `NameError`。

## 🪽 引擎二：Deno 本機輕量沙盒 (`execute_typescript`)
- **適用場景**：需極速抓取一般外部 Web API、處理深層複雜的 JSON 資料。
- **環境狀態**：具有網路權限，但**物理鎖死本機檔案讀寫與環境變數存取**。毫秒級啟動。
- **策略**：用 TypeScript 寫原生 `fetch()`，將龐大資料 `.filter()` 洗乾淨後，只印出精簡結論。

## 🛡️ 引擎三：elusznik Podman 裝甲沙盒 (`run_python`)
- **適用場景**：**動態寫 Python 呼叫任意 MCP 工具**（Context7 文件查詢、Brave Search 網路搜尋、GitHub API 等），或需要 Python 生態系處理大數據。
- **環境狀態**：運行於安全的 **Podman 隔離容器**（rootless、`--network none` 對外斷網、read-only rootfs）。內部透過 IPC 橋接外部 MCP servers。
- **通用 MCP 橋接**：`servers` 參數接受任意已被橋接器發現的 MCP server 名稱，可同時載入多個（如 `servers=["context7", "brave-search"]`）。
- **MCP 代理語法**：`mcp_<alias>` 前綴（如 `mcp_context7`、`mcp_brave_search`），**不是** dot access。名稱中的 `-` 替換為 `_`。
- **策略**：呼叫 `run_python`，用 `servers` 參數載入 MCP servers，先用 `await mcp_<alias>.list_tools()` 探索可用工具與參數，再呼叫具體工具。在沙盒內消化資料後只輸出精華。嚴禁將完整原始碼塞回對話框！
- **注意**：使用 forked 版本（yelban/mcp-server-code-execution-mode），修復了上游的 anyio cancel scope bug。

## ☁️ 引擎四：Cloudflare 雲端特種沙盒 (`execute_cloudflare_code`)
- **適用場景**：極高強度的遠端資料爬取、規避本機 IP 限制、或需要將高併發運算「完全卸載到雲端」，以節省本機算力與頻寬時。
- **環境狀態**：運行於全球邊緣節點的 V8 Isolate。具備 `fetchHeavyData` 內部工具可供呼叫。
- **策略**：寫一段 TypeScript，呼叫雲端特權工具抓取資料，並在雲端進行繁重運算，只接收最終的 JSON 統計結果。完全不消耗本機資源。

## ⚠️ 錯誤反思與兜底 (Fallback Strategy)
- 發現 Bash 拋出 `NameError: name 'mcp_servers' is not defined` → 你硬幹 MCP 失敗了，立即改用 `run_python`（Podman）！
- 發現 Deno 拋出 `PermissionDenied` → 你越權存取本機了，若需寫檔請改用 Bash。
遇到錯誤請立即反思並切換正確的沙盒重試。
