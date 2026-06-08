function resolveApiBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }
  // Requêtes relatives → proxy Next.js (next.config.ts) vers le backend local.
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

export type SettingsResponse = {
  language: string;
  translator: string;
  bidirectional_mode: boolean;
};

export const api = {
  health: () => request<{ status: string }>("/api/v1/health"),
  messages: async (limit = 50) => {
    const payload = await request<unknown>(`/api/v1/messages?limit=${limit}`);
    return asArray<MessageItem>(payload);
  },
  translate: (text: string) =>
    request<TranslateResult>("/api/v1/translate", {
      method: "POST",
      body: JSON.stringify({ text, origin: "user" }),
    }),
  compose: (text: string) =>
    request<{ source_text: string; translated_text: string; character_count: number }>(
      "/api/v1/reply/compose",
      { method: "POST", body: JSON.stringify({ text }) },
    ),
  quickReplies: async () => {
    const payload = await request<unknown>("/api/v1/reply/quick");
    return asArray<QuickReply>(payload);
  },
  settings: () => request<SettingsResponse>("/api/v1/settings"),
};

export { API_BASE };
