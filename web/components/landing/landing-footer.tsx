import Link from "next/link";

const productLinks = [
  { href: "/fundamentals?metric=pe", label: "基本面分析" },
  { href: "/technical/highest", label: "技术面筛选" },
  { href: "/clusters/sz50", label: "向量聚类" },
  { href: "/business", label: "精选报告" },
];

const legalLinks = [
  { href: "/blog", label: "研究博客" },
  { href: "/register", label: "服务条款" },
  { href: "/register", label: "隐私政策" },
  { href: "/register", label: "数据免责声明" },
];

const connectLinks = [
  { href: "mailto:support@twelvewin.win", label: "support@twelvewin.win" },
  { href: "/register", label: "企业销售" },
];

export function LandingFooter() {
  return (
    <footer className="bg-surface-container-low">
      <div className="mx-auto grid max-w-[var(--container-max-width)] gap-8 px-4 py-12 md:grid-cols-4 lg:px-8">
        <div>
          <p className="text-sm font-bold text-on-surface">团赢数据</p>
          <p className="mt-2 max-w-xs body-sm leading-relaxed text-on-surface-variant">
            专业 A 股量化研究终端。日终数据、预计算筛选、机构级信息密度。
          </p>
        </div>

        <div>
          <p className="label-zh mb-3">产品</p>
          <ul className="space-y-2">
            {productLinks.map((link) => (
              <li key={link.label}>
                <Link
                  href={link.href}
                  className="body-sm text-on-surface-variant hover:text-on-surface"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="label-zh mb-3">法律与文档</p>
          <ul className="space-y-2">
            {legalLinks.map((link) => (
              <li key={link.label}>
                <Link
                  href={link.href}
                  className="body-sm text-on-surface-variant hover:text-on-surface"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="label-zh mb-3">联系我们</p>
          <ul className="space-y-2">
            {connectLinks.map((link) => (
              <li key={link.label}>
                <Link
                  href={link.href}
                  className="body-sm text-on-surface-variant hover:text-on-surface"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="bg-surface-container-lowest px-4 py-4 lg:px-8">
        <div className="mx-auto flex max-w-[var(--container-max-width)] flex-col gap-2 text-xs text-on-surface-variant sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} 团赢数据 保留所有权利</p>
          <p className="tabular-nums">日终同步 · 预测终端 v1.0</p>
        </div>
      </div>
    </footer>
  );
}
