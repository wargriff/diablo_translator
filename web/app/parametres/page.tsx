"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api, GAMES, LANGUAGES, type Settings, type SettingsUpdate } from "@/lib/api";

const TRANSLATORS = [
  { value: "google", label: "Google Translate" },
  { value: "deepl", label: "DeepL" },
];

const TOOL_LINKS = [
  { href: "/live", label: "Live OCR", desc: "Flux traduit en direct" },
  { href: "/history", label: "Historique", desc: "Toutes les traductions" },
  { href: "/statistics", label: "Statistiques", desc: "Compteurs & métriques" },
  { href: "/logs", label: "Logs", desc: "Journal de l'application" },
];

export default function ParametresPage() {
  const [form, setForm] = useState<Settings | null>(null);
  const [deeplKey, setDeeplKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void api
      .settings()
      .then(setForm)
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur API"))
      .finally(() => setLoading(false));
  }, []);

  function updateField<K extends keyof Settings>(key: K, value: Settings[K]) {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  async function save() {
    if (!form) return;
    setSaving(true);
    setStatus(null);
    setError(null);
    const payload: SettingsUpdate = {
      language: form.language,
      translator: form.translator,
      bidirectional_mode: form.bidirectional_mode,
      auto_detect_language: form.auto_detect_language,
      default_reply_language: form.default_reply_language,
      capture_fps: form.capture_fps,
      chat_monitor_enabled: form.chat_monitor_enabled,
      voice_input_enabled: form.voice_input_enabled,
      speak_translation: form.speak_translation,
      hub_sounds_enabled: form.hub_sounds_enabled,
      preferred_launch_game: form.preferred_launch_game,
      ocr_languages: form.ocr_languages,
    };
    if (deeplKey.trim()) {
      payload.deepl_api_key = deeplKey.trim();
    }
    try {
      const saved = await api.updateSettings(payload);
      setForm(saved);
      setDeeplKey("");
      setStatus("Paramètres enregistrés.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur sauvegarde");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Paramètres"
        subtitle="Configuration, modules et outils avancés"
        action={
          <button className="btn-primary" disabled={!form || saving} onClick={() => void save()}>
            {saving ? "Sauvegarde…" : "Enregistrer"}
          </button>
        }
      />

      <section className="mb-8 grid gap-3 sm:grid-cols-2">
        {TOOL_LINKS.map((item) => (
          <Link key={item.href} href={item.href} className="card transition hover:border-diablo-gold/50">
            <p className="font-cinzel text-sm text-diablo-gold">{item.label}</p>
            <p className="mt-1 text-xs text-diablo-muted">{item.desc}</p>
          </Link>
        ))}
      </section>

      <div className="card mb-6 border-diablo-gold/20">
        <p className="font-cinzel text-sm text-diablo-gold">Desktop OCR</p>
        <p className="mt-2 text-sm text-diablo-muted">
          Lancez <code>py -3 launcher.py gui</code> pour la capture chat en jeu (Diablo III / IV /
          Immortal).
        </p>
      </div>

      {loading ? (
        <p className="text-diablo-muted">Chargement…</p>
      ) : error && !form ? (
        <p className="text-red-400">{error}</p>
      ) : form ? (
        <div className="space-y-6">
          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">Langues</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="text-diablo-muted">Votre langue</span>
                <select
                  className="input mt-1"
                  value={form.language}
                  onChange={(e) => updateField("language", e.target.value)}
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="text-diablo-muted">Langue du jeu</span>
                <select
                  className="input mt-1"
                  value={form.default_reply_language}
                  onChange={(e) => updateField("default_reply_language", e.target.value)}
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label className="flex items-center gap-2 text-sm text-diablo-muted">
              <input
                type="checkbox"
                checked={form.bidirectional_mode}
                onChange={(e) => updateField("bidirectional_mode", e.target.checked)}
              />
              Traduction bidirectionnelle automatique (OCR)
            </label>
          </section>

          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">Moteur</h2>
            <select
              className="input"
              value={form.translator}
              onChange={(e) => updateField("translator", e.target.value)}
            >
              {TRANSLATORS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
            <label className="block text-sm">
              <span className="text-diablo-muted">Clé DeepL (optionnel)</span>
              <input
                className="input mt-1"
                type="password"
                value={deeplKey}
                onChange={(e) => setDeeplKey(e.target.value)}
                placeholder={form.deepl_api_key_set ? "Clé déjà configurée" : "sk-…"}
              />
            </label>
          </section>

          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">Jeu</h2>
            <select
              className="input"
              value={form.preferred_launch_game}
              onChange={(e) => updateField("preferred_launch_game", e.target.value)}
            >
              {GAMES.map((game) => (
                <option key={game.value} value={game.value}>
                  {game.label}
                </option>
              ))}
            </select>
          </section>

          {status ? <p className="text-sm text-emerald-400">{status}</p> : null}
          {error && form ? <p className="text-sm text-red-400">{error}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
