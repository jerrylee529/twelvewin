import { DashboardShell, PageHeader } from "@/components/dashboard-shell";
import { Button, Pane } from "@/components/ui/primitives";

export default function LoginPage() {
  return (
    <DashboardShell>
      <PageHeader
        title="登录"
        description="账户体系将在 Phase 3 接入，当前可先浏览公开榜单与单股研究页。"
      />
      <Pane variant="glass" className="max-w-lg p-5">
        <p className="text-xs leading-6 text-on-surface-variant">
          登录、注册、自选股与订阅功能尚未开放。你可以先从以下入口体验 MVP：
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button href="/rankings/pe" variant="primary">
            市盈率排行
          </Button>
          <Button href="/" variant="secondary">
            返回首页
          </Button>
        </div>
      </Pane>
    </DashboardShell>
  );
}
