# legacy/bin

本目录存放已迁出主流程、仅作历史参考的 `bin/` 脚本。

## 当前推荐入口

- 日终全量（推荐）：`./bin/run_eod_jobs.sh` 或 `python manage.py run_job eod_all`
- 仅技术筛选/下载：`python manage.py run_job daily_pipeline`
- 仅排名 CSV：`python manage.py run_job ranking_pipeline`
- 兼容旧入口：`analysis/start_job.sh`、`analysis/schedule_job.py`

## 仍保留在 `bin/` 的常用脚本

- `downloaddaydata.py` / `ts_downloaddaydata.py`：行情下载
- `generate_business_report.py`：业务报表
- `datamonitor.py`：数据监控
- `timertask.py`：定时任务包装

## 已移至 legacy 的脚本

| 脚本 | 原因 |
|------|------|
| `stock_predict_2.py` | 与 `stock_predict.py` 重复的实验版本 |
| `fileconverter.py` | 一次性格式转换工具 |
| `receivemsg.py` | 短信接收实验脚本 |

如需恢复某个脚本，可从 Git 历史中取回并移回 `bin/`。
