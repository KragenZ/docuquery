import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocMind AI | Chat with your PDFs",
  description: "RAG-powered document Q&A with citations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#0f111a] text-slate-200">
        {children}
      </body>
    </html>
  );
}
