"use client";

import { useState } from "react";
import { useRecommendations } from "@/hooks/useRecommendations";
import { AlgorithmSelector } from "@/components/recommendations/AlgorithmSelector";
import { ComparisonView } from "@/components/recommendations/ComparisonView";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { RecommendationSkeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Algorithm } from "@/types";
import { motion } from "framer-motion";
import { Sparkles, RefreshCw, Clock, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function RecommendationsPage() {
  const [algorithm, setAlgorithm] = useState<Algorithm | "compare">("hybrid");
  const [limit, setLimit] = useState(20);
  const { data, isLoading, refetch, isFetching } = useRecommendations(algorithm as Algorithm, limit);

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary-600" />
            Recommendations
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Explore recommendations from different algorithms</p>
        </div>
        <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </motion.div>

      <AlgorithmSelector selected={algorithm} onChange={setAlgorithm} />

      <div className="flex items-center gap-4">
        <label className="text-sm text-gray-500 dark:text-gray-400">Show:</label>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          {[5, 10, 15, 20, 30, 50].map((n) => (
            <option key={n} value={n}>{n} items</option>
          ))}
        </select>
      </div>

      {algorithm === "compare" ? (
        <ComparisonView />
      ) : isLoading ? (
        <RecommendationSkeleton />
      ) : data?.recommendations?.length ? (
        <>
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> Generated: {new Date(data.generated_at).toLocaleTimeString()}</span>
            {data.response_time_ms && <span className="flex items-center gap-1"><Zap className="h-3 w-3" /> {data.response_time_ms}ms</span>}
            {data.cached && <span className="text-green-600">Cached</span>}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {data.recommendations.map((item, i) => (
              <RecommendationCard key={item.item_id} item={item} index={i} />
            ))}
          </div>
        </>
      ) : (
        <Card className="p-12 text-center">
          <Sparkles className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400 text-lg">No recommendations available</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Train a model from the admin panel or interact with items first</p>
        </Card>
      )}
    </div>
  );
}
