import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import QueryProvider from "@/components/ui/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CloudGRC-AI — Cloud Compliance & Risk Scanner",
  description: "Automated multi-cloud security scanning mapped to ISO 27001, NIST CSF, and CIS Benchmarks",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#010a0e] text-[#c9e8e0] min-h-screen`}>
        <QueryProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              style: { background: "#0a1a20", color: "#c9e8e0", border: "1px solid #2a6b7c" },
              success: { iconTheme: { primary: "#00cc66", secondary: "#010a0e" } },
              error:   { iconTheme: { primary: "#ff003c", secondary: "#010a0e" } },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  );
}
