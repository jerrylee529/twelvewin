# twelvewin 架构说明

本文档描述 twelvewin 当前代码架构、数据流、运行边界和主要技术债。它反映的是当前仓库实际状态，不是目标架构。

## 1. 架构概览

twelvewin 当前是一个传统 Flask 单体 Web 应用，外加一组离线行情和财务分析脚本。

核心组成：

- `app/`：Flask Web 应用、蓝图、模板、SQLAlchemy 模型、Redis 读取、Analyzer。
- `analysis/`：离线数据下载、技术分析、聚类、财报抓取、调度任务。
- `bin/`：历史遗留的单次运行脚本、实验脚本和批处理工具。
- `utils/`：邮件、短信和通用工具。
- `local_data/`：本地 CSV 和 SQLite 数据目录，已被 `.gitignore` 忽略。

整体数据流：

```text
Tushare / Xueqiu / 外部数据源
        |
        v
analysis/ + bin/ 离线脚本
        |
        +--> PostgreSQL/MySQL/SQLite 数据库
        +--> local_data/day_data/*.csv
        +--> local_data/results/*.csv
        +--> Redis 实时行情 hash
                    |
                    v
app/ Flask 蓝图 + Jinja 页面 + AJAX JSON
```

## 2. Web 应用结构

Web 入口：

- `manage.py`：管理入口，提供 `runserver`、`create_db`、`drop_db`、`create_admin`、`test`。
- `start_local.sh`：当前 Python 3.12 本地启动入口，默认使用 `app.config.LocalConfig`。
- `app/__init__.py`：创建 Flask app、加载配置、初始化扩展、创建 Redis pool、注册蓝图。

主要蓝图：

- `app/main/`：首页、股票查询、财务画像、预测、投资知识和测验接口。
- `app/user/`：注册、登录、登出、邮箱确认、密码重置。
- `app/stock/`：PE/PB/ROE/股息率排名、K 线页面和历史行情接口。
- `app/business/`：精选股票列表和标签过滤。
- `app/technical_analysis/`：历史新高、新低、均线多头、突破均线、年线以上等技术筛选页面。
- `app/strategy_analysis/`：策略结果页面。
- `app/industry_analysis/`：行业分析页面。
- `app/cluster_analysis/`：聚类结果页面。
- `app/self_selected_stock/`：用户自选股。
- `app/annual_report/`：年度报告页面。

当前 Web 层特点：

- Blueprint route 中直接读取 CSV、查询数据库、访问 `analyzer`。
- Jinja 页面和 AJAX 数据接口成对存在。
- 页面稳定性依赖本地 CSV 产物是否存在。

## 3. 数据源模型

### 3.1 数据库

主要模型定义在 `app/models.py`。

典型表：

- `users`
- `instrument`
- `report`
- `stock_labels`
- `self_selected_stock`
- `stock_cluster`
- `stock_cluster_item`
- `stock_prediction`
- 多个雪球财报和财务指标表
- 策略结果表

当前数据库状态：

- Web 应用使用 Flask-SQLAlchemy。
- `analysis/models.py` 另起一个独立 SQLAlchemy Base 和 Session。
- 两套模型定义有重复，存在 schema 漂移风险。
- 当前没有可靠的 Alembic 迁移流程；`manage.py create_db` 只适合初始化，不适合生产迁移。

### 3.2 CSV 文件

CSV 是当前系统的核心数据产物之一。

主要目录：

- `DAY_FILE_PATH`：日线行情文件，通常是 `<code>.csv`。
- `RESULT_PATH`：分析结果文件，例如排名、技术筛选、年度报告。
- `INDEX_FILE_PATH`：指数行情文件。

典型结果文件：

- `stock_pe.csv`
- `stock_pb.csv`
- `stock_roe.csv`
- `stock_dividence.csv`
- `stock_business.csv`
- `highest_in_history.csv`
- `lowest_in_history.csv`
- `ma_long.csv`
- `break_ma.csv`
- `above_ma.csv`
- `price_change.csv`

当前 CSV 使用问题：

- Route 直接通过 `open()` 读取文件。
- 文件不存在、字段缺失、半写入状态缺少统一处理。
- Web 端没有明确的数据版本和更新时间元数据。

### 3.3 Redis

Redis 主要用于实时行情读取。

