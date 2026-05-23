# twelvewin 部署文档（Python 3.12）

本文档说明如何使用 Python 3.12 部署 twelvewin Web 应用。当前仓库处于 legacy Flask 项目向 Python 3 迁移后的过渡状态，部署时应优先使用 `requirements-local.txt`，不要直接使用历史 `requirements.txt`。

## 1. 部署范围

当前文档覆盖 Web 应用部署：

- Flask 页面和 JSON 接口
- SQLAlchemy 数据库表初始化
- PostgreSQL/Neon 数据库连接
- Redis 行情缓存连接
- 本地 CSV 数据目录准备

当前文档不把 `analysis/` 离线批处理作为生产部署必需步骤。`analysis/` 中很多脚本仍有 Python 2 风格代码，并依赖 `pandas`、`numpy`、`tushare`、`scikit-learn`、`APScheduler` 等额外包；如需部署批处理任务，应先单独迁移和验证这些脚本。

若已启用阶段 5 的 job 框架，可按以下方式运行日终任务并记录状态：

```bash
set -a && . ./.env && set +a
export TWELVEWIN_DISABLE_ANALYZER=1
flask db upgrade   # 创建 analysis_job_run 表
python -m compute eod_all
# 或单独运行：
# python -m compute daily_pipeline
# python -m compute ranking_pipeline
# python -m compute import_results

# 兼容（会打印弃用提示）：
# python manage.py run_job eod_all
# python -m jobs.run eod_all
```

生产 cron 推荐使用仓库根目录脚本（需先 `chmod +x bin/run_eod_jobs.sh`）：

```bash
./bin/run_eod_jobs.sh
```

分析依赖（akshare、pandas 等）见 `requirements-analysis.txt`，Web 部署可不安装。

无 tushare 时可用本地代码列表：

```bash
export TW_DATA_PROVIDER=local   # 仅读 instruments.csv 或 day_data/*.csv
# 或
export TW_DATA_PROVIDER=akshare # 需 pip install akshare
```

### 阶段 6：分析结果入库（Postgres/SQLite）

迁移新表：

```bash
flask db upgrade   # 含 analysis_runs、ranking_results、technical_screen_results
```

将已有 CSV 导入数据库（Web 默认 `READ_ANALYSIS_FROM_DB=true`，优先读库）：

```bash
python -m compute import_results
# 或：python manage.py import_results
# 单项回填需使用 manage.py import_results ranking:pe
```

仅跑 Web、不跑批处理时，也可在每次更新 CSV 后执行 `import_results`。

Web 可通过 `GET /main/data_status` 查看主要 CSV 的 `update_time` 与最近一次 `daily_pipeline` 运行状态。

## 2. 服务器前置条件

推荐环境：

- Python 3.12.x
- Git
- Redis 6+ 或兼容 Redis 服务
- PostgreSQL 14+，或 Neon Postgres
- 可访问外网的服务器，用于安装 Python 包和访问 Neon

确认 Python 版本：

```bash
python3.12 --version
```

如果系统没有 `python3.12`，需要先用系统包管理器、`pyenv` 或服务器镜像安装 Python 3.12。

## 3. 获取代码

```bash
git clone <YOUR_REPO_URL> twelvewin
cd twelvewin
```

如果服务器上已经有仓库：

```bash
cd /path/to/twelvewin
git pull
```

## 4. 创建 Python 3.12 虚拟环境

```bash
python3.12 -m venv .venv312
./.venv312/bin/python -m pip install --upgrade pip setuptools wheel
./.venv312/bin/pip install -r requirements-local.txt
```

说明：

- `requirements-local.txt` 是当前 Python 3.12 Web 应用依赖入口。
- `requirements.txt` 保留了历史依赖，包含部分不适合 Python 3.12 的旧版本包，部署时不要优先使用。
- 虚拟环境目录 `.venv312/` 已被 `.gitignore` 忽略，不应提交。

## 5. 准备 PostgreSQL / Neon

### 5.1 数据库命名建议

建议数据库名使用项目名和环境名：

```text
twelvewin_prod
twelvewin_staging
twelvewin_dev
```

如果使用 Neon，一个 Neon Project 可以包含多个 database；生产环境建议使用 `twelvewin_prod`。

### 5.2 连接字符串格式

