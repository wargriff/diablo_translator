"use client";

import { useEffect, useState } from "react";
import { api, LANGUAGES } from "@/lib/api";

type Props = {
  initialSource?: string;
  initialTarget?: string;
};

export function DeeplTranslator({ initialSource = "fr", initialTarget = "en" }: Props) {
  const [sourceLang, setSourceLang] = useState(initialSource);
  const [targetLang, setTargetLang] = useState(initialTarget);
  const [sourceText, setSourceText] = useState("");
  const [targetText, setTargetText] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void api.settings().then((settings) => {
      setSourceLang(settings.language);
      setTargetLang(settings.default_reply_language);
    }).catch(() => undefined);
  }, []);

  useEffect(() => {
    const value = sourceText.trim();
    if (!value) {
      setTargetText("");
      return;
    }
    const timer = setTimeout(() => {
      void api
        .compose(value, sourceLang, targetLang)
        .then((result) => setTargetText(result.translated_text))
        .catch(() => setTargetText(""));
    }, 350);
    return () => clearTimeout(timer);
  }, [sourceText, sourceLang, targetLang]);

  function swapLanguages() {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    if (targetText.trim()) {
      setSourceText(targetText);
      setTargetText(sourceText);
    }
  }

  async function copyResult() {
    if (!targetText.trim()) return;
    await navigator.clipboard.writeText(targetText);
    setStatus("Traduction copiée");
  }

  async function saveHistory() {
    const value = sourceText.trim();
    if (!value) return;
    setBusy(true);
    try {
      await api.translate(value, sourceLang, targetLang);
      setStatus("Enregistré dans l'historique");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erreur API");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-5xl">
      <div className="mb-4 flex flex-wrap items-center justify-center gap-3">
        <select
          className="input w-44"
          value={sourceLang}
          onChange={(event) => setSourceLang(event.target.value)}
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>

        <button
          type="button"
          className="btn-gold flex h-11 w-11 items-center justify-center rounded-full text-lg"
          onClick={swapLanguages}
          title="Inverser les langues"
          aria-label="Inverser les langues"
        >
          ⇄
        </button>

        <select
          className="input w-44"
          value={targetLang}
          onChange={(event) => setTargetLang(event.target.value)}
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <textarea
          className="input min-h-56 resize-y text-base"
          value={sourceText}
          onChange={(event) => setSourceText(event.target.value)}
          placeholder="Tapez votre message…"
        />
        <textarea
          className="input min-h-56 resize-y border-diablo-gold/30 bg-black/30 text-base text-diablo-gold"
          value={targetText}
          readOnly
          placeholder="Traduction…"
        />
      </div>

      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <button className="btn-primary" disabled={!targetText.trim()} onClick={() => void copyResult()}>
          Copier
        </button>
        <button
          className="btn-ghost"
          disabled={!sourceText.trim() || busy}
          onClick={() => void saveHistory()}
        >
          Enregistrer
        </button>
        <button
          className="btn-ghost"
          onClick={() => {
            setSourceText("");
            setTargetText("");
            setStatus(null);
          }}
        >
          Effacer
        </button>
      </div>

      {status ? <p className="mt-3 text-center text-sm text-diablo-muted">{status}</p> : null}
    </div>
  );
}
