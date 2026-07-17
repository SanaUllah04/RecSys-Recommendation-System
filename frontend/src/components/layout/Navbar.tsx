"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { BarChart3, Home, Search, Sparkles, Settings, LogOut, Menu, X, User } from "lucide-react";
import { useState } from "react";

const navLinks = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/recommendations", label: "Recommendations", icon: Sparkles },
  { href: "/search", label: "Search", icon: Search },
  { href: "/admin", label: "Admin", icon: Settings, adminOnly: true },
];

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!isAuthenticated) return null;

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md dark:border-gray-700 dark:bg-gray-900/80">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-2">
              <BarChart3 className="h-7 w-7 text-primary-600" />
              <span className="text-xl font-bold text-gray-900 dark:text-white hidden sm:block">RecSys</span>
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {navLinks
                .filter((l) => !l.adminOnly || user?.is_admin)
                .map((link) => {
                  const Icon = link.icon;
                  const active = pathname === link.href || pathname?.startsWith(link.href + "/");
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={cn(
                        "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                        active
                          ? "bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400"
                          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {link.label}
                    </Link>
                  );
                })}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <User className="h-4 w-4" />
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
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
              >
                <Icon className="h-5 w-5" />
                {link.label}
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
}
