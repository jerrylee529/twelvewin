import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Cpu,
  FileBarChart,
  Layers,
} from "lucide-react";
import { LandingFooter } from "@/components/landing/landing-footer";
import { LandingHeader } from "@/components/landing/landing-header";
import { LandingPreviewTable } from "@/components/landing/landing-preview-table";
import { Button } from "@/components/ui/primitives";

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

const philosophy = [
  {
    title: "极致密度",
    body: "以 12px 为主字号，单屏展示 50+ 行数据。每个像素都为信息传递服务。",
  },
  {
    title: "语义着色",
    body: "遵循 A 股红涨绿跌惯例。AI 洞察使用赛博紫高亮，避免纯白文字造成视觉疲劳。",
  },
  {
    title: "离线计算",
    body: "日终 Pipeline 写入数据库，Web 只读已发布结果，请求零计算、响应更稳定。",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-surface">
      <LandingHeader />

      <section className="hero-terminal-bg relative min-h-[520px] lg:min-h-[600px]">
        <div className="mx-auto flex max-w-[var(--container-max-width)] flex-col justify-center px-4 py-16 lg:px-8 lg:py-24">
          <p className="label-zh text-secondary">日终同步终端</p>
          <h1 className="display-lg mt-4 max-w-3xl text-on-surface">
            洞察 A 股，
            <span className="text-accent">智领量化</span>
          </h1>
          <p className="mt-5 max-w-xl body-md text-on-surface-variant">
            团赢数据为 A 股量化研究而生。日终自动更新的基本面排行、技术筛选与
            AI 聚类分析，集成于专业级预测终端工作台。
          </p>
          <div className="mt-8 flex flex-wrap gap-2">
            <Button href="/register" variant="primary">
              免费试用
            </Button>
            <Button href="/fundamentals?metric=pe" variant="outline">
              查看演示
            </Button>
          </div>
        </div>
      </section>

      <section className="bg-surface py-[var(--pane-margin)]">
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
                <h2 className="headline-md mt-4 text-on-surface">{feature.title}</h2>
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

      <LandingPreviewTable />

      <section className="bg-surface py-12 lg:py-16">
        <div className="mx-auto grid max-w-[var(--container-max-width)] gap-[var(--terminal-gap)] px-4 md:grid-cols-3 lg:px-8">
          {philosophy.map((item) => (
            <div key={item.title} className="terminal-pane-recessed p-5">
              <h3 className="headline-md text-on-surface">{item.title}</h3>
              <p className="mt-3 body-sm leading-relaxed text-on-surface-variant">
                {item.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-surface-container-low py-16 lg:py-20">
        <div className="mx-auto max-w-[var(--container-max-width)] px-4 text-center lg:px-8">
          <h2 className="display-sm text-on-surface">
            加入 5000+ 专业投资者的选择
          </h2>
          <p className="mx-auto mt-4 max-w-lg body-md text-on-surface-variant">
            从日终量化筛选到单股深度研究，团赢数据提供机构级信息密度与
            AI 驱动的研究效率。
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
            <Button href="/register" variant="primary">
              立即免费试用
            </Button>
            <Button href="/register" variant="outline">
              联系销售
            </Button>
          </div>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
