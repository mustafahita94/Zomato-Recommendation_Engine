import type { Metadata } from "next";
import { Outfit, Sora, Space_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  weight: ["400", "500", "600"],
});

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  weight: ["600"],
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  variable: "--font-space-mono",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "Discover — Places Worth the Trip",
  description:
    "AI restaurant recommender for Bangalore. Set preferences and get ranked picks with clear explanations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${outfit.variable} ${sora.variable} ${spaceMono.variable} font-body antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
