import { DashboardShell, PageHeader } from "@/components/dashboard-shell";
import { Button, Pane } from "@/components/ui/primitives";

export default function RegisterPage() {
  return (
    <DashboardShell>
      <PageHeader
        title="注册"
        description="SaaS 账户注册将在下一阶段开放。"
      />
      <Pane variant="glass" className="max-w-lg p-5">
        <p className="text-xs leading-6 text-on-surface-variant">
          当前版本聚焦数据浏览与研究工作流验证。若已有账号，请等待 Phase 3 正式接入
          Auth。
        </p>
        <Button href="/login" variant="primary" className="mt-4">
          前往登录说明
        </Button>
      </Pane>
    </DashboardShell>
  );
}
