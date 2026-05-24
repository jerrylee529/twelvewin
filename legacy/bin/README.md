# legacy/bin

本目录存放已迁出主流程、仅作历史参考的 `bin/` 脚本。

## 当前推荐入口

- 日终全量（推荐）：`./bin/run_eod_jobs.sh` 或 `python manage.py run_job eod_all`
- 仅技术筛选/下载：`python manage.py run_job daily_pipeline`
- 仅排名 CSV：`python manage.py run_job ranking_pipeline`
- 兼容旧入口：`analysis/start_job.sh`、`analysis/schedule_job.py`
- 数据导入：`python -m compute import_day_bars` / `python -m compute import_results`

## 仍保留在 `bin/` 的脚本

| 脚本 | 用途 |
|------|------|
| `run_eod_jobs.sh` | 生产 cron 日终任务入口，调用 `python -m compute eod_all` |

## 已移至 legacy 的脚本

### 共享配置 / 工具（仅被 legacy 脚本引用）

| 脚本 | 原因 |
|------|------|
| `commondatadef.py` | 旧版硬编码路径常量，被 legacy 批处理脚本共用 |
| `stock_utility.py` | 旧版 tushare 股票列表工具，仅 legacy 下载脚本使用 |

### 行情下载（已被 `analysis/history_data_service.py` 替代）

| 脚本 | 原因 |
|------|------|
| `downloaddaydata.py` | 旧版日线增量下载（CSV + commondatadef 路径） |
| `ts_downloaddaydata.py` | 旧版 tushare 日线下载 + 特征工程 |
| `downloaddata.py` | 旧版 txt 格式历史行情下载 |
| `downloadindex.py` | 旧版指数 txt 下载 |
| `downloadmindata.py` | 5 分钟线下载实验脚本 |
| `download15khistdata.py` | 15 分钟 K 线下载（Windows 本地路径） |

### 排名 / 报表（已被 `jobs/ranking_pipeline` + `analysis/` 模块替代）

| 脚本 | 原因 |
|------|------|
| `generate_business_report.py` | 已被 `analysis/get_value_4_business.py` 替代 |
| `getfinancialreport.py` | 旧版财务报告 CSV 生成 |
| `get_growth_valuation.py` | 旧版成长/估值报告 |
| `getreportdata.py` | 旧版 ROE/PE/PB/PEG 邮件报告 |
| `timertask.py` | 旧版 20:00 定时触发，已被 cron + `eod_all` 替代 |

### 技术策略筛选（已被 `analysis/technical_analysis_service.py` 替代）

| 脚本 | 原因 |
|------|------|
| `mafilter.py` | 均线突破筛选 + 邮件 |
| `belowmastrategy.py` | 均线下方策略 |
| `upmastrategy.py` | 均线上方策略 |
| `returntop10.py` | 策略回测持仓排名（Windows 路径） |

### ML / LSTM 实验

| 脚本 | 原因 |
|------|------|
| `stock_predict.py` | TensorFlow LSTM 训练/预测实验 |
| `stock_predict_2.py` | 与 `stock_predict.py` 重复的实验版本 |
| `predict_stock_price.py` | sklearn 线性回归演示 |
| `downloaddata4lstm.py` | LSTM 数据集下载 |
| `downloadindex4lstm.py` | LSTM 指数数据下载 |
| `makedataset.py` | LSTM 特征数据集构建 |

### 运维 / 监控 / 迁移

| 脚本 | 原因 |
|------|------|
| `datamonitor.py` | 实时价格监控告警（Windows 路径 + 旧 tushare API） |
| `import_daily_bars_export.py` | 一次性 CSV→DB 迁移工具；日常请用 `python -m compute import_day_bars` |
| `fileconverter.py` | 一次性格式转换工具 |
| `receivemsg.py` | 短信接收实验脚本 |
| `analysis_report.py` | 分析报告检查清单（无执行逻辑，纯备注模板） |

如需恢复某个脚本，可从 Git 历史中取回并移回 `bin/`。
