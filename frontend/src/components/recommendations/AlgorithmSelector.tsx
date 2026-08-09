"use client";

import { Algorithm, ALGORITHM_LABELS } from "@/types";
import { cn } from "@/lib/utils";

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

        return (
          <button
            key={algo}
            onClick={() => onChange(algo)}
            className={cn(
              "rounded-lg border-b-2 px-4 py-2 text-sm font-medium transition-colors",
              isActive
                ? "border-white text-white"
                : "border-transparent text-gray-400 hover:text-white"
            )}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
