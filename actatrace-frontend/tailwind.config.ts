import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx}",
    "./components/home/**/*.{ts,tsx}",
    "./components/map/**/*.{ts,tsx}",
    "./components/search/**/*.{ts,tsx}",
    "./app-lib/**/*.{ts,tsx}",
    "./types/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "#d7dde5",
        background: "#f7f9fb",
        foreground: "#17202a",
        muted: "#5f6f82",
        surface: "#ffffff",
        trust: {
          50: "#eef7f4",
          100: "#d6eee7",
          600: "#147362",
          700: "#0f5f52"
        },
        review: {
          50: "#fff8e6",
          600: "#9a6700"
        },
        danger: {
          50: "#fff1f2",
          600: "#be123c"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 12px 40px rgba(23, 32, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
