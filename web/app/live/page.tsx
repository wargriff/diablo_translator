"use client";

import { useEffect, useState } from "react";
import { api, type MessageItem } from "@/lib/api";

export default function LivePage() {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const items = await api.messages();
      setMessages(Array.isArray(items) ? items : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur API");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(), 5000);
    return () => clearInterval(timer);
  }, []);

  if (loading && messages.length === 0) {
    return <p className="text-diablo-muted">Chargement…</p>;
  }

  if (error) {
    return (
      <div className="card max-w-xl">
        <p className="text-red-400">{error}</p>
        <p className="mt-2 text-sm text-diablo-muted">
          Lancez l&apos;API : <code>py -3 launcher.py server</code>
        </p>
        <button className="btn-primary mt-4" onClick={() => void load()}>
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="mb-4 text-xl font-semibold">Live Chat</h2>
      <div className="space-y-3">
        {messages.length === 0 ? (
          <p className="text-diablo-muted">Aucun message pour le moment.</p>
        ) : (
          messages.map((msg) => (
            <article key={msg.id} className="card">
              <p className="text-xs uppercase text-diablo-gold">{msg.source_language ?? "?"}</p>
              <p className="mt-1 text-sm text-diablo-muted">{msg.source_text}</p>
              <p className="mt-2">{msg.translated_text}</p>
            </article>
          ))
        )}
      </div>
    </div>
  );
}
