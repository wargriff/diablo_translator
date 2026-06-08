"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function ApiStatus() {
  const [online, setOnline] = useState(false);
  const [gameSummary, setGameSummary] = useState("—");

  useEffect(() => {
    async function poll() {
      try {
        await api.health();
        setOnline(true);
        const game = await api.gameStatus();
        setGameSummary(game.summary);
      } catch {
        setOnline(false);
        setGameSummary("API hors ligne");
      }
    }
    void poll();
    const timer = setInterval(() => void poll(), 8000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="mt-auto space-y-3 border-t border-diablo-border/60 pt-4">
      <div className="flex items-center gap-2 text-xs">
        <span className={`status-dot ${online ? "status-online" : "status-offline"}`} />
        <span className="text-diablo-muted">{online ? "Sanctuaire connecté" : "Lien rompu"}</span>
      </div>
      <p className="text-[11px] leading-relaxed text-diablo-muted">{gameSummary}</p>
    </div>
  );
}
