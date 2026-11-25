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
        /* uupm-inspired: electric blue CTA + warm orange accent */
        primary: "#3B82F6",
        "on-primary": "#F8FAFC",
        "primary-deep": "#2563EB",
        "primary-container": "#1E3A5F",
        "on-primary-container": "#DBEAFE",
        secondary: "#FB923C",
        "on-secondary": "#1A0A00",
        "secondary-container": "#3D2410",
        "on-secondary-container": "#FFEDD5",
        accent: "#60A5FA",
        "on-accent": "#0B1E3A",
        "accent-container": "#12253F",
        "on-accent-container": "#DBEAFE",
        success: "#4ADE80",
        "on-success": "#00210C",
        "success-container": "#003919",
        "on-success-container": "#C4FFCD",
        error: "#F87171",
        "on-error": "#410002",
        "error-container": "#5C1210",
        "on-error-container": "#FFDAD6",
        "surface-base": "#020617",
        "surface-canvas": "#0B1220",
        surface: "#0F172A",
        "surface-elevated": "#1E293B",
        "surface-input": "#0B1220",
        "on-surface": "#F8FAFC",
        "on-surface-muted": "#94A3B8",
        outline: "#1E293B",
        "outline-strong": "#334155",
      },
      borderRadius: {
        sm: "8px",
        DEFAULT: "12px",
        md: "14px",
        lg: "18px",
        full: "9999px",
      },
      spacing: {
        "gutter-xs": "4px",
        "gutter-sm": "8px",
        "gutter-md": "16px",
        "gutter-lg": "24px",
        "gutter-xl": "32px",
        section: "56px",
        "page-margin": "24px",
      },
      fontFamily: {
        display: ["var(--font-syne)", "sans-serif"],
        headline: ["var(--font-syne)", "sans-serif"],
        title: ["var(--font-jakarta)", "sans-serif"],
        body: ["var(--font-jakarta)", "sans-serif"],
        label: ["var(--font-jakarta)", "sans-serif"],
        mono: ["var(--font-space-mono)", "monospace"],
      },
      fontSize: {
        "display-lg": [
          "52px",
          { lineHeight: "56px", letterSpacing: "-1.4px", fontWeight: "700" },
        ],
        "display-lg-mobile": [
          "34px",
          { lineHeight: "38px", letterSpacing: "-0.8px", fontWeight: "700" },
        ],
        "headline-lg": [
          "26px",
          { lineHeight: "32px", letterSpacing: "-0.5px", fontWeight: "700" },
        ],
        "headline-md": [
          "20px",
          { lineHeight: "28px", letterSpacing: "-0.3px", fontWeight: "600" },
        ],
        "title-md": [
          "17px",
          { lineHeight: "24px", letterSpacing: "-0.1px", fontWeight: "600" },
        ],
        "body-lg": [
          "16px",
          { lineHeight: "26px", letterSpacing: "0px", fontWeight: "400" },
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
          { lineHeight: "16px", letterSpacing: "0.2px", fontWeight: "500" },
        ],
        "mono-sm": [
          "12px",
          { lineHeight: "18px", letterSpacing: "0px", fontWeight: "400" },
        ],
      },
      boxShadow: {
        glow: "0 0 40px rgba(59, 130, 246, 0.22)",
        "glow-accent": "0 0 36px rgba(251, 146, 60, 0.16)",
        panel: "0 18px 50px rgba(0, 0, 0, 0.4)",
        nav: "0 8px 32px rgba(0, 0, 0, 0.35)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(14px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "soft-pulse": {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "0.9" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        "fade-up": "fade-up 520ms cubic-bezier(0.2, 0, 0, 1) both",
        "soft-pulse": "soft-pulse 3.2s ease-in-out infinite",
        shimmer: "shimmer 2.4s linear infinite",
      },
      transitionDuration: {
        "state-change": "150ms",
        "surface-enter": "280ms",
      },
      transitionTimingFunction: {
        "state-change": "ease-out",
        "surface-enter": "cubic-bezier(0.2, 0, 0, 1)",
      },
      maxWidth: {
        content: "1120px",
      },
      backdropBlur: {
        glass: "18px",
      },
    },
  },
  plugins: [],
} satisfies Config;
