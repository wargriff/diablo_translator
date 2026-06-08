import type { Metadata, Viewport } from "next";
import { Cinzel, Crimson_Pro } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

const cinzel = Cinzel({
  subsets: ["latin"],
  variable: "--font-cinzel",
  weight: ["400", "600", "700"],
});

const body = Crimson_Pro({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Diablo Translator — Sanctuaire",
  description: "Traduction multilingue en temps réel — thème Diablo IV",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#8b0000",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`dark ${cinzel.variable} ${body.variable}`}>
      <body className="min-h-screen bg-d4-radial">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="relative flex-1 overflow-auto p-6 md:p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
