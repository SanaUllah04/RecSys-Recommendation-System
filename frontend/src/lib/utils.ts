import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "K";
  return num.toString();
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export function debounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
  let timer: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

export function getAlgorithmColor(algo: string): string {
  const colors: Record<string, string> = {
    popularity: "bg-amber-100 text-amber-800",
    content_based: "bg-blue-100 text-blue-800",
    collaborative: "bg-green-100 text-green-800",
    matrix_factorization: "bg-purple-100 text-purple-800",
    hybrid: "bg-red-100 text-red-800",
  };
  return colors[algo] || "bg-gray-100 text-gray-800";
}
