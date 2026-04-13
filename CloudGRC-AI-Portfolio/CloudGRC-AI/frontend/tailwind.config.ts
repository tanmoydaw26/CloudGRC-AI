import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy:   { DEFAULT: "#1a2940", light: "#243450", dark: "#111d2e" },
        teal:   { DEFAULT: "#2a6b7c", light: "#3a8a9e", dark: "#1e4f5c" },
        cyber:  { DEFAULT: "#00ffe7", dim: "#00ccbb" },
        danger: "#ff003c",
        warn:   "#ff6600",
        caution:"#ffaa00",
        safe:   "#00cc66",
      },
      fontFamily: {
        mono: ["'Courier New'", "monospace"],
        sans: ["Inter", "sans-serif"],
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(rgba(0,255,231,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,231,0.03) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
export default config;
