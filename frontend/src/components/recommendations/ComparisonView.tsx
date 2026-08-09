"use client";

import { useCompareAlgorithms } from "@/hooks/useRecommendations";
import { RecommendationCard } from "./RecommendationCard";
import { RecommendationSkeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ALGORITHM_LABELS, Algorithm, RecommendationItem } from "@/types";
import { motion } from "framer-motion";

export function ComparisonView() {
  const { data, isLoading } = useCompareAlgorithms(5);

  if (isLoading) return <RecommendationSkeleton />;

  if (!data?.results) return <p className="text-center text-gray-500 py-8">No comparison data available. Train the models first.</p>;

  const algos = Object.keys(data.results) as Algorithm[];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Algorithm Comparison</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1">See how different algorithms recommend different items</p>
      </div>
      {algos.map((algo, i) => (
        <motion.div
          key={algo}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className="space-y-3"
        >
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {ALGORITHM_LABELS[algo]}
            </h3>
            <Badge variant="secondary">{data.results[algo]?.length || 0} items</Badge>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {data.results[algo]?.slice(0, 5).map((item: RecommendationItem, j: number) => (
              <RecommendationCard key={item.item_id} item={{ ...item, algorithm: algo }} index={j} />
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
