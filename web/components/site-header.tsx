"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, Search } from "lucide-react";
import { BrandLogo } from "@/components/brand-logo";
import {
  isNavChildActive,
  primaryNavTabs,
} from "@/lib/navigation";
import { StockSearch } from "@/components/stock-search";

export function SiteHeader({
  variant = "dashboard",
}: {
  variant?: "dashboard" | "marketing";
}) {
  const pathname = usePathname();

  if (variant === "marketing") {
    return (
      <header className="border-b border-on-surface/5 bg-surface-container-low">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between px-4 py-3">
          <Link href="/" className="flex items-center">
            <BrandLogo />
          </Link>
          <div className="flex items-center gap-2 text-xs">
            <Link href="/fundamentals?metric=pe" className="px-2 py-1 text-on-surface-variant hover:text-on-surface">
              进入终端
            </Link>
            <Link href="/login" className="btn-gradient-primary px-3 py-1.5 text-xs font-medium">
              登录
            </Link>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="border-b border-on-surface/5 bg-surface-container-low">
      <div className="flex h-12 items-stretch">
        <Link
          href="/"
          className="flex w-56 shrink-0 items-center border-r border-on-surface/5 px-4 transition hover:opacity-90"
        >
          <BrandLogo />
        </Link>

        <div className="nav-menu flex min-w-0 flex-1 items-center gap-1 overflow-visible px-2">
          {primaryNavTabs.map((tab) => {
            const active = tab.match.test(pathname);
            const children = "children" in tab ? tab.children : undefined;

            if (children) {
              return (
                <div key={tab.href} className="group relative flex items-stretch">
                  <Link
                    href={tab.href}
                    className={`nav-menu-link flex items-center gap-1 whitespace-nowrap px-3 py-3 transition ${
                      active ? "nav-menu-link-active border-b-2" : ""
                    }`}
                  >
                    {tab.label}
                    <ChevronDown className="h-3 w-3 transition group-hover:rotate-180 group-focus-within:rotate-180" />
                  </Link>
                  <div className="invisible absolute left-0 top-full z-50 min-w-36 rounded-md border border-on-surface/10 bg-surface-container-lowest py-1 opacity-0 shadow-xl transition group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100">
                    {children.map((child) => {
                      const childActive = isNavChildActive(pathname, child);

                      return (
                        <Link
                          key={child.href}
                          href={child.href}
                          className={`nav-menu-link block whitespace-nowrap px-3 py-2 transition ${
                            childActive
                              ? "nav-menu-link-active bg-surface-container-high"
                              : "hover:bg-surface-container-highest"
                          }`}
                        >
                          {child.label}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            }

            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`nav-menu-link whitespace-nowrap px-3 py-3 transition ${
                  active ? "nav-menu-link-active border-b-2" : ""
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center gap-3 border-l border-on-surface/5 px-4">
          <div className="hidden w-52 items-center gap-2 rounded-md bg-surface-container-lowest px-2 py-1.5 md:flex">
            <Search className="h-3.5 w-3.5 shrink-0 text-on-surface-variant" />
            <div className="min-w-0 flex-1 [&_input]:border-none [&_input]:bg-transparent [&_input]:px-0 [&_input]:py-0 [&_input]:text-xs">
              <StockSearch compact />
            </div>
          </div>
          <Link href="/register" className="nav-menu-link hidden sm:inline">
            注册
          </Link>
          <Link href="/login" className="nav-menu-cta">
            登录
          </Link>
        </div>
      </div>
    </header>
  );
}

export const sidebarSections = [];
