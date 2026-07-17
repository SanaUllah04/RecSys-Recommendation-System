"use client";

import "./globals.css";
import { Inter } from "next/font/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { AuthContext, useAuthProvider } from "@/hooks/useAuth";
import { Navbar } from "@/components/layout/Navbar";
import { useState } from "react";

const inter = Inter({ subsets: ["latin"] });

function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 2, staleTime: 60000 } },
      })
  );
  const auth = useAuthProvider();

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={auth}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
          <Navbar />
          <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
        </div>
        <Toaster position="top-right" toastOptions={{ duration: 3000, style: { borderRadius: "12px", background: "#1e293b", color: "#f1f5f9" } }} />
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
