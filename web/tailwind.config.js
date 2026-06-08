/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        diablo: {
          bg: "#0f0f12",
          panel: "#17171c",
          border: "#2a2a33",
          accent: "#c41e3a",
          gold: "#d4af37",
          muted: "#9ca3af",
        },
      },
    },
  },
  plugins: [],
};
