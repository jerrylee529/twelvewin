# Dify + Twelvewin（同机部署）

本文档针对以下运行方式给出 **可直接复制** 的配置：

| 组件 | 运行方式 | 默认地址 |
|------|----------|----------|
| Twelvewin Research API | 本机 `uvicorn api.main:app --port 8090` | `http://127.0.0.1:8090` |
| Dify | 官方 Docker Compose | `http://127.0.0.1:5001/v1`（以实际映射为准） |
| Web 终端 | 本机 `npm run start` | `http://127.0.0.1:3000` |

数据流：

```text
浏览器 → Web :3000 (/api/agent/* BFF)
           → Dify :5001/v1
               → HTTP Tool → Twelvewin API :8090
                   → Postgres / Redis
```

---

## 1. Twelvewin API（本机 uvicorn）

启动：

```bash
cd /path/to/twelvewin
source .venv-api/bin/activate   # 或你的 venv
uvicorn api.main:app --host 127.0.0.1 --port 8090
```

建议在 Twelvewin 根目录 `.env` 中设置（见根目录 `.env.example`）：

```bash
TW_RESEARCH_API_KEY=change-me-to-a-long-random-string
TW_AGENT_ENABLED=true
```

自检：

```bash
curl -s http://127.0.0.1:8090/api/v1/health
curl -s http://127.0.0.1:8090/api/v1/data-status
```

---

## 2. Dify Docker → 访问本机 Twelvewin API

Dify 容器 **不能** 使用 `http://127.0.0.1:8090`（容器内的 127.0.0.1 是容器自身，不是宿主机）。

在 Dify 控制台 → **设置 → 环境变量**（或 `.env`）中配置：

```bash
TWELVEWIN_API=http://host.docker.internal:8090
TW_RESEARCH_API_KEY=与 Twelvewin .env 中相同的密钥
```

### Linux 服务器

若 `host.docker.internal` 不可用，在 Dify 的 `docker-compose.yaml` 中为 API/worker 服务添加：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

或使用宿主机内网 IP，例如 `http://192.168.1.10:8090`。

### macOS（Docker Desktop）

通常直接使用 `http://host.docker.internal:8090` 即可。

### 在 Dify 容器内验证

```bash
docker compose exec api curl -s http://host.docker.internal:8090/api/v1/health
```

HTTP Tool 请求头（每个 Tool 或 OpenAPI 全局）：

```http
X-Twelvewin-Api-Key: {{TW_RESEARCH_API_KEY}}
Accept: application/json
```

---

## 3. Web（本机 npm run start）→ 访问 Dify

在 `web/.env.local` 中配置（**不要**提交到 Git）：

```bash
API_URL=http://127.0.0.1:8090

# Dify Chat API（服务端 BFF 使用，禁止 NEXT_PUBLIC_ 前缀）
DIFY_API_URL=http://127.0.0.1:5001/v1
DIFY_STOCK_AGENT_API_KEY=app-xxxxxxxxxxxxxxxx
# 可选：摘要 Workflow 应用
DIFY_STOCK_SUMMARY_API_KEY=app-yyyyyyyyyyyyyyyy

TW_AGENT_ENABLED=true
```

说明：

- Web 与 Dify 都在 **宿主机** 上，通过 `127.0.0.1` 互通。
- 若 Dify 只通过 Nginx 暴露 80 端口，则改为 `DIFY_API_URL=http://127.0.0.1/v1`。
- 确认端口：`cd /path/to/dify/docker && docker compose ps`

自检（在宿主机）：

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5001/v1/parameters \
  -H "Authorization: Bearer app-你的密钥"
```

---

## 4. Dify 应用配置摘要

### 应用变量（Inputs）

| 变量 | 说明 |
|------|------|
| `stock_code` | 股票代码，Web 从 `/stock/[code]` 传入 |
| `stock_name` | 可选 |
| `locale` | 默认 `zh-CN` |

### 推荐 HTTP Tool（聚合接口）

```http
GET {{TWELVEWIN_API}}/api/v1/stocks/{{stock_code}}/research-context
X-Twelvewin-Api-Key: {{TW_RESEARCH_API_KEY}}
```

在 Dify Agent 应用中绑定 Tool `get_research_context`，System Prompt 见 [`prompts/system.md`](./prompts/system.md)。

Web BFF（已实现，Key 不暴露给浏览器）：

| 路径 | 说明 |
|------|------|
| `GET /api/agent` | 是否启用 Agent |
| `POST /api/agent/chat` | 流式对话 |
| `POST /api/agent/summary` | 阻塞式摘要 |

多 Tool 备用方案见 [twelvewin-tools.md](./twelvewin-tools.md)。

### Dify API 调用示例（与 Web BFF 一致）

```bash
curl -X POST 'http://127.0.0.1:5001/v1/chat-messages' \
  -H 'Authorization: Bearer app-你的密钥' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": {
      "stock_code": "600000",
      "stock_name": "浦发银行",
      "locale": "zh-CN"
    },
    "query": "相对同行业，估值处于什么水平？",
    "response_mode": "blocking",
    "user": "oss-dev-1"
  }'
```

---

## 5. 配置对照（勿混用）

| 调用方 | Twelvewin API 基址 | Dify API 基址 |
|--------|-------------------|---------------|
| 浏览器 → Web rewrite | `http://127.0.0.1:8090`（`API_URL`） | 不直连 |
| Web BFF → Dify | — | `http://127.0.0.1:5001/v1` |
| Dify Tool → Twelvewin | `http://host.docker.internal:8090` | — |
| 本机 curl 调试 Twelvewin | `http://127.0.0.1:8090` | — |

**错误示例**：在 Dify Tool 里写 `http://api:8090`（仅适用于 Twelvewin 也在同一 Docker Compose 网络内）。

---

## 6. 启动顺序

1. Postgres / Redis（若 Twelvewin 依赖）
2. `uvicorn api.main:app --port 8090`
3. Dify：`docker compose up -d`
4. `cd web && npm run build && npm run start`
5. 确保已发布分析数据：`python -m compute eod_all`（或等价 job）

---

## 7. 故障排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Dify Tool 连接 refused | 用了容器内 127.0.0.1 | 改为 `host.docker.internal:8090` |
| Linux 无法解析 host.docker.internal | 未配置 extra_hosts | 见上文 §2 |
| Web 调 Dify 401 | App API Key 错误 | 在 Dify 应用 → API 访问 复制 Key |
| Agent 回答「无数据」 | 未跑 EOD | `GET /api/v1/data-status` 检查 |
| uvicorn 只监听 127.0.0.1 | 正常；Dify 通过 host.docker.internal 访问 | 不要将 API 暴露到公网除非有鉴权 |

---

## 相关文件

- [Twelvewin Tool 端点清单](./twelvewin-tools.md)
- [Dify 环境变量示例](./env.example)
- 根目录 `.env.example` — `TW_RESEARCH_API_KEY`
- `web/.env.example` — `DIFY_API_URL` 等