- `app/redis_op.py` 创建 Redis connection pool。
- `Analyzer.get_quotation()` 从 Redis hash 读取股票代码对应实时行情。
- `analysis/realtime_quot_updater.py` 负责抓取 Tushare 实时行情并写入 Redis。

当前 Redis 限制：

- 连接解析只覆盖普通 `redis://`。
- `rediss://` TLS Redis 尚未支持。
- Web 端只读取 Redis，不负责生成行情数据。

## 4. 离线分析结构

`analysis/` 是离线任务目录，主要职责：

- 下载股票基础信息。
- 下载日线历史行情。
- 生成估值和分红排名。
- 生成技术分析 CSV。
- 做行业或指数聚类。
- 生成年度报告。
- 训练或调用预测模型。
- 运行策略信号。

`bin/` 是更松散的脚本集合，包含：

- 数据下载脚本。
- 报表生成脚本。
- 预测数据集和模型脚本。
- 监控与策略实验脚本。

当前离线层问题：

- Python 2 风格残留较多。
- 配置模型与 Web 不统一。
- 部分脚本依赖 Windows 路径或本地文件。
- 调度、日志、状态、失败重试没有统一框架。
- 分析产物写入 CSV 和数据库的边界不清。

## 5. 配置和部署

当前配置入口：

- `app/config.py`：Web 配置。
- `.env.example`：本地环境变量示例。
- `analysis/config.py`：离线分析配置，读取 `TW_ANALYSIS_CONFIG_FILE` 和 `TW_ANALYSIS_ENV`。
- `app/config/production.cfg`：历史生产配置方式。

当前推荐部署基线：

- Python 3.12。
- `requirements-local.txt`。
- `APP_SETTINGS=app.config.LocalConfig` 或显式配置生产类。
- PostgreSQL/Neon 使用 `postgresql+psycopg://...`。
- Redis 使用 `redis://...`。

详细部署流程见 `DEPLOYMENT.md`。

## 6. 关键耦合点

### 6.1 应用启动和数据加载耦合

`app/__init__.py` 在 import 阶段完成大量工作：

- 创建 Flask app。
- 初始化扩展。
- 创建 Redis pool。
- 创建目录。
- 尝试初始化 `Analyzer`。
- 注册所有 blueprint。

这会让测试、脚本导入和部署启动都更容易受外部依赖影响。

### 6.2 Web route 和 CSV 文件耦合

多个 route 直接读取 `RESULT_PATH` 或 `DAY_FILE_PATH` 下文件。文件命名、字段和存在性直接决定页面能否正常返回。

### 6.3 Web 模型和分析模型重复

`app/models.py` 和 `analysis/models.py` 都定义数据库表。只修改其中一处会导致另一个运行路径使用旧 schema。

### 6.4 数据真相源混杂

同一业务页面可能同时依赖：

- 数据库中的用户、标签、财报、聚类结果。
- CSV 中的排名或日线行情。
- Redis 中的实时行情。

这让排错成本和数据一致性成本偏高。

## 7. 当前技术债清单

高优先级：

- 缺少统一 CSV 读取和错误处理。
- 缺少数据库迁移机制。
- `analysis/models.py` 与 `app/models.py` 重复。
- 生产配置仍有文件配置和环境变量配置两套路径。
- 默认管理员账号密码写死。

中优先级：

- Blueprint 中业务逻辑过重。
- `Analyzer` 职责过多。
- 离线任务缺少 job 状态和统一日志。
- 依赖文件分裂，Web 和分析依赖边界不清。
- Redis 不支持 TLS 托管服务。

低优先级：

- 模板和静态资源组织较老。
- 一些 `.bak`、`.old` 文件仍在源码目录。
- 命名和代码风格不统一。

## 8. 建议目标架构

短中期目标不是微服务化，而是把当前单体整理成更清晰的模块化单体。

建议目标结构：

```text
app/
  __init__.py
  config.py
  extensions.py
  models.py
  services/
    csv_store.py
    market_data_service.py
    ranking_service.py
    profile_service.py
    watchlist_service.py
  blueprints/
    ...

jobs/
  download_history.py
  generate_rankings.py
  generate_technical_screens.py
  update_realtime_quotes.py
  strategies/

migrations/
tests/
```

原则：

- Web route 只处理 HTTP，不直接知道 CSV 文件细节。
- 数据库模型只有一套。
- 离线任务通过服务层写入数据库或原子写入 CSV。
- 所有配置优先来自环境变量。
- 所有外部依赖都有启动检查和降级策略。
