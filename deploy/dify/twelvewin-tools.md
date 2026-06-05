# Twelvewin Research API — Dify Tool 清单

基址（Dify 容器内）：`{{TWELVEWIN_API}}` = `http://host.docker.internal:8090`

所有请求建议携带：

```http
X-Twelvewin-Api-Key: {{TW_RESEARCH_API_KEY}}
Accept: application/json
```

OpenAPI 完整定义：`http://127.0.0.1:8090/openapi.json`（宿主机导入 Dify 后删除 Agent 不需要的路径）。

---

## 推荐：单 Tool（已实现）

| 名称 | 方法 | 路径 |
|------|------|------|
| `get_research_context` | GET | `/api/v1/stocks/{stock_code}/research-context` |

Dify OpenAPI 导入时可只保留此 path，或手动创建 HTTP GET Tool。

---

## 现有端点（临时多 Tool 方案）

| 名称 | 方法 | 路径 | 参数 |
|------|------|------|------|
| `get_data_status` | GET | `/api/v1/data-status` | — |
| `get_fundamentals` | GET | `/api/v1/fundamentals/screener` | `search={code}`, `page_size=1` |
| `get_stock_profile` | GET | `/api/v1/stocks/{code}/profile` | `include_quote=false` |
| `get_stock_quote` | GET | `/api/v1/stocks/{code}/quote` | — |
| `get_stock_bars` | GET | `/api/v1/stocks/{code}/bars` | `days=250` |
| `search_stocks` | GET | `/api/v1/stocks/search` | `q`, `limit=10` |
| `get_industry_peers` | GET | `/api/v1/industries/{industry}/stocks/{code}` | 需已知 industry |
| `fundamentals_screener` | GET | `/api/v1/fundamentals/screener` | `roe_min`, `pe_max`, … |

### 技术筛选（整表，慎用）

| screen_key | 路径 |
|------------|------|
| `highest` | `/api/v1/technical/highest?preview=true` |
| `lowest` | `/api/v1/technical/lowest?preview=true` |
| `ma_long` | `/api/v1/technical/ma_long?preview=true` |
| `break_ma` | `/api/v1/technical/break_ma?preview=true` |
| `above_ma` | `/api/v1/technical/above_ma?preview=true` |

`preview=true` 仅返回前 10 条，**无法可靠判断单只股票是否命中**；长期应使用 `research-context` 中的 `technical_signals`。

### 排名（整表，慎用）

| ranking_key | 路径 |
|-------------|------|
| `pe` | `/api/v1/rankings/pe` |
| `pb` | `/api/v1/rankings/pb` |
| `roe` | `/api/v1/rankings/roe` |
| `divi` | `/api/v1/rankings/divi` |

---

## 响应形状

列表类接口统一：

```json
{
  "total": 100,
  "rows": [{ "code": "600000", "name": "..." }],
  "updateTime": "2026-05-30",
  "error": null
}
```

K 线：

```json
{
  "rows": [["2026-05-30", open, close, low, high]],
  "updateTime": "2026-05-30",
  "error": null
}
```
