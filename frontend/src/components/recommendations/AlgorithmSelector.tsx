"use client";

import { Algorithm, ALGORITHM_LABELS, ALGORITHM_COLORS } from "@/types";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface Props {
  selected: Algorithm | "compare";
  onChange: (algo: Algorithm | "compare") => void;
}

const algorithms: (Algorithm | "compare")[] = ["hybrid", "popularity", "content_based", "collaborative", "matrix_factorization", "compare"];

export function AlgorithmSelector({ selected, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {algorithms.map((algo) => {
        const isActive = selected === algo;
        const label = algo === "compare" ? "Compare All" : ALGORITHM_LABELS[algo as Algorithm];
        const color = algo === "compare" ? "#6366f1" : ALGORITHM_COLORS[algo as Algorithm];

        return (
          <button
            key={algo}
            onClick={() => onChange(algo)}
            className={cn(
              "relative rounded-full px-4 py-2 text-sm font-medium transition-all duration-200",
              isActive
                ? "text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
            )}
            style={isActive ? { backgroundColor: color } : {}}
          >
            {isActive && (
              <motion.div
                layoutId="algorithm-indicator"
                className="absolute inset-0 rounded-full"
                style={{ backgroundColor: color }}
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
            <span className="relative z-10">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
