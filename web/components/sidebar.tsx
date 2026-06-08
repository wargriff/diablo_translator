"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ApiStatus } from "@/components/api-status";

const links = [
  { href: "/", label: "Sanctuaire", icon: "⛧" },
  { href: "/live", label: "Live", icon: "◈" },
  { href: "/reply", label: "Reply", icon: "✦" },
  { href: "/history", label: "History", icon: "☗" },
  { href: "/statistics", label: "Stats", icon: "◆" },
  { href: "/settings", label: "Rites", icon: "⚙" },
  { href: "/logs", label: "Logs", icon: "☰" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 flex-col border-r border-diablo-borderGold/30 bg-diablo-panel/95 p-4 backdrop-blur-sm">
      <div className="mb-8 text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-sm border border-diablo-gold/40 bg-diablo-accent/20 text-xl text-diablo-gold shadow-d4-gold">
          ⛧
        </div>
        <h1 className="font-cinzel text-sm font-bold uppercase tracking-[0.25em] text-diablo-gold">
          Diablo
        </h1>
        <p className="text-[10px] uppercase tracking-widest text-diablo-muted">Translator IV</p>
      </div>

      <nav className="flex flex-col gap-1">
        {links.map((link) => {
          const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn("nav-link", active && "nav-link-active")}
            >
              <span className="text-diablo-goldDim">{link.icon}</span>
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="my-4 border-t border-diablo-border/40" />

      <Link href="/live" className="btn-primary mb-2 w-full text-center">
        Entrer — Start
      </Link>

      <ApiStatus />
    </aside>
  );
}
