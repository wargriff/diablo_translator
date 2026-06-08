"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
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

  return (
    <div>
      <PageHeader
        title="History"
        subtitle="Chroniques des traductions passées"
        action={
          <button className="btn-ghost" onClick={() => void load()}>
            Actualiser
          </button>
        }
      />

      {loading ? (
        <p className="text-diablo-muted">Chargement…</p>
      ) : error ? (
        <div className="card">
          <p className="text-red-400">{error}</p>
          <button className="btn-primary mt-4" onClick={() => void load()}>
            Réessayer
          </button>
        </div>
      ) : messages.length === 0 ? (
        <p className="text-diablo-muted">Aucune chronique enregistrée.</p>
      ) : (
        <div className="space-y-3">
          {messages.map((msg) => (
            <article key={msg.id} className="card">
              <p className="text-[10px] text-diablo-muted">{msg.created_at}</p>
              <p className="mt-2">{msg.source_text}</p>
              <p className="mt-1 text-diablo-gold">{msg.translated_text}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
