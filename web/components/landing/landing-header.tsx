import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";
import { Button } from "@/components/ui/primitives";

const navLinks = [
  { href: "/fundamentals?metric=pe", label: "基本面" },
  { href: "/technical/highest", label: "技术面" },
  { href: "/clusters/sz50", label: "板块聚类" },
  { href: "/business", label: "研究报告" },
  { href: "/register", label: "定价" },
];

export function LandingHeader() {
  return (
    <header className="sticky top-0 z-50 bg-surface/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[var(--container-max-width)] items-center justify-between px-4 lg:px-8">
        <Link href="/" className="flex items-center">
          <BrandLogo />
        </Link>

        <nav className="hidden items-center gap-6 lg:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-on-surface-variant transition hover:text-on-surface"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm text-on-surface-variant transition hover:text-on-surface"
          >
            登录
          </Link>
          <Button href="/register" variant="primary" className="!px-4 !py-2">
            免费试用
          </Button>
        </div>
      </div>
    </header>
  );
}
