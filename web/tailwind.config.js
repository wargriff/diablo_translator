/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        cinzel: ["var(--font-cinzel)", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      colors: {
        diablo: {
          bg: "#0a0806",
          panel: "#14110e",
          panelLight: "#1c1712",
          border: "#3d2e1f",
          borderGold: "#8b6914",
          accent: "#8b0000",
          accentBright: "#c41e3a",
          gold: "#c9a227",
          goldDim: "#8a6d1d",
          ember: "#ff4d2e",
          muted: "#8a8278",
          ash: "#2a2520",
        },
      },
      boxShadow: {
        d4: "0 0 24px rgba(196, 30, 58, 0.15), inset 0 1px 0 rgba(201, 162, 39, 0.12)",
        "d4-gold": "0 0 20px rgba(201, 162, 39, 0.25)",
      },
      backgroundImage: {
        "d4-radial":
          "radial-gradient(ellipse at 50% 0%, rgba(139, 0, 0, 0.35) 0%, transparent 55%), radial-gradient(ellipse at 80% 100%, rgba(201, 162, 39, 0.08) 0%, transparent 40%)",
        "d4-panel":
          "linear-gradient(180deg, rgba(201,162,39,0.06) 0%, transparent 40%), linear-gradient(135deg, #1c1712 0%, #0f0c0a 100%)",
      },
      animation: {
        ember: "ember 3s ease-in-out infinite",
        "pulse-gold": "pulse-gold 2s ease-in-out infinite",
      },
      keyframes: {
        ember: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        "pulse-gold": {
          "0%, 100%": { boxShadow: "0 0 12px rgba(201,162,39,0.2)" },
          "50%": { boxShadow: "0 0 28px rgba(201,162,39,0.45)" },
        },
      },
    },
  },
  plugins: [],
};
