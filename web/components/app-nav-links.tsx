"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  {
    href: "/fundamentals?metric=pe",
    label: "基本面",
    match: /^\/fundamentals|^\/rankings|^\/value/,
  },
  {
    href: "/technical/highest",
    label: "技术面",
    match: /^\/technical/,
  },
  {
    href: "/clusters/sz50",
    label: "板块聚类",
    match: /^\/clusters/,
  },
  {
    href: "/business",
    label: "研究报告",
    match: /^\/business/,
  },
  {
    href: "/blog",
    label: "研究博客",
    match: /^\/blog/,
  },
  {
    href: "/register",
    label: "定价",
    match: /^\/register/,
  },
] as const;

export function AppNavLinks() {
  const pathname = usePathname();

  return (
    <nav className="nav-menu flex flex-wrap items-center gap-x-6 gap-y-2">
      {navLinks.map((link) => {
        const active = link.match.test(pathname);
        return (
          <Link
            key={link.href}
            href={link.href}
            className={active ? "nav-menu-link nav-menu-link-active" : "nav-menu-link"}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
