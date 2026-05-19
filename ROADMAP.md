# twelvewin 架构优化路线图

本文档给出 twelvewin 从当前 legacy Flask + CSV + Redis + 离线脚本架构，逐步演进到可部署、可维护、可迁移架构的实施路线。

## 目标

优化目标按优先级排序：

1. 提高部署可重复性。
2. 降低页面因 CSV、Redis、DB 任一缺失而崩溃的概率。
3. 统一数据库 schema 管理。
4. 降低 Web route 和离线脚本的耦合。
5. 为后续完整 Python 3.12 迁移和 Neon/Postgres 生产化铺路。

非目标：

- 不在短期内拆成微服务。
- 不立即重写前端。
- 不一次性废弃 CSV。
- 不在未验证前把所有离线分析脚本迁移到生产调度。

## 阶段 0：基线保护

目标：确保后续改动有基本安全网。

建议任务：

- 固化 Python 3.12 Web 依赖，只使用 `requirements-local.txt`。
- 新增 `requirements-analysis.txt`，单独记录分析脚本依赖。
- 增加最小 smoke test：
  - app import。
  - `/` 首页。
  - 一个 CSV 排名接口。
  - 一个数据库查询接口。
- 为 `start_local.sh` 增加启动前检查说明或脚本。
- 确认 `.env`、`local_data/`、虚拟环境和日志不进入 Git。

验收标准：

- 新机器按 `DEPLOYMENT.md` 能启动 Web。
- 缺少分析依赖时 Web 仍可启动。
- `git diff --check` 和最小测试通过。

风险：

- 当前没有 tests 目录，需要先建立测试基础。

## 阶段 1：CSV 访问封装

目标：消除 route 中直接 `open()` CSV 的模式。

建议任务：

- 新增 `app/services/csv_store.py`。
- 提供统一方法：
  - `read_result_csv(filename)`
  - `read_day_csv(code)`
  - `get_file_update_time(path)`
  - `safe_rows(...)`
- 统一处理：
  - 文件不存在。
  - 空文件。
  - 字段缺失。
  - 编码问题。
  - 匿名用户行数限制。
- 将以下 route 逐步迁移：
  - `app/stock/views.py`
  - `app/business/views.py`
  - `app/technical_analysis/views.py`
  - `app/strategy_analysis/views.py`
  - `app/annual_report/views.py`

验收标准：

- 缺少 `stock_pe.csv` 时接口返回结构化空结果或明确错误，不抛 500。
- route 文件中不再直接拼接 `RESULT_PATH + '/' + filename`。
- 页面响应结构保持兼容。

风险：

- 前端表格可能依赖旧字段，需要保持 response shape 不变。

## 阶段 2：服务层抽离

目标：让 blueprint 只做 HTTP 输入输出，业务逻辑进入服务层。

建议任务：

- 新增 `app/services/ranking_service.py`。
- 新增 `app/services/market_data_service.py`。
- 新增 `app/services/profile_service.py`。
- 新增 `app/services/watchlist_service.py`。
- 将 route 中的查询、CSV 合并、Redis 读取、字段转换移动到 service。
- 为每个 service 加最小单元测试。

推荐边界：

- `stock/views.py`：只解析 request、调用 service、返回 JSON/template。
- `market_data_service.py`：读取日线 CSV 和 Redis 实时行情，并合并 K 线数据。
- `ranking_service.py`：读取排名 CSV，补充标签，执行匿名限制。
- `profile_service.py`：读取财务指标和实时行情。

验收标准：

- 代表性 route 单文件明显变薄。
- 核心数据转换逻辑可以不启动 Flask request context 独立测试。
- 外部响应保持兼容。

风险：

- route 和 template 耦合较深，迁移时需要逐页验证。

## 阶段 3：配置统一

目标：减少环境差异和隐式配置。

建议任务：

- 让 `ProductionConfig` 支持和 `LocalConfig` 一样读取 `DATABASE_URL`。
- 将 `production.cfg` 降级为兼容路径，不作为首选。
- 增加配置校验函数，但只校验当前启用功能需要的配置。
- 为 `SECRET_KEY`、`SECURITY_PASSWORD_SALT`、mail、Redis、数据目录增加明确环境变量说明。
- 增加 `APP_ENV` 或类似环境名，避免 `APP_SETTINGS` 字符串散落。

验收标准：

- 本地、测试、生产都能通过 `.env` 或平台环境变量配置。
- Neon 连接串不需要手动特殊处理即可使用。
- 缺少关键配置时错误信息明确。

风险：

- 现有部署如果依赖 `production.cfg`，需要兼容一段时间。

## 阶段 4：数据库模型统一和迁移

目标：建立长期可维护的数据库 schema 管理。

当前进展：

- 已加入 Flask-Migrate/Alembic 迁移脚手架。
- Web app 已可选初始化 `Migrate(app, db)`；未安装迁移依赖时仍可启动。
- `requirements-local.txt` 已加入迁移依赖范围。
- 已生成初始 baseline revision：`migrations/versions/33e7716425a6_baseline_schema.py`。
- 为迁移命令增加了 `TWELVEWIN_DISABLE_ANALYZER=1` 开关，避免 Alembic 运行时触发 Analyzer 查询业务表。

