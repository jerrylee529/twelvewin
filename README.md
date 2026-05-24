# Twelvewin（团赢数据）

Twelvewin 是一个 **A 股日终量化研究终端** 的开源项目：收盘后自动计算基本面、技术面与板块结构榜单，通过 Web 终端浏览与筛选，支持自部署。

**许可证：[Apache License 2.0](LICENSE)**

> 本仓库为 **开源社区版（Community）**，包含核心数据管道、Research API 与研究终端 UI。  
> 账户体系、云托管、订阅计费等商业化能力在独立产品中开发，不包含在本开源发行版内。

---

## 功能概览

| 模块 | 说明 |
|------|------|
| **基本面** | 市盈率 / 市净率 / ROE / 股息率排行与多维 screener |
| **技术面** | 历史新高/新低、均线多头、突破均线、年线之上、涨跌幅筛选 |
| **板块聚类** | 上证50、沪深300、中证500及行业聚类 |
| **行业分析** | 业务价值与标签筛选结果 |
| **单股研究** | K 线、财务画像、实时行情补充（Redis） |

---

## 架构

```text
Market data (AkShare / Tushare / …)
        │
        ▼
compute/ + jobs/ + analysis/     ← 离线日终计算，写入 Postgres
        │
        ▼
api/ (FastAPI, 只读)              ← Research API  :8090
        │
        ▼
web/ (Next.js)                    ← 研究终端 UI   :3000

app/ (Flask, legacy)              ← 旧版单体 UI，维护模式，非 OSS 推荐路径
```

数据流：`python -m compute eod_all` → Postgres（`analysis_runs`、`ranking_results` 等）→ API → Web。

---

## 快速开始（Docker，推荐）

**前置：** Docker Engine 24+、Docker Compose v2

```bash
git clone <YOUR_REPO_URL> twelvewin
cd twelvewin

cp .env.docker.example .env
# 编辑 .env：至少修改 SECRET_KEY、SECURITY_PASSWORD_SALT

docker compose up -d --build
```

访问：

- **Web 终端：** http://localhost:3000
- **API 文档：** http://localhost:8090/docs

首次启动表格为空，需发布分析数据：

```bash
docker compose --profile jobs run --rm eod
```

（需在 `.env` 中配置 `TUSHARE_TOKEN` 等行情数据源，详见 [docs/DOCKER.md](docs/DOCKER.md)）

---

## 本地开发

### 1. 环境

- Python 3.12+
- Node.js 20+
- PostgreSQL 14+（或 Neon）
- Redis 6+（可选，用于 K 线页实时行情）

```bash
cp .env.example .env
# 配置 DATABASE_URL、REDIS_URL 等
```

### 2. 数据库迁移

```bash
pip install -r requirements-local.txt
export FLASK_APP=manage.py TWELVEWIN_DISABLE_ANALYZER=1
flask db upgrade
```

### 3. 发布分析数据

```bash
pip install -r requirements-analysis.txt
python -m compute eod_all
```

### 4. 启动 API

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8090
```

### 5. 启动 Web

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

打开 http://localhost:3000

---

## 仓库结构

| 路径 | 说明 |
|------|------|
| [`compute/`](compute/) | 离线任务 CLI（`eod_all`、`ranking_pipeline` 等） |
| [`jobs/`](jobs/) | Pipeline 编排 |
| [`analysis/`](analysis/) | 行情下载、技术分析、聚类、估值计算 |
| [`core/`](core/) | 数据库、schema、artifacts 契约 |
| [`api/`](api/) | FastAPI Research API（开源主后端） |
| [`web/`](web/) | Next.js 研究终端 |
| [`docker/`](docker/) | Dockerfile 与 Compose 配套 |
| [`app/`](app/) | **Legacy** Flask 应用（Jinja + 用户登录） |
| [`tests/`](tests/) | 单元测试 |
| [`docs/`](docs/) | 补充文档 |

---

## 文档

| 文档 | 内容 |
|------|------|
| [docs/DOCKER.md](docs/DOCKER.md) | Docker 自部署 |
| [api/README.md](api/README.md) | Research API 端点 |
| [web/README.md](web/README.md) | 前端开发说明 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 历史架构（含 Flask 细节） |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 传统 Flask 部署（legacy） |
| [ROADMAP.md](ROADMAP.md) | 演进路线 |
| [DESIGN.md](DESIGN.md) | Web UI 设计规范 |
| [docs/menu-pages-data-sources.md](docs/menu-pages-data-sources.md) | 页面与数据表对照 |

---

## 测试

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

---

## 开源范围说明

**包含（Community）：**

- 日终计算与 Postgres 发布
- Research API（只读分析接口）
- Web 研究终端（基本面 / 技术面 / 板块 / 单股）
- Docker 自部署

**不包含（商业版 / 后续独立仓库）：**

- 用户注册登录、邮箱验证、订阅支付
- 自选股云同步、团队空间、SSO
- 官方托管 Cloud 与托管 pipeline

Legacy Flask 中的 `app/user/`、`self_selected_stock/` 等仅作参考，新功能请不要再基于 Flask 扩展。

---

## 贡献

欢迎提交 Issue 与 Pull Request。贡献代码即表示同意以 [Apache 2.0](LICENSE) 许可证发布。

---

## 相关链接

- 设计系统：见 [DESIGN.md](DESIGN.md)（Predictive Terminal 深色终端风格）
- 生产站点（示例）：https://twelvewin.win
