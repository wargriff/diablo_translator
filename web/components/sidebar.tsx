"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/live", label: "Live" },
  { href: "/reply", label: "Reply" },
  { href: "/history", label: "History" },
  { href: "/statistics", label: "Statistics" },
  { href: "/settings", label: "Settings" },
  { href: "/logs", label: "Logs" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 border-r border-diablo-border bg-diablo-panel p-4">
      <h1 className="mb-6 text-lg font-bold text-diablo-gold">Diablo Translator</h1>
      <nav className="flex flex-col gap-1">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "rounded-lg px-3 py-2 text-sm transition",
              pathname === link.href
                ? "bg-diablo-accent text-white"
                : "text-diablo-muted hover:bg-white/5 hover:text-white",
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
