"use client";

import { useState, useEffect } from "react";
import { useSearch, useCategories } from "@/hooks/useRecommendations";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { RecommendationSkeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Search as SearchIcon, X } from "lucide-react";
import { motion } from "framer-motion";
import { debounce } from "@/lib/utils";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(1);
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const { data, isLoading } = useSearch(debouncedQuery, category, page);
  const { data: categories } = useCategories();

  useEffect(() => {
    const handler = debounce((val: string) => {
      setDebouncedQuery(val);
      setPage(1);
    }, 300);
    handler(query);
  }, [query]);

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Search</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Discover movies, books, music, games, and courses</p>
      </motion.div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title, genre, or keyword..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-white dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          />
          {query && (
            <button onClick={() => setQuery("")} className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setCategory(undefined)}
          className={`border-b-2 px-3 py-1 text-sm font-medium transition-colors ${
            !category ? "border-white text-white" : "border-transparent text-gray-400 hover:text-white"
          }`}
        >
          All
        </button>
        {categories?.map((cat) => (
          <button
            key={cat.name}
            onClick={() => setCategory(cat.name === category ? undefined : cat.name)}
            className={`border-b-2 px-3 py-1 text-sm font-medium transition-colors ${
              category === cat.name ? "border-white text-white" : "border-transparent text-gray-400 hover:text-white"
            }`}
          >
            {cat.name} ({cat.count})
          </button>
        ))}
      </div>

      {isLoading ? (
        <RecommendationSkeleton />
      ) : data?.items?.length ? (
        <>
          <p className="text-sm text-gray-500 dark:text-gray-400">{data.total} results found</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {data.items.map((item, i) => (
              <RecommendationCard
                key={item.id}
                item={{
                  item_id: item.id, title: item.title, image_url: item.image_url,
                  category: item.category, genres: item.genres, avg_rating: item.avg_rating,
                  score: item.popularity_score, confidence: 0.8, reason: `Popular in ${item.category || "its category"}`,
                  similarity_pct: Math.round(item.popularity_score * 100), algorithm: "content_based",
                }}
                index={i}
              />
            ))}
          </div>
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              <Button variant="outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
              <span className="flex items-center px-4 text-sm text-gray-500">Page {page} of {data.total_pages}</span>
              <Button variant="outline" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </>
      ) : (
        <Card className="p-12 text-center">
          <p className="text-gray-500 text-lg">Search for items</p>
          <p className="text-gray-400 text-sm mt-2">Type a query or select a category to explore</p>
        </Card>
      )}
    </div>
  );
}
