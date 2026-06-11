# Month 1 SEO: Search Console Submission

After deploying the SEO infrastructure (`sitemap.xml`, `robots.txt`, page metadata), submit the site to search engines.

## Prerequisites

1. Set `NEXT_PUBLIC_SITE_URL` to your production domain (e.g. `https://twelvewin.com`).
2. Deploy web with API reachable from the build/runtime (sitemap fetches `/api/v1/stocks/list`).
3. Verify endpoints:
   - `curl -s https://YOUR_DOMAIN/robots.txt`
   - `curl -s https://YOUR_DOMAIN/sitemap.xml | head`
   - `curl -s https://YOUR_DOMAIN/stock/600519 | grep -E '<title>|<h1>|description'`

## Google Search Console

1. Go to [Google Search Console](https://search.google.com/search-console).
2. Add property → URL prefix → enter `https://YOUR_DOMAIN`.
3. Verify ownership (DNS TXT record or HTML file upload).
4. Sitemaps → submit `https://YOUR_DOMAIN/sitemap.xml`.
5. URL Inspection → test `/stock/600519` and `/fundamentals?metric=pe` for indexability.
6. Monitor **Coverage** and **Performance** weekly.

## Bing Webmaster Tools

1. Go to [Bing Webmaster Tools](https://www.bing.com/webmasters).
2. Add site and verify (can import from Google Search Console).
3. Submit sitemap: `https://YOUR_DOMAIN/sitemap.xml`.

## Baidu Webmaster (百度站长)

1. Go to [百度搜索资源平台](https://ziyuan.baidu.com/).
2. Add site and verify (HTML file or CNAME).
3. 链接提交 → sitemap → `https://YOUR_DOMAIN/sitemap.xml`.
4. Use「普通收录」API if you need programmatic URL push for new stocks.

## Expected sitemap size

| URL type | Approx. count |
|----------|---------------|
| Stock detail `/stock/{code}` | 500–5000+ (from `instrument` table) |
| Fundamental screens | 4 |
| Technical screens | 5 |
| Price-change periods | 5 |
| Value ranking | 1 |
| Business | 1 |
| Index clusters | 3 |
| Industry clusters | 30–100+ |

Total should exceed **500+ stock pages** and **20+ list pages** when DB is populated.

## Indexing checklist

- [ ] `robots.txt` allows crawlers and points to sitemap
- [ ] Stock pages return unique `<title>` and `<meta name="description">`
- [ ] Stock pages render `<h1>` with company name in server HTML
- [ ] List pages have canonical URLs and `ItemList` JSON-LD
- [ ] Sitemap submitted to Google, Bing, and Baidu
