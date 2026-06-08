"use client";

import { useEffect, useState } from "react";
import { api, type QuickReply } from "@/lib/api";

export default function ReplyPage() {
  const [text, setText] = useState("");
  const [preview, setPreview] = useState("");
  const [quick, setQuick] = useState<QuickReply[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    void api.quickReplies().then(setQuick).catch(() => setQuick([]));
  }, []);

  useEffect(() => {
    const value = text.trim();
    if (!value) {
      setPreview("");
      return;
    }
    const timer = setTimeout(() => {
      void api
        .compose(value)
        .then((result) => setPreview(result.translated_text))
        .catch(() => setPreview(""));
    }, 400);
    return () => clearTimeout(timer);
  }, [text]);

  async function copy(clear = false) {
    if (!preview) return;
    await navigator.clipboard.writeText(preview);
    setStatus("Texte copié");
    if (clear) {
      setText("");
      setPreview("");
    }
  }

  async function save() {
    const value = text.trim();
    if (!value) return;
    try {
      await api.translate(value);
      setStatus("Traduction enregistrée");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Erreur");
    }
  }

  return (
    <div className="max-w-2xl">
      <h2 className="mb-4 text-xl font-semibold">Reply</h2>
      <textarea
        className="input min-h-28"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Bonjour, comment vas-tu ?"
      />
      <div className="card mt-4">
        <p className="text-sm text-diablo-gold">Aperçu traduit</p>
        <p className="mt-2 text-lg">{preview || "…"}</p>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn-primary" disabled={!preview} onClick={() => void copy()}>
          Copier
        </button>
        <button className="btn-ghost" disabled={!preview} onClick={() => void copy(true)}>
          Copier et effacer
        </button>
        <button className="btn-ghost" disabled={!text.trim()} onClick={() => void save()}>
          Enregistrer
        </button>
      </div>
      {status ? <p className="mt-3 text-sm text-diablo-muted">{status}</p> : null}
      <h3 className="mb-2 mt-8 font-semibold">Réponses rapides</h3>
      <div className="flex flex-wrap gap-2">
        {quick.map((item) => (
          <button
            key={item.key}
            className="btn-ghost"
            onClick={() => {
              setText(item.label);
              setPreview(item.translated_text);
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
