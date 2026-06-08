"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api } from "@/lib/api";

export default function LogsPage() {
  const [lines, setLines] = useState<string[]>([]);
  const [path, setPath] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const payload = await api.logs(120);
      setLines(payload.lines);
      setPath(payload.path);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur API");
    }
  }

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(), 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="max-w-4xl">
      <PageHeader
        title="Logs"
        subtitle="Dernières lignes du journal applicatif"
        action={
          <button className="btn-ghost" onClick={() => void load()}>
            Actualiser
          </button>
        }
      />

      {path ? <p className="mb-4 text-xs text-diablo-muted">{path}</p> : null}
      {error ? <p className="text-red-400">{error}</p> : null}

      <pre className="card max-h-[60vh] overflow-auto font-mono text-xs leading-relaxed text-diablo-muted">
        {lines.length === 0 ? "Aucun log disponible." : lines.join("\n")}
      </pre>
    </div>
  );
}
