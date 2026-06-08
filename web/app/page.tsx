"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function HomePage() {
  const [online, setOnline] = useState(false);
  const [version, setVersion] = useState("");
  const [gameSummary, setGameSummary] = useState("Scan des royaumes…");

  useEffect(() => {
    void api
      .health()
      .then((payload) => {
        setOnline(true);
        setVersion(payload.version ?? "2.x");
      })
      .catch(() => setOnline(false));

    void api
      .gameStatus()
      .then((game) => setGameSummary(game.summary))
      .catch(() => setGameSummary("API non disponible"));
  }, []);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center text-center">
      <div className="card max-w-2xl border-diablo-gold/40 p-10 shadow-d4-gold">
        <p className="d4-subtitle mb-4 ember-glow">Bienvenue au Sanctuaire</p>
        <h1 className="font-cinzel text-4xl font-bold uppercase tracking-[0.15em] text-diablo-gold md:text-5xl">
          Diablo Translator
        </h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-diablo-muted">
          Traduction en temps réel pour Diablo III, IV et Immortal. OCR du chat, réponses rapides,
          historique et rites de configuration — style Diablo IV.
        </p>

        <div className="my-8 grid gap-3 text-left sm:grid-cols-3">
          {[
            { title: "Live", desc: "Flux OCR traduit", href: "/live" },
            { title: "Reply", desc: "Composer & copier", href: "/reply" },
            { title: "Rites", desc: "Paramètres éditables", href: "/settings" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="d4-frame block p-4 transition hover:border-diablo-gold/70 hover:shadow-d4-gold"
            >
              <p className="font-cinzel text-sm text-diablo-gold">{item.title}</p>
              <p className="mt-1 text-xs text-diablo-muted">{item.desc}</p>
            </Link>
          ))}
        </div>

        <div className="mb-8 space-y-2 text-xs text-diablo-muted">
          <p>
            Statut API :{" "}
            <span className={online ? "text-emerald-400" : "text-red-400"}>
              {online ? `Connecté v${version}` : "Hors ligne — lancez py -3 launcher.py server"}
            </span>
          </p>
          <p>{gameSummary}</p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link href="/live" className="btn-primary-lg">
            ⛧ Entrer dans le Sanctuaire
          </Link>
          <Link href="/settings" className="btn-ghost">
            Configurer les rites
          </Link>
        </div>
      </div>

      <p className="mt-8 text-[11px] uppercase tracking-[0.3em] text-diablo-goldDim/60">
        For Sanctuary — Multilingual
      </p>
    </div>
  );
}
