"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { api, type MessageItem } from "@/lib/api";

function mergeMessages(existing: MessageItem[], incoming: MessageItem[]): MessageItem[] {
  const map = new Map<number, MessageItem>();
  for (const item of [...incoming, ...existing]) {
    map.set(item.id, item);
  }
  return Array.from(map.values()).sort((a, b) => b.id - a.id);
}

export default function LivePage() {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [liveMode, setLiveMode] = useState<"websocket" | "poll">("poll");
  const socketRef = useRef<WebSocket | null>(null);

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

    let pollTimer: ReturnType<typeof setInterval> | null = null;
    let socket: WebSocket | null = null;

    function startPolling() {
      if (pollTimer) {
        return;
      }
      setLiveMode("poll");
      pollTimer = setInterval(() => void load(), 5000);
    }

    try {
      socket = new WebSocket(api.liveSocketUrl());
      socketRef.current = socket;

      socket.onopen = () => {
        setLiveMode("websocket");
        socket?.send("ping");
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as MessageItem & { type?: string };
          if (payload.type === "translation" && payload.id) {
            setMessages((current) => mergeMessages(current, [payload]));
          }
        } catch {
          void load();
        }
      };

      socket.onerror = () => {
        socket?.close();
      };

      socket.onclose = () => {
        startPolling();
      };
    } catch {
      startPolling();
    }

    return () => {
      if (pollTimer) {
        clearInterval(pollTimer);
      }
      socket?.close();
      socketRef.current = null;
    };
  }, []);

  return (
    <div>
      <PageHeader
        title="Live Chat"
        subtitle={
          liveMode === "websocket"
            ? "Flux temps réel via WebSocket"
            : "Flux via polling (5 s) — WebSocket indisponible"
        }
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
