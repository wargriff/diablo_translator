"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function StatisticsPage() {
  const [count, setCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void api
      .messages(200)
      .then((messages) => setCount(messages.length))
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur API"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-xl">
      <h2 className="mb-4 text-xl font-semibold">Statistics</h2>
      <div className="card">
        {loading ? (
          <p className="text-diablo-muted">Chargement…</p>
        ) : error ? (
          <p className="text-red-400">{error}</p>
        ) : (
          <>
            <p className="text-3xl font-bold text-diablo-gold">{count}</p>
            <p className="text-diablo-muted">messages récents en historique</p>
          </>
        )}
      </div>
    </div>
  );
}
