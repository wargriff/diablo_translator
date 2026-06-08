"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api, type QuickReply } from "@/lib/api";

export default function ReplyPage() {
  const [text, setText] = useState("");
  const [preview, setPreview] = useState("");
  const [quick, setQuick] = useState<QuickReply[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

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
        .then((r) => setPreview(r.translated_text))
        .catch(() => setPreview(""));
    }, 400);
    return () => clearTimeout(timer);
  }, [text]);

  async function copy(clear = false) {
    if (!preview) return;
    await navigator.clipboard.writeText(preview);
    setStatus("Texte copié dans le presse-papiers");
    if (clear) {
      setText("");
      setPreview("");
    }
  }

  async function save() {
    const value = text.trim();
    if (!value) return;
    setBusy(true);
    try {
      await api.translate(value);
      setStatus("Traduction scellée dans l'historique");
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Erreur");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <PageHeader title="Reply" subtitle="Composez, traduisez et copiez vos réponses" />

      <textarea
        className="input min-h-32 font-medium"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Bonjour, prêt pour le donjon ?"
      />

      <div className="card mt-4 border-diablo-gold/30">
        <p className="d4-subtitle">Aperçu traduit</p>
        <p className="mt-3 min-h-[2rem] text-lg text-diablo-gold">{preview || "…"}</p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn-primary" disabled={!preview} onClick={() => void copy()}>
          Copier
        </button>
        <button className="btn-ghost" disabled={!preview} onClick={() => void copy(true)}>
          Copier & effacer
        </button>
        <button className="btn-gold" disabled={!text.trim() || busy} onClick={() => void save()}>
          Enregistrer
        </button>
      </div>

      {status ? <p className="mt-3 text-sm text-diablo-muted">{status}</p> : null}

      <h3 className="mb-3 mt-10 font-cinzel text-sm uppercase tracking-widest text-diablo-gold">
        Réponses rapides
      </h3>
      <div className="flex flex-wrap gap-2">
        {quick.map((item) => (
          <button
            key={item.key}
            className="btn-ghost text-xs"
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
