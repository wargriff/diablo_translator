"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { api, GAMES, LANGUAGES, type Settings, type SettingsUpdate } from "@/lib/api";

const TRANSLATORS = [
  { value: "google", label: "Google Translate" },
  { value: "deepl", label: "DeepL" },
];

export default function SettingsPage() {
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
      setStatus("Rites enregistrés — synchronisés avec le desktop.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur sauvegarde");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Rites & Paramètres"
        subtitle="Modifiez la configuration — sauvegardée dans user_data/settings.json"
        action={
          <button className="btn-primary" disabled={!form || saving} onClick={() => void save()}>
            {saving ? "Invocation…" : "Enregistrer"}
          </button>
        }
      />

      {loading ? (
        <p className="text-diablo-muted">Chargement des rites…</p>
      ) : error && !form ? (
        <div className="card border-red-900/50">
          <p className="text-red-400">{error}</p>
          <p className="mt-2 text-sm text-diablo-muted">
            Lancez l&apos;API : <code>py -3 launcher.py server</code>
          </p>
        </div>
      ) : form ? (
        <div className="space-y-6">
          {status ? <p className="text-sm text-emerald-400">{status}</p> : null}
          {error ? <p className="text-sm text-red-400">{error}</p> : null}

          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">
              ◈ Traduction
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Langue cible</label>
                <select
                  className="select"
                  value={form.language}
                  onChange={(e) => updateField("language", e.target.value)}
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Traducteur</label>
                <select
                  className="select"
                  value={form.translator}
                  onChange={(e) => updateField("translator", e.target.value)}
                >
                  {TRANSLATORS.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Langue des réponses</label>
                <select
                  className="select"
                  value={form.default_reply_language}
                  onChange={(e) => updateField("default_reply_language", e.target.value)}
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Jeu préféré</label>
                <select
                  className="select"
                  value={form.preferred_launch_game}
                  onChange={(e) => updateField("preferred_launch_game", e.target.value)}
                >
                  {GAMES.map((game) => (
                    <option key={game.value} value={game.value}>
                      {game.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Toggle
                label="Mode bidirectionnel"
                checked={form.bidirectional_mode}
                onChange={(v) => updateField("bidirectional_mode", v)}
              />
              <Toggle
                label="Détection auto langue"
                checked={form.auto_detect_language}
                onChange={(v) => updateField("auto_detect_language", v)}
              />
            </div>
            {form.translator === "deepl" ? (
              <div>
                <label className="label">
                  Clé DeepL {form.deepl_api_key_set ? "(configurée ✓)" : "(non définie)"}
                </label>
                <input
                  className="input"
                  type="password"
                  placeholder="Nouvelle clé DeepL (optionnel)"
                  value={deeplKey}
                  onChange={(e) => setDeeplKey(e.target.value)}
                />
              </div>
            ) : null}
          </section>

          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">
              ◈ Capture & OCR
            </h2>
            <div>
              <label className="label">Langues OCR (séparées par virgule)</label>
              <input
                className="input"
                value={form.ocr_languages}
                onChange={(e) => updateField("ocr_languages", e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">FPS capture ({form.capture_fps})</label>
                <input
                  className="input"
                  type="range"
                  min={1}
                  max={3}
                  value={form.capture_fps}
                  onChange={(e) => updateField("capture_fps", Number(e.target.value))}
                />
              </div>
              <Toggle
                label="Surveillance chat OCR"
                checked={form.chat_monitor_enabled}
                onChange={(v) => updateField("chat_monitor_enabled", v)}
              />
            </div>
          </section>

          <section className="card space-y-4">
            <h2 className="font-cinzel text-sm uppercase tracking-widest text-diablo-gold">
              ◈ Voix
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              <Toggle
                label="Entrée micro"
                checked={form.voice_input_enabled}
                onChange={(v) => updateField("voice_input_enabled", v)}
              />
              <Toggle
                label="Lire traductions"
                checked={form.speak_translation}
                onChange={(v) => updateField("speak_translation", v)}
              />
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}

function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-3 rounded-sm border border-diablo-border/60 bg-black/20 px-3 py-2.5">
      <span className="text-sm text-diablo-muted">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 rounded-full border transition ${
          checked
            ? "border-diablo-gold bg-diablo-accentBright/80"
            : "border-diablo-border bg-diablo-ash"
        }`}
      >
        <span
          className={`absolute top-0.5 h-4 w-4 rounded-full bg-diablo-gold transition ${
            checked ? "left-5" : "left-0.5"
          }`}
        />
      </button>
    </label>
  );
}
