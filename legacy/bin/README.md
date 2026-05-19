# legacy/bin

本目录存放已迁出主流程、仅作历史参考的 `bin/` 脚本。

## 当前推荐入口

- 日终分析：`python -m jobs.run daily_pipeline`
- 或通过 Web 项目管理脚本：`python manage.py run_job daily_pipeline`
- 兼容旧 cron 入口：`python analysis/schedule_job.py`（内部转调 `jobs.daily_pipeline`）

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
