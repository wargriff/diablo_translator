"use client";

import { useEffect, useState } from "react";
import { api, type MessageItem } from "@/lib/api";

export default function HistoryPage() {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setMessages(await api.messages(100));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur API");
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (loading) {
    return <p className="text-diablo-muted">Chargement…</p>;
  }

  return (
    <div>
      <h2 className="mb-4 text-xl font-semibold">History</h2>
      {error ? (
        <div className="card max-w-xl">
          <p className="text-red-400">{error}</p>
          <p className="mt-2 text-sm text-diablo-muted">
            Lancez l&apos;API : <code>py -3 launcher.py server</code>
          </p>
          <button className="btn-primary mt-4" onClick={() => void load()}>
            Réessayer
          </button>
        </div>
      ) : messages.length === 0 ? (
        <p className="text-diablo-muted">Aucun message en historique.</p>
      ) : (
        <div className="space-y-3">
          {messages.map((msg) => (
            <article key={msg.id} className="card">
              <p className="text-xs text-diablo-muted">{msg.created_at}</p>
              <p className="mt-1">{msg.source_text}</p>
              <p className="mt-1 text-diablo-gold">{msg.translated_text}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
