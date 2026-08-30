import Link from "next/link";

import { HeaderNav } from "@/components/layout/header-nav";

export function Header() {
  const dated = new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date());

  return (
    <header className="bg-paper">
      <div className="mx-auto w-full max-w-[1280px] px-4 pt-5 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4 text-[0.7rem] tracking-[0.18em] text-ink/55 uppercase">
          <p>AI news · research · models</p>
          <p className="hidden sm:block">{dated}</p>
        </div>
        <div className="py-5 text-center">
          <p className="text-[0.7rem] font-semibold tracking-[0.42em] text-crimson uppercase">
            Independent briefing
          </p>
          <Link href="/" className="font-display mt-2 block text-4xl tracking-tight text-ink sm:text-5xl">
            The Intelligence Desk
          </Link>
          <p className="mt-2 text-sm text-ink/60">
            What changed in AI, why it matters, and which models to use.
          </p>
        </div>
        <HeaderNav />
      </div>
    </header>
  );
}
