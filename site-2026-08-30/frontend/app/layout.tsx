import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";

import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "The Intelligence Desk",
    template: "%s | The Intelligence Desk",
  },
  description: "AI news briefs, research articles, and a model comparison desk.",
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-paper text-ink antialiased">
        <Providers>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}
