"use client";

import { useEffect, useState } from "react";
import { api, type SettingsResponse } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void api
      .settings()
      .then(setSettings)
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur API"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-xl">
      <h2 className="mb-4 text-xl font-semibold">Settings</h2>
      <div className="card space-y-3">
        <p>
          <span className="text-diablo-muted">API : </span>
          <code>http://127.0.0.1:8000</code> (proxy via Next.js)
        </p>
        {loading ? (
          <p className="text-diablo-muted">Chargement…</p>
        ) : error ? (
          <p className="text-red-400">{error}</p>
        ) : settings ? (
          <>
            <p>Langue : {settings.language}</p>
            <p>Traducteur : {settings.translator}</p>
            <p>Mode bidirectionnel : {settings.bidirectional_mode ? "Oui" : "Non"}</p>
          </>
        ) : null}
        <p className="text-sm text-diablo-muted">
          Modifiez la config dans le desktop PyQt6 ou <code>user_data/settings.json</code>.
        </p>
      </div>
    </div>
  );
}
