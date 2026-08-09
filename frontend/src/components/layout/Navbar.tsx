"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, Menu, X } from "lucide-react";
import { useState } from "react";

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/search", label: "Search" },
  { href: "/admin", label: "Admin", adminOnly: true },
];

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!isAuthenticated) return null;

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-black/90 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-2">
              <img src="/logo.svg" alt="RecSys" className="h-8 w-8" />
              <span className="text-xl font-bold text-white hidden sm:block">RecSys</span>
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {navLinks
                .filter((l) => !l.adminOnly || user?.is_admin)
                .map((link) => {
                  const active = pathname === link.href || pathname?.startsWith(link.href + "/");
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={cn(
                        "flex items-center border-b-2 px-3 py-2 text-sm font-medium transition-colors",
                        active
                          ? "border-white text-white"
                          : "border-transparent text-gray-400 hover:text-white"
                      )}
                    >
                      {link.label}
                    </Link>
                  );
                })}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center text-sm text-gray-600 dark:text-gray-400">
              <span>{user?.username}</span>
            </div>
            <button onClick={logout} className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-800" title="Logout">
              <LogOut className="h-5 w-5" />
            </button>
            <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden rounded-lg p-2 text-gray-500 hover:bg-gray-100">
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-200 dark:border-gray-700 pb-3 px-4">
          {navLinks.filter((l) => !l.adminOnly || user?.is_admin).map((link) => {
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="flex items-center rounded-lg px-3 py-3 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
}
