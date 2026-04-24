# Quad-Engine Routing Protocol

根據任務選擇正確的執行環境，不要混用。

## Bash（本機）
日常開發：腳本、套件安裝、測試、Git、檔案操作。
禁止 `python3 -c` 呼叫 MCP 工具（本機無代理物件，必定 NameError）。

## Deno Sandbox（`execute_typescript`）
快速 Web API fetch + JSON 處理。有網路，無檔案讀寫/環境變數。
PermissionDenied → 改用 Bash。

## Podman Sandbox（`run_python`）
在隔離容器內呼叫 MCP 工具或跑 Python。
- `servers=["context7", "brave-search"]` 橋接 MCP servers
- 代理語法：`mcp_<alias>`（`-` 換 `_`），如 `mcp_context7`
- 先 `await mcp_<alias>.list_tools()` 探索，再呼叫工具
- 在沙盒內消化資料，只輸出精華摘要

## Cloudflare（`execute_cloudflare_code`）— 未啟用
雲端邊緣 V8，重度遠端爬取用。

## Fallback
- Bash `NameError: mcp_servers` → 改用 `run_python`
- Deno `PermissionDenied` → 改用 Bash 寫檔




