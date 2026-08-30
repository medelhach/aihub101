"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Front page" },
  { href: "/news", label: "News" },
  { href: "/articles", label: "Articles" },
  { href: "/models", label: "Models" },
  { href: "/compare", label: "Compare" },
];

export function HeaderNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Primary"
      className="flex flex-wrap items-center justify-center gap-x-1 gap-y-1 border-y border-rule py-2 text-[0.8rem] tracking-[0.14em] uppercase"
    >
      {links.map((link) => {
        const active =
          link.href === "/"
            ? pathname === "/"
            : pathname === link.href || pathname.startsWith(`${link.href}/`);
        return (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "px-3 py-1.5 text-ink/70 transition hover:text-crimson",
              active && "bg-ink text-paper hover:text-paper",
            )}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
