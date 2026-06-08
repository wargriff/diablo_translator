"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ApiStatus } from "@/components/api-status";

const links = [
  { href: "/reply", label: "Traduction", icon: "✦" },
  { href: "/history", label: "Historique", icon: "☗" },
  { href: "/parametres", label: "Paramètres", icon: "⚙" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-52 flex-col border-r border-diablo-borderGold/30 bg-diablo-panel/95 p-4 backdrop-blur-sm">
      <div className="mb-8 text-center">
        <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-sm border border-diablo-gold/40 bg-diablo-accent/20 text-lg text-diablo-gold">
          ⛧
        </div>
        <h1 className="font-cinzel text-xs font-bold uppercase tracking-[0.2em] text-diablo-gold">
          Diablo Translator
        </h1>
      </div>

      <nav className="flex flex-col gap-1">
        {links.map((link) => {
          const active =
            pathname === link.href ||
            (link.href !== "/reply" && pathname.startsWith(link.href));
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
      <ApiStatus />
    </aside>
  );
}
