"use client";

import { DeeplTranslator } from "@/components/deepl-translator";

export default function ReplyPage() {
  return (
    <div className="flex min-h-[calc(100vh-6rem)] flex-col items-center justify-center py-4">
      <div className="mb-8 text-center">
        <p className="d4-subtitle mb-2">Diablo Translator</p>
        <h1 className="font-cinzel text-3xl font-bold uppercase tracking-[0.12em] text-diablo-gold">
          Traduction
        </h1>
      </div>
      <DeeplTranslator />
    </div>
  );
}
