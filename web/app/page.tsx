import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Cpu,
  FileBarChart,
  Layers,
} from "lucide-react";
import { HomeSearchHero } from "@/components/home-search-hero";
import { LandingFooter } from "@/components/landing/landing-footer";
import { LandingHeader } from "@/components/landing/landing-header";

const features = [
  {
    title: "基本面分析",
    description:
      "市盈率、市净率、ROE、股息率等维度日终更新，快速缩小 A 股研究范围。",
    href: "/fundamentals?metric=pe",
    icon: BarChart3,
  },
  {
    title: "技术面筛选",
    description:
      "历史新高、均线多头、突破均线、涨跌幅等预计算榜单，辅助趋势判断。",
    href: "/technical/highest",
    icon: Layers,
  },
  {
    title: "AI 向量聚类",
    description:
      "指数与行业聚类分析，揭示 A 股市场中的结构性关联与板块关系。",
    href: "/clusters/sz50",
    icon: Cpu,
  },
  {
    title: "年度量化报告",
    description:
      "个股与行业年度表现报告，支持深度研究与历史回溯分析工作流。",
    href: "/business",
    icon: FileBarChart,
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-surface">
      <LandingHeader />
      <HomeSearchHero />

      <section className="border-t border-on-surface/5 bg-surface py-[var(--pane-margin)]">
        <div className="mx-auto mb-8 max-w-[var(--container-max-width)] px-4 text-center lg:px-8">
          <p className="label-zh text-secondary">研究终端</p>
          <h2 className="headline-md mt-2 text-on-surface">探索更多分析模块</h2>
        </div>
        <div className="mx-auto grid max-w-[var(--container-max-width)] gap-[var(--terminal-gap)] px-4 sm:grid-cols-2 lg:grid-cols-4 lg:px-8">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.href}
                href={feature.href}
                className="terminal-pane group flex flex-col p-4 transition hover:bg-surface-container-high"
              >
                <Icon className="h-5 w-5 text-secondary" strokeWidth={1.5} />
                <h3 className="headline-md mt-4 text-on-surface">
                  {feature.title}
                </h3>
                <p className="mt-2 flex-1 body-sm leading-relaxed text-on-surface-variant">
                  {feature.description}
                </p>
                <span className="mt-4 inline-flex items-center gap-1 text-sm text-secondary group-hover:text-on-surface">
                  进入模块
                  <ArrowRight className="h-3.5 w-3.5" />
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