本项目 Python 3.12 依赖使用 `psycopg` v3，推荐连接字符串使用：

```text
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Neon 控制台复制出的连接串可能是：

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require
```

用于本项目时建议改成：

```text
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

原因：

- `postgresql+psycopg://` 明确指定 SQLAlchemy 使用 psycopg v3 驱动。
- 当前生产配置不会自动清理 `channel_binding` 参数，建议先移除。

## 6. 配置（单一 `.env` 文件）

Web、compute、analysis 均只读取仓库根目录 **`/.env`**（`python-dotenv`，见 `core/env.py`）。**不同环境**（本机、测试机、生产）通过**各自机器上编辑 `.env` 内容**区分，不提交 `.env` 到 Git。

**不再使用** `analysis/config.ini`、`app/config/production.cfg` 或任何 INI 文件。

初始化：

```bash
cp .env.example .env
# 编辑 .env：APP_ENV、DATABASE_URL、SECRET_KEY 等
```

在 `.env` 中用 `APP_ENV` 选择运行形态（未设置 `APP_SETTINGS` 时自动映射 Flask 配置类）：

| `APP_ENV` | Flask 类 |
|-----------|----------|
| `local` | `LocalConfig` |
| `development` | `DevelopmentConfig` |
| `production` | `ProductionConfig` |
| `test` | `TestingConfig` |

生产示例：同一文件，改 `APP_ENV=production`、`DEBUG=false`，并填写生产库与邮件等变量。

`manage.py`、`python -m compute` 启动时自动加载 `.env`；启动脚本也会 `source .env`。

注意：

- `.env` 含密钥，勿提交（已在 `.gitignore`）。
- 可用 `DOTENV_PATH` 指向其他路径（CI）。
- 可选 `APP_SETTINGS=app.config.XXX` 覆盖 `APP_ENV` 映射。
- Redis 连接解析仅支持普通 `redis://`；`rediss://` TLS 需扩展 `app/redis_op.py`。

## 7. 准备数据目录

Web 页面依赖部分 CSV 文件。即使暂时没有完整数据，也应先创建目录：

```bash
mkdir -p local_data/day_data
mkdir -p local_data/results
mkdir -p local_data/index_data
```

默认路径来自 `app/config.py`：

- `DAY_FILE_PATH=local_data/day_data`
- `RESULT_PATH=local_data/results`
- `INDEX_FILE_PATH=local_data/index_data`

也可以通过环境变量覆盖：

```bash
DAY_FILE_PATH=/data/twelvewin/day_data
RESULT_PATH=/data/twelvewin/results
INDEX_FILE_PATH=/data/twelvewin/index_data
```

注意：很多页面会直接读取结果 CSV。如果目录存在但文件缺失，应用可以启动，但相关页面可能显示为空或报错。

## 8. 启动 Redis

本地 Redis 示例：

```bash
redis-server
```

验证 Redis：

```bash
redis-cli ping
```

期望输出：

```text
PONG
```

如果 Redis 不在本机，更新 `.env`：

```bash
REDIS_URL=redis://:PASSWORD@REDIS_HOST:6379/0
```

## 9. 初始化或迁移数据库表

确认 `.env` 中 `DATABASE_URL` 已指向目标 PostgreSQL 数据库后执行：

### 9.1 新项目快速初始化

如果是全新数据库，可以用当前 SQLAlchemy 模型直接建表：

```bash
set -a
. ./.env
set +a
./.venv312/bin/python manage.py create_db
```

创建管理员账号：

```bash
set -a
. ./.env
set +a
./.venv312/bin/python manage.py create_admin
```

默认管理员账号由 `manage.py` 写死：

```text
email: ad@min.com
password: admin
```

上线前应立即修改默认密码，或改造 `create_admin()` 让账号和密码来自环境变量。

### 9.2 正式迁移流程

项目已预置 Flask-Migrate/Alembic 脚手架和初始 baseline revision。安装 `requirements-local.txt` 后可以使用：

```bash
set -a
. ./.env
set +a
export FLASK_APP=manage.py
TWELVEWIN_DISABLE_ANALYZER=1 flask db migrate -m "describe schema change"
TWELVEWIN_DISABLE_ANALYZER=1 flask db upgrade
```

注意：

