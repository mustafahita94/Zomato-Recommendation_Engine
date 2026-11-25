import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#FB7185",
        "on-primary": "#400010",
        "primary-deep": "#C94B60",
        "primary-container": "#400010",
        "on-primary-container": "#FFDADC",
        secondary: "#FDBA74",
        "on-secondary": "#2C1600",
        "secondary-container": "#492900",
        "on-secondary-container": "#FFDCBD",
        success: "#4ADE80",
        "on-success": "#00210C",
        "success-container": "#003919",
        "on-success-container": "#C4FFCD",
        error: "#FF897D",
        "on-error": "#410002",
        "error-container": "#690005",
        "on-error-container": "#FFDAD6",
        "surface-base": "#0B0F14",
        "surface-canvas": "#0D1219",
        surface: "#151B24",
        "surface-elevated": "#1A222E",
        "surface-input": "#0F151E",
        "on-surface": "#E8EEF7",
        "on-surface-muted": "#9AA8BC",
        outline: "#2B3442",
        "outline-strong": "#3A4658",
      },
      borderRadius: {
        sm: "8px",
        DEFAULT: "12px",
        md: "16px",
        lg: "20px",
        full: "9999px",
      },
      spacing: {
        "gutter-xs": "4px",
        "gutter-sm": "8px",
        "gutter-md": "16px",
        "gutter-lg": "24px",
        "gutter-xl": "32px",
        section: "48px",
        "page-margin": "24px",
      },
      fontFamily: {
        display: ["var(--font-sora)", "sans-serif"],
        headline: ["var(--font-sora)", "sans-serif"],
        title: ["var(--font-outfit)", "sans-serif"],
        body: ["var(--font-outfit)", "sans-serif"],
        label: ["var(--font-outfit)", "sans-serif"],
        mono: ["var(--font-space-mono)", "monospace"],
      },
      fontSize: {
        "display-lg": [
          "44px",
          { lineHeight: "50px", letterSpacing: "-0.9px", fontWeight: "600" },
        ],
        "display-lg-mobile": [
          "30px",
          { lineHeight: "36px", letterSpacing: "-0.6px", fontWeight: "600" },
        ],
        "headline-lg": [
          "24px",
          { lineHeight: "32px", letterSpacing: "-0.4px", fontWeight: "600" },
        ],
        "headline-md": [
          "20px",
          { lineHeight: "28px", letterSpacing: "-0.25px", fontWeight: "600" },
        ],
        "title-md": [
          "17px",
          { lineHeight: "24px", letterSpacing: "-0.1px", fontWeight: "600" },
        ],
        "body-lg": [
          "16px",
          { lineHeight: "25px", letterSpacing: "0px", fontWeight: "400" },
        ],
        "body-md": [
          "14px",
          { lineHeight: "22px", letterSpacing: "0px", fontWeight: "400" },
        ],
        "label-lg": [
          "14px",
          { lineHeight: "20px", letterSpacing: "0.1px", fontWeight: "600" },
        ],
        "label-sm": [
          "12px",
          { lineHeight: "16px", letterSpacing: "0.3px", fontWeight: "500" },
        ],
        "mono-sm": [
          "12px",
          { lineHeight: "18px", letterSpacing: "0px", fontWeight: "400" },
        ],
      },
      transitionDuration: {
        "state-change": "120ms",
        "surface-enter": "220ms",
      },
      transitionTimingFunction: {
        "state-change": "ease-out",
        "surface-enter": "cubic-bezier(0.2, 0, 0, 1)",
      },
      maxWidth: {
        content: "1120px",
      },
    },
  },
  plugins: [],
} satisfies Config;
