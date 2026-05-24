# legacy/analysis

本目录存放已迁出主流程、仅作历史参考的 `analysis/` 脚本。

## 当前推荐入口

- 日终全量：`./bin/run_eod_jobs.sh` 或 `python -m compute eod_all`
- 仅技术筛选/下载：`python -m compute daily_pipeline`
- 仅排名 CSV：`python -m compute ranking_pipeline`
- 兼容旧入口：`analysis/schedule_job.py`、`analysis/start_job.sh`

## 仍保留在 `analysis/` 的核心模块

| 模块 | 用途 |
|------|------|
| `history_data_service.py` | 日线增量下载（Postgres `daily_bars`） |
| `technical_analysis_service.py` | 技术筛选 CSV（历史新高/新低、均线等） |
| `price_change_analysis.py` | 涨跌幅/振幅计算 |
| `getvaluation.py` / `get_value_4_business.py` | 估值排名与精选股筛选 |
| `fundamental_snapshot.py` | 基本面快照 |
| `cluster_compute.py` | 股票聚类（写入 `stock_cluster` 表） |
| `annual_report.py` | 年度行业/个股报告 |
| `instruments.py` / `quotation.py` / `providers/` | 股票列表与行情数据源 |
| `result_export.py` / `csv_output.py` / `day_data.py` | 结果发布与数据加载 |
| `schedule_job.py` / `schedule_manager.py` | 兼容调度入口 |

## 已移至 legacy 的脚本

### 聚类（已被 `cluster_compute.py` 替代）

| 脚本 | 原因 |
|------|------|
| `cluster_data_service.py` | 旧版 Python 2 聚类服务，依赖已废弃的 `bin.quotation` |
| `cluster_data_service.py.bak` | 上述文件的备份 |
| `industry_cluster.py` | `cluster_data_service` 的轻量入口 |

### 财务 / 指数下载

| 脚本 | 原因 |
|------|------|
| `financial_data_service.py` | 旧版 tushare 季报下载，未接入 pipeline |
| `downloadindex.py` | 一次性指数历史下载（固定 2018 年前） |

### 策略 / 预测实验

| 脚本 | 原因 |
|------|------|
| `strategy_test.py` | PEMAStrategy 回测，写入 `StrategyResultInfo` |
| `long_short_predict.py` | SVM 涨跌预测，写入 `StockPrediction` |
| `test.py` | 本地聚类实验（读取 `e:/sz50.csv`） |

### 监控 / 通知

| 脚本 | 原因 |
|------|------|
| `realtime_quot_updater.py` | Redis 实时行情更新（旧 tushare API） |
| `rsi_analysis.py` | RSI 超买超卖邮件通知 |
| `roe_selection.py` | 高 ROE 选股 + 雪球数据补充 |

### Shell 包装

| 脚本 | 原因 |
|------|------|
| `technical_analysis.sh` | 手动串联 `history_data_service` + `technical_analysis_service`，已被 `daily_pipeline` 替代 |

如需恢复某个脚本，可从 Git 历史中取回并移回 `analysis/`。
