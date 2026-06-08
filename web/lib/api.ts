function resolveApiBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }
  return "";
}

const API_BASE = resolveApiBase();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = API_BASE ? `${API_BASE}${path}` : path;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  const contentType = response.headers.get("content-type") ?? "";
  const body: unknown = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : `API ${response.status}`;
    throw new Error(detail);
  }

  return body as T;
}

function asArray<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload && typeof payload === "object" && "items" in payload) {
    const items = (payload as { items?: unknown }).items;
    return Array.isArray(items) ? (items as T[]) : [];
  }
  return [];
}

export type MessageItem = {
  id: number;
  source_text: string;
  translated_text: string;
  source_language?: string | null;
  target_language?: string | null;
  created_at: string;
};

export type TranslateResult = {
  source_text: string;
  translated_text: string;
  source_language?: string | null;
  target_language?: string | null;
  provider?: string | null;
};

export type QuickReply = {
  key: string;
  label: string;
  translated_text: string;
};

export type Settings = {
  language: string;
  translator: string;
  bidirectional_mode: boolean;
  auto_detect_language: boolean;
  default_reply_language: string;
  capture_fps: number;
  chat_monitor_enabled: boolean;
  voice_input_enabled: boolean;
  speak_translation: boolean;
  hub_sounds_enabled: boolean;
  preferred_launch_game: string;
  ocr_languages: string;
  deepl_api_key_set: boolean;
};

export type SettingsUpdate = Partial<
  Omit<Settings, "deepl_api_key_set"> & { deepl_api_key: string }
>;

export type GameStatus = {
  running: boolean;
  summary: string;
  games: { key: string; title: string; short_title: string }[];
};

export type Stats = {
  message_count: number;
  recent_count: number;
  translator: string;
  language: string;
  translations_today?: number;
  unique_sources?: number;
  api_version?: string;
};

export type LogsPayload = {
  lines: string[];
  path: string;
};

export const LANGUAGES = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
  { value: "de", label: "Deutsch" },
  { value: "es", label: "Español" },
  { value: "it", label: "Italiano" },
  { value: "pt", label: "Português" },
  { value: "ru", label: "Русский" },
  { value: "pl", label: "Polski" },
];

export const GAMES = [
  { value: "d4", label: "Diablo IV" },
  { value: "d3", label: "Diablo III" },
  { value: "immortal", label: "Diablo Immortal" },
];

export const api = {
  health: () => request<{ status: string; version?: string }>("/api/v1/health"),
  messages: async (limit = 50) => {
    const payload = await request<unknown>(`/api/v1/messages?limit=${limit}`);
    return asArray<MessageItem>(payload);
  },
  translate: (text: string, sourceLanguage?: string, targetLanguage?: string) =>
    request<TranslateResult>("/api/v1/translate", {
      method: "POST",
      body: JSON.stringify({
        text,
        origin: "user",
        source_language: sourceLanguage,
        target_language: targetLanguage,
      }),
    }),
  compose: (text: string, sourceLanguage: string, targetLanguage: string) =>
    request<{
      source_text: string;
      translated_text: string;
      character_count: number;
      source_language?: string | null;
      target_language?: string | null;
    }>("/api/v1/reply/compose", {
      method: "POST",
      body: JSON.stringify({
        text,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      }),
    }),
  quickReplies: async () => {
    const payload = await request<unknown>("/api/v1/reply/quick");
    return asArray<QuickReply>(payload);
  },
  settings: () => request<Settings>("/api/v1/settings"),
  updateSettings: (payload: SettingsUpdate) =>
    request<Settings>("/api/v1/settings", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  gameStatus: () => request<GameStatus>("/api/v1/game/status"),
  stats: () => request<Stats>("/api/v1/stats"),
  logs: (lines = 80) => request<LogsPayload>(`/api/v1/logs?lines=${lines}`),
  liveSocketUrl: () => {
    const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
    if (configured) {
      return `${configured.replace(/^http/, "ws").replace(/\/$/, "")}/ws/v1/live`;
    }
    return "ws://127.0.0.1:8000/ws/v1/live";
  },
};

export { API_BASE };
