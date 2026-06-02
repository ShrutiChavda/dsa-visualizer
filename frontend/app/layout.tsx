import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DSA Visualizer — Step-by-step code execution",
  description:
    "Visualize Python code execution at a beginner level with step-by-step breakdown of every expression.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#080c14] text-slate-100 antialiased overflow-hidden h-screen">
        {children}
      </body>
    </html>
  );
}
