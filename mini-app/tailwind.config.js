/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        wase: {
          primary: "#0D9488",    // Teal — trust, stability
          dark: "#134E4A",       // Deep teal
          light: "#CCFBF1",     // Light mint
          accent: "#F59E0B",     // Amber — money, warmth
          danger: "#EF4444",     // Red — overdue
          success: "#10B981",    // Green — paid
          bg: "var(--tg-theme-bg-color, #FFFFFF)",
          text: "var(--tg-theme-text-color, #1A1A1A)",
          hint: "var(--tg-theme-hint-color, #8E8E93)",
          link: "var(--tg-theme-link-color, #0D9488)",
          button: "var(--tg-theme-button-color, #0D9488)",
          "button-text": "var(--tg-theme-button-text-color, #FFFFFF)",
          "secondary-bg": "var(--tg-theme-secondary-bg-color, #F2F2F7)",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system", "BlinkMacSystemFont", "Segoe UI",
          "Roboto", "Helvetica Neue", "Arial", "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