- `create_db` 只适合全新数据库初始化，不负责生产 schema 演进。
- 已有数据库应优先使用 `flask db upgrade`。
- 第一次对已有生产库启用迁移前，先备份数据库，并确认 `migrations/versions/33e7716425a6_baseline_schema.py` 与线上表结构一致。
- 如果目标数据库已有旧表且没有 migration 记录，不要直接自动生成并执行破坏性 migration。

## 10. 本机启动验证

使用项目提供的 Python 3.12 启动脚本：

```bash
./start_local.sh
```

默认监听：

```text
http://127.0.0.1:8088
```

如果要指定端口：

```bash
PORT=8090 ./start_local.sh
```

另一个终端验证首页：

```bash
curl -I http://127.0.0.1:8088/
```

期望看到 `HTTP/1.1 200 OK` 或可解释的重定向/错误页面。

## 11. 生产进程管理示例

当前仓库没有为 Python 3.12 固化 `gunicorn` 或 `uwsgi` 依赖。最小可运行方式是用 `start_local.sh` 交给 systemd 管理；对公网生产环境，建议后续补充并验证正式 WSGI Server。

### 11.1 systemd service 示例

创建：

```text
/etc/systemd/system/twelvewin.service
```

内容示例：

```ini
[Unit]
Description=twelvewin Flask app
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/twelvewin
EnvironmentFile=/opt/twelvewin/.env
ExecStart=/opt/twelvewin/start_local.sh
Restart=always
RestartSec=5
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable twelvewin
sudo systemctl start twelvewin
sudo systemctl status twelvewin
```

查看日志：

```bash
sudo journalctl -u twelvewin -f
```

应用自身也会写入：

```text
flask.log
```

### 11.2 Nginx 反向代理示例

如果服务监听本机 `8088`，Nginx 可以代理到 Flask：

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用后检查配置：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 12. 发布新版本流程

每次发布建议按以下顺序执行：

```bash
cd /opt/twelvewin
git pull
./.venv312/bin/pip install -r requirements-local.txt
set -a
. ./.env
set +a
export FLASK_APP=manage.py
TWELVEWIN_DISABLE_ANALYZER=1 flask db upgrade
sudo systemctl restart twelvewin
sudo systemctl status twelvewin
```

然后做烟雾测试：

```bash
curl -I http://127.0.0.1:8088/
curl -s http://127.0.0.1:8088/ | head
```

如果接入 Nginx，也测试域名：

```bash
curl -I http://example.com/
```

## 13. 常见问题

### 13.1 安装依赖失败

确认使用的是：

```bash
./.venv312/bin/pip install -r requirements-local.txt
```

不要先安装历史 `requirements.txt`。其中包含旧版 Flask 扩展、旧版 SQLAlchemy 驱动和不适配 Python 3.12 的包。

### 13.2 数据库连接失败

检查：

- Neon 数据库是否启动
- 连接字符串是否使用 `postgresql+psycopg://`
- 是否包含 `sslmode=require`
- 用户名、密码、host、database 是否正确
- 服务器出站网络是否允许访问 Neon

### 13.3 页面启动正常但部分页面报错

优先检查 CSV 数据：

- `local_data/results`
- `local_data/day_data`
- `local_data/index_data`

该项目很多页面依赖离线分析脚本生成的 CSV 文件；数据库表存在不代表页面数据完整。

### 13.4 Redis 相关页面没有实时数据

检查 Redis：

```bash
redis-cli ping
```

再检查 `.env`：

```bash
REDIS_URL=redis://:PASSWORD@HOST:6379/0
```

实时行情数据需要额外脚本写入 Redis。Web 应用只负责读取 Redis 中已有的数据。

## 14. 部署检查清单

上线前确认：

- Python 版本是 3.12.x。
- `.venv312` 已创建并安装 `requirements-local.txt`。
- 根目录 `.env` 已配置（可从 `.env.example` 复制）。
- PostgreSQL/Neon 连接串使用 `postgresql+psycopg://`。
- Redis 可连接。
- `local_data/day_data`、`local_data/results`、`local_data/index_data` 已创建。
- 全新数据库已执行 `manage.py create_db`，或已有数据库已执行 `flask db upgrade`（含 `analysis_job_run` 表）。
- 默认管理员密码已修改。
- `curl -I http://127.0.0.1:8088/` 返回可接受结果。
- 如果对公网开放，已配置 Nginx、HTTPS 和进程守护。
