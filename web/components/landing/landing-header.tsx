import Link from "next/link";
import { AppNavLinks } from "@/components/app-nav-links";

export function LandingHeader() {
  return (
    <header className="nav-header sticky top-0 z-50">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <AppNavLinks />

        <div className="nav-menu-actions flex shrink-0 items-center gap-4">
          <Link href="/login" className="nav-menu-link">
            登录
          </Link>
          <Link href="/register" className="nav-menu-cta">
            数据 API 接入
          </Link>
        </div>
      </div>
    </header>
  );
}
