import { Button } from "@/components/ui/primitives";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="text-center">
        <p className="title-sm text-primary-container">404</p>
        <h1 className="display-sm mt-2 text-on-surface">页面不存在</h1>
        <p className="mt-2 text-xs text-on-surface-variant">
          请检查链接是否正确，或返回首页继续浏览。
        </p>
        <Button href="/" variant="primary" className="mt-6">
          返回首页
        </Button>
      </div>
    </div>
  );
}
