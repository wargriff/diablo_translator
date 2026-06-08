"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
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

  return (
    <div>
      <PageHeader
        title="Live Chat"
        subtitle="Flux des traductions OCR en temps réel"
        action={
          <button className="btn-ghost" onClick={() => void load()}>
            Actualiser
          </button>
        }
      />

      {loading && messages.length === 0 ? (
        <p className="text-diablo-muted">Invocation du flux…</p>
      ) : error ? (
        <div className="card max-w-xl border-red-900/40">
          <p className="text-red-400">{error}</p>
          <p className="mt-2 text-sm text-diablo-muted">
            <Link href="/" className="text-diablo-gold hover:underline">
              Retour au Sanctuaire
            </Link>{" "}
            ou lancez <code>py -3 launcher.py server</code>
          </p>
          <button className="btn-primary mt-4" onClick={() => void load()}>
            Réessayer
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="card text-center text-diablo-muted">
              <p>Aucun message — traduisez depuis Reply ou lancez le desktop OCR.</p>
              <Link href="/reply" className="btn-gold mt-4 inline-flex">
                Composer une réponse
              </Link>
            </div>
          ) : (
            messages.map((msg) => (
              <article key={msg.id} className="card border-l-2 border-l-diablo-accentBright">
                <p className="text-[10px] uppercase tracking-widest text-diablo-gold">
                  {msg.source_language ?? "?"} → {msg.target_language ?? "?"}
                </p>
                <p className="mt-2 text-sm text-diablo-muted">{msg.source_text}</p>
                <p className="mt-2 font-medium text-gray-100">{msg.translated_text}</p>
              </article>
            ))
          )}
        </div>
      )}
    </div>
  );
}
