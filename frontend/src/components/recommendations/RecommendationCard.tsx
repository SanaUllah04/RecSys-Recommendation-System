"use client";

import { RecommendationItem } from "@/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";

interface Props {
  item: RecommendationItem;
  index?: number;
  onClick?: () => void;
}

const algoColors: Record<string, string> = {
  popularity: "from-gray-400 to-gray-600",
  content_based: "from-gray-400 to-gray-600",
  collaborative: "from-gray-400 to-gray-600",
  matrix_factorization: "from-gray-400 to-gray-600",
  hybrid: "from-gray-400 to-gray-600",
};

export function RecommendationCard({ item, index = 0, onClick }: Props) {
  const gradient = algoColors[item.algorithm] || "from-gray-500 to-gray-600";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      whileHover={{ y: -4 }}
      onClick={onClick}
      className="cursor-pointer"
    >
      <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="relative aspect-[3/4] bg-gray-100 dark:bg-gray-800 overflow-hidden">
          {item.image_url ? (
            <img src={item.image_url} alt={item.title} className="h-full w-full object-cover" loading="lazy" />
          ) : (
            <div className={`h-full w-full bg-gradient-to-br ${gradient}`} />
          )}
          <div className="absolute top-2 right-2">
            <Badge className={`bg-gradient-to-r ${gradient} text-white border-0`}>
              {Math.round(item.score * 100)}% match
            </Badge>
          </div>
          <div className="absolute top-2 left-2">
            <Badge variant="secondary" className="bg-white/90 dark:bg-gray-900/90">
              {item.algorithm.replace("_", " ")}
            </Badge>
          </div>
        </div>
        <div className="p-3">
          <h3 className="font-semibold text-sm text-gray-900 dark:text-white line-clamp-1">{item.title}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{item.avg_rating}</span>
            {item.genres && (
              <span className="text-xs text-gray-500 dark:text-gray-400 line-clamp-1">{item.genres.split(",")[0]}</span>
            )}
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{item.reason}</p>
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
              <div className="h-full rounded-full bg-white" style={{ width: `${item.similarity_pct}%` }} />
            </div>
            <span className="text-[10px] text-gray-400">{item.similarity_pct}%</span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