建议任务：

- 首次应用到真实 Neon/Postgres 数据库前，先备份并确认 baseline 与线上表结构一致。
- 将 `analysis/models.py` 逐步改为复用 `app.models` 或共享模型包。
- 删除重复模型定义前，确认所有分析脚本仍可运行。
- 为重要表补索引和唯一约束。

优先表：

- `instrument`
- `self_selected_stock`
- `stock_labels`
- `stock_prediction`
- 财报类表
- 聚类类表
- 策略结果表

验收标准：

- 新数据库可以通过 migration 初始化。
- 已有数据库可以通过 migration 升级。
- `analysis/` 不再维护第二套 schema。

风险：

- 旧表结构和当前模型可能不完全一致，需要先对现有数据库做 schema diff。

## 阶段 5：离线任务重组

目标：把 `analysis/` 和 `bin/` 从脚本集合整理为可运维 job。

当前进展：

- 已新增 `jobs/` 包（`base.py`、`daily_pipeline.py`、`io.py`、`run.py`）。
- 已新增 `analysis_job_run` 表模型、Alembic revision `b8f4a2c91d0e` 与 `job_run_service`。
- 技术分析结果 CSV 已改为 `.tmp` → 校验 → `rename` 原子写入。
- Web 暴露 `GET /main/data_status` 查询 CSV 更新时间与最近 job 状态。
- `analysis/schedule_job.py` 与 `manage.py run_job daily_pipeline` 转调统一 pipeline。
- 实验性 `bin/` 脚本已移至 `legacy/bin/`。
- `analysis/csv_output.py` 统一原子导出；排名/涨跌幅/业务筛选 CSV 已接入。
- 全站页脚通过 `/main/data_status` 展示数据更新时间与日终任务状态。

建议任务：

- 建立 `jobs/` 或整理 `analysis/jobs/`。
- 定义统一 job 接口：
  - 输入配置。
  - 输出状态。
  - 错误处理。
  - 日志。
- 增加 job run 表，记录每次运行：
  - job name
  - started_at
  - finished_at
  - status
  - output files
  - error message
- CSV 写入改为原子写：
  - 写入 `.tmp`
  - 校验字段
  - rename 到正式文件
- 将仍需使用的 `bin/` 脚本迁移，废弃实验脚本或移动到 `legacy/`。

验收标准：

- 日终任务失败时不会留下半成品 CSV。
- 能查询最近一次 job 是否成功。
- Web 可以显示数据更新时间和 job 状态。

风险：

- 部分脚本仍是 Python 2 风格，需要逐个迁移。

## 阶段 6：数据存储升级

目标：逐步减少 CSV 作为线上查询主数据源的比例。

短期方案：

- CSV 继续作为分析产物缓存。
- Web 通过统一 `csv_store` 读取。
- 每个 CSV 产物有明确 schema。

中期方案：

- 排名和技术筛选结果写入 Postgres：
  - `ranking_results`
  - `technical_screen_results`
  - `analysis_runs`
- Web 查询 Postgres，CSV 作为导出或备份。

长期方案：

- 日线行情根据规模选择：
  - Postgres 普通表。
  - TimescaleDB。
  - Parquet + 对象存储。
  - ClickHouse。

验收标准：

- 核心页面不再依赖本地 CSV 文件存在。
- 分析结果可按日期、类型、股票代码查询。
- 支持多批次历史结果保留。

风险：

- 数据迁移和查询性能需要单独评估。

## 阶段 7：生产化和安全

目标：让项目具备基本生产运维能力。

建议任务：

- 管理员创建改为读取环境变量。
- 引入正式 WSGI Server，例如 gunicorn。
- 增加 health check：
  - app alive
  - DB 可连接
  - Redis 可连接
  - 关键数据目录可读
- Redis 支持 `rediss://`。
- 日志改为标准结构化 logging。
- 增加 Sentry 或等价错误监控。
- 配置 HTTPS、Nginx、systemd 或容器部署。

验收标准：

- 部署后能通过 `/healthz` 判断服务状态。
- 生产不会使用默认管理员密码。
- 关键异常有日志和告警。

风险：

- 当前部分错误被 `except Exception` 吃掉，需要逐步收紧。

## 推荐实施顺序

建议先做以下 6 个 PR 或提交：

1. `test: add minimal app smoke tests`
2. `refactor: add csv store service`
3. `refactor: move ranking csv reads into service`
4. `config: standardize environment based configuration`
5. `db: introduce alembic migration baseline`
6. `jobs: add analysis job run tracking`

这个顺序的原因：

- 先补测试，避免迁移时无反馈。
- 先封装 CSV，收益大且风险低。
- 再抽 service，减少 route 复杂度。
- 配置统一后再做 migration，避免环境差异影响数据库工作。
- 最后整理 job，因为涉及历史脚本最多，风险最高。

## 决策记录建议

后续每次做架构级变更，建议在文档中记录：

- 改动背景。
- 被替代方案。
- 选择理由。
- 回滚方式。
- 数据兼容策略。

可以后续新增 `docs/adr/` 目录保存 Architecture Decision Records。
