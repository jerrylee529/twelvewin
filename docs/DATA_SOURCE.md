# 数据源迁移计划（tushare → 可维护方案）

本文档描述 twelvewin 离线分析脚本当前对 **tushare** 的依赖，以及阶段 6 之后建议的替换路线。阶段 6 已将 Web 查询切到 **Postgres 优先、CSV 备份**；数据源替换是独立后续工作。

## 当前 tushare 使用点

| 模块 | API / 用途 | 影响 job |
|------|------------|----------|
| `analysis/instruments.py` | `get_stock_basics()` | 股票列表入库 |
| `analysis/getvaluation.py` | 分红/行情：`akshare` / **Tushare Pro**（`dividend` + `daily_basic`） | `ranking_pipeline` |
| `analysis/get_value_4_business.py` | 行情：provider 链；周 K：AkShare | `ranking_pipeline` |
| `analysis/quotation.py` | **`pro_bar` / `index_daily`**（替代 `get_k_data`） | `daily_pipeline` |
| `analysis/history_data_service.py` | 经 `quotation.get_history_data` | `daily_pipeline` |
| 其他实验脚本 | 各类历史接口 | 非 eod 主路径 |

常见问题：

- 旧版 tushare 0.8.x 接口与 Python 3 / 新 token 机制不兼容。
- `get_today_all` 等接口已长期不可用或需 pro token。
- 无统一重试、限流与审计。

## 推荐替换选项（按优先级）

### 1. AkShare（首选评估）

- 开源、接口多，A 股日线/实时/基本面覆盖较好。
- 适合：`instruments` 列表、`get_today_all` 类行情快照、部分财务数据。
- 风险：接口变更较频，需 pin 版本并封装在 `analysis/providers/akshare_provider.py`。

### 2. BaoStock

- 免费、偏历史日线与基础信息。
- 适合：`history_data_service` 日线增量。
- 风险：实时性弱，不适合盘中快照。

### 3. 自建 / 商业 API

- 若已有券商或数据商合约，可统一经 `analysis/providers/http_provider.py` 对接。
- 适合：生产稳定性要求高的环境。

## 已实现（POC）

```
analysis/providers/
  base.py              # 代码规范化、读 instruments.csv、扫描 day_data/*.csv
  akshare_provider.py  # ak.stock_info_a_code_name()
  akshare_market.py    # ak.stock_fhps_em() 分红 + 东财/新浪行情
  yahoo_market.py      # yfinance 行情 / 基本面（.SS / .SZ / .BJ）
  tushare_pro.py       # Token、`ts_code` 映射、`daily_basic` 快照
  tushare_market.py    # Pro：dividend、daily_basic、stock_basic
  tushare_provider.py  # Pro：stock_basic 标的列表
  market_registry.py   # TW_MARKET_DATA_PROVIDER 链式调度
  local_provider.py    # instruments.csv + 日线目录文件名
  registry.py          # TW_DATA_PROVIDER 链式调度

analysis/instruments.py
  get_instrument_list()   # 拉取 → 入库 → 写 instruments.csv
  get_all_instrument_codes()  # DB 优先，否则本地 CSV/日线目录
```

