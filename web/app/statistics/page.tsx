"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api, type GameStatus, type Stats } from "@/lib/api";

export default function StatisticsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [game, setGame] = useState<GameStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([api.stats(), api.gameStatus()])
      .then(([s, g]) => {
        setStats(s);
        setGame(g);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur API"));
  }, []);

  return (
    <div className="max-w-3xl">
      <PageHeader title="Statistiques" subtitle="Métriques du Sanctuaire" />

      {error ? (
        <p className="text-red-400">{error}</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard label="Messages total" value={stats?.message_count ?? "—"} accent />
          <StatCard label="Messages récents" value={stats?.recent_count ?? "—"} />
          <StatCard label="Aujourd'hui" value={stats?.translations_today ?? "—"} />
          <StatCard label="Textes uniques" value={stats?.unique_sources ?? "—"} />
          <StatCard label="Traducteur" value={stats?.translator ?? "—"} />
          <StatCard label="Langue" value={stats?.language ?? "—"} />
          <StatCard label="API" value={stats?.api_version ?? "—"} />
          <StatCard
            label="Jeu détecté"
            value={game?.running ? game.games.map((g) => g.short_title).join(", ") : "Aucun"}
            wide
          />
        </div>
      )}

      {game ? (
        <p className="mt-6 text-sm text-diablo-muted">{game.summary}</p>
      ) : null}
    </div>
  );
}

function StatCard({
  label,
  value,
  accent,
  wide,
}: {
  label: string;
  value: string | number;
  accent?: boolean;
  wide?: boolean;
}) {
  return (
    <div
      className={`card text-center ${accent ? "border-diablo-gold/50 shadow-d4-gold" : ""} ${wide ? "sm:col-span-2 lg:col-span-1" : ""}`}
    >
      <p className="d4-subtitle">{label}</p>
      <p className={`mt-2 font-cinzel text-3xl ${accent ? "text-diablo-gold" : "text-gray-100"}`}>
        {value}
      </p>
    </div>
  );
}
