# Month 1 Community Posts: Templates & CTR Tracking

Use these 10 post templates to test which ranking types drive the highest click-through rate on Xueqiu (雪球) and Jisilu (集思录).

## UTM convention

Append to every landing URL:

```
?utm_source={xueqiu|jisi}&utm_medium=post&utm_campaign=m1_{topic}&utm_content=post{N}
```

Example:

```
https://twelvewin.win/fundamentals?metric=pe&utm_source=xueqiu&utm_medium=post&utm_campaign=m1_pe_rank&utm_content=post1
```

## CTR tracking spreadsheet

| Post # | Platform | Topic | Landing URL | Publish date | Views | Clicks | CTR | Notes |
|--------|----------|-------|-------------|--------------|-------|--------|-----|-------|
| 1 | xueqiu | 低PE榜 | /fundamentals?metric=pe | | | | | |
| 2 | jisi | 低PE榜 | /fundamentals?metric=pe | | | | | |
| 3 | xueqiu | 突破均线 | /technical/break_ma | | | | | |
| 4 | jisi | 突破均线 | /technical/break_ma | | | | | |
| 5 | xueqiu | 白酒聚类 | /clusters/白酒 | | | | | |
| 6 | jisi | 新能源聚类 | /clusters/电气设备 | | | | | |
| 7 | xueqiu | 高ROE低PB | /fundamentals?metric=roe | | | | | |
| 8 | jisi | 高股息 | /fundamentals?metric=divi | | | | | |
| 9 | xueqiu | 茅台个股 | /stock/600519 | | | | | |
| 10 | jisi | 内在价值榜 | /value | | | | | |

Track clicks via analytics (UTM) or platform link stats. Compare CTR after 7 days.

---

## Post 1–2: Low PE ranking

**Title:** 今日 A 股低市盈率 Top 20（PE 5–20，日终更新）

**Body template:**

```
数据截至：{updateTime}

| 代码 | 名称 | PE | PB | ROE | 收盘价 |
|------|------|----|----|-----|--------|
{top_20_rows_markdown}

筛选条件：PE 5–20，按 PE 升序。
完整榜单（可筛选、导出）：{landing_url}

数据来源：团赢数据日终量化管道。
```

**API:** `GET /api/v1/fundamentals/screener?metric=pe&pe_min=5&pe_max=20&sort=pe_ttm&order=asc&page_size=20`

---

## Post 3–4: Break MA technical screen

**Title:** 今日突破 20 日均线个股一览

**Body template:**

```
数据截至：{updateTime}

以下个股收盘价突破 20 日均线：

{top_15_codes_and_names}

完整技术筛选列表：{landing_url}
```

**API:** `GET /api/v1/technical/break_ma` (take first 15 rows)

---

## Post 5–6: Industry cluster

**Title:** {行业}板块股票相关性聚类图解读

**Body template:**

```
{行业}板块 {stock_count} 只股票日终相关性聚类结果已更新。

聚类要点：
- 最大聚类：{cluster_1_name}（{n} 只）
- 高相关配对：{code_a} ↔ {code_b}（r={corr}）

交互式散点图、热力图：{landing_url}
```

**API:** `GET /api/v1/clusters/{industry}` + `/chart`

---

## Post 7: High ROE screen

**Title:** A 股高 ROE 标的筛选（ROE ≥ 10%）

**Landing:** `/fundamentals?metric=roe&utm_...`

**API:** `GET /api/v1/fundamentals/screener?metric=roe&roe_min=10&sort=roe&order=desc&page_size=20`

---

## Post 8: High dividend yield

**Title:** A 股高股息率 Top 20（股息率 ≥ 3%）

**Landing:** `/fundamentals?metric=divi&utm_...`

**API:** `GET /api/v1/fundamentals/screener?metric=divi&dividend_yield_min=3&page_size=20`

---

## Post 9: Single-stock deep dive (Moutai)

**Title:** 贵州茅台（600519）估值与财务快照

**Body template:**

```
{name}（{code}）
最新价：¥{close} | PE：{pe} | 52周：{low}–{high}

技术信号：{technical_signals}
行业基准：{industry_benchmark_summary}

完整研究页：{landing_url}
```

**API:** `GET /api/v1/stocks/600519/research-context`

---

## Post 10: Intrinsic value ranking

**Title:** 内在价值偏离度榜：哪些 A 股相对低估？

**Landing:** `/value?utm_...`

**API:** `GET /api/v1/rankings/value` (preview: `?preview=true` for top 20)

---

## Publishing SOP

1. Run `python -m compute eod_all` and confirm `GET /api/v1/data-status` is fresh.
2. Pull data from Research API (or use web page as reference).
3. Fill template; add 1 cluster screenshot for posts 5–6.
4. Publish on Xueqiu/Jisilu; record views after 24h and 7d.
5. Update CTR spreadsheet; identify winning topic for Month 2 newsletter focus.
