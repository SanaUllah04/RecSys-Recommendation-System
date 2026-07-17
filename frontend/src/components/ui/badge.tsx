"use client";
import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger";
  className?: string;
}

const variantStyles = {
  default: "bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200",
  secondary: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
  outline: "border border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-300",
  success: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  danger: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", variantStyles[variant], className)}>
      {children}
    </span>
  );
}