### 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `TW_DATA_PROVIDER` | `auto` | `auto` = akshare → tushare → local；**有 `TUSHARE_TOKEN` 时优先 tushare** |
| `TW_MARKET_DATA_PROVIDER` | `auto` | 排名：`auto` = akshare → yahoo → tushare；**已配置 `TUSHARE_TOKEN` 时优先 tushare** |
| `TUSHARE_TOKEN` | （空） | [Tushare Pro](https://tushare.pro) 令牌，见 `analysis/providers/tushare_pro.py` |
| `TW_DIVIDEND_REPORT_DATE` | 上年 `1231` | `stock_fhps_em` 报告期，如 `20241231` |
| `TW_YAHOO_QUOTE_CODES` | （空） | 仅拉指定代码，逗号分隔，如 `600000,000001` |
| `TW_YAHOO_MAX_CODES` | `0` | 限制 Yahoo 请求数量，`0` 表示不限制 |
| `TW_YAHOO_BATCH_SIZE` | `80` | `yf.download` 每批 ticker 数 |
| `TW_YAHOO_FETCH_FUNDAMENTALS` | `1` | 是否用 `fast_info` 补 PE/PB/市值 |

### 仅用 Yahoo 行情（东财/新浪不稳定时）

```bash
pip install yfinance
export TW_MARKET_DATA_PROVIDER=yahoo
# 代码列表来自 day_data/*.csv 或 instruments.csv，也可显式指定：
export TW_YAHOO_QUOTE_CODES=600000,000001,600519
python -m jobs.run ranking_pipeline
```

A 股 Yahoo 代码规则：`6/5xxxxx` → `.SS`，`0/3xxxxx` → `.SZ`，北交所/新三板 `92/83/87/88/43/4/8xxxxx` → `.BJ`（其中 `92xxxx` 为北交所新号段）。

### Tushare Pro（已接入 provider）

```bash
export TUSHARE_TOKEN=你的token
export TW_MARKET_DATA_PROVIDER=tushare   # 或 auto（有 token 时自动优先 tushare）
export TW_DIVIDEND_REPORT_DATE=20241231
python -m jobs.run ranking_pipeline
```

接口对应关系：

| 旧接口 (0.8.x) | Tushare Pro |
|----------------|-------------|
| `get_today_all()` | `daily_basic` + `stock_basic` |
| `profit_data()` | `dividend`（按 `end_date` / 年度筛选） |
| `get_stock_basics()` | `stock_basic` |
| `get_k_data()` | `pro_bar` / `index_daily` |

积分要求（官方）：`daily_basic`、`dividend` 等需一定积分，详见 tushare.pro 文档。

### 无 tushare / 无网络时

1. 在 `local_data/day_data/` 放置 `<code>.csv`，或维护 `instruments.csv`（列：`code,name`）。
2. 设置 `TW_DATA_PROVIDER=local` 跳过远程：
   ```bash
   export TW_DATA_PROVIDER=local
   python -m jobs.run eod_all
   ```
3. 或安装 AkShare 使用免费列表接口：
   ```bash
   pip install akshare
   export TW_DATA_PROVIDER=akshare
   ```

## 建议架构（后续）

```
  baostock_provider.py  # 日线 history 下载
  tushare_legacy.py     # 逐步下线

analysis/config.py  # 与 TW_DATA_PROVIDER 统一
```

离线 job 通过 `providers.registry` 拉列表，不直接在业务脚本里 `import tushare`。

## 迁移步骤（建议 PR 顺序）

1. **Provider 抽象 + 配置开关**（不改行为，tushare 仍为默认）。
2. **history_data_service** 改用 BaoStock/AkShare 日线（最易验证）。
3. **instruments + ranking_pipeline** 改用 AkShare 快照与基础面。
4. **删除脚本内直接 tushare 调用**；`requirements-analysis.txt` 去掉 tushare 或标为 optional。
5. **文档与 cron**：更新 `DEPLOYMENT.md` 所需 token/环境变量。

## 环境变量（规划）

| 变量 | 说明 |
|------|------|
| `TW_DATA_PROVIDER` | `akshare` / `baostock` / `tushare` |
| `TW_DATA_PROVIDER_TOKEN` | 若商业 API 需要 |
| `READ_ANALYSIS_FROM_DB` | Web 是否优先读 Postgres（阶段 6 已实现） |

## 与阶段 6 的关系

- 阶段 6：**存储与查询** — CSV 仍生成，但 Web 可读 DB；`manage.py import_results` 与 `eod_all` 的 `sync_results_to_db` 负责入库。
- 数据源替换：**生成侧** — 仍写 CSV（兼容）并触发 DB sync；替换 provider 后 CSV 列结构需保持稳定或同步更新 `result_store_service` 的 JSON payload。

## 验收（数据源替换完成后）

- `eod_all` 在无 tushare 环境下可跑通（使用 mock 或 AkShare）。
- 排名/技术页数据与替换前抽样一致（允许字段名映射层）。
- 集成测试覆盖 provider 选择与失败重试。
