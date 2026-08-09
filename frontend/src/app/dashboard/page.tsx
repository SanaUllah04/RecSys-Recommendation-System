"use client";

import { useAuth } from "@/hooks/useAuth";
import { useRecommendations, useTrending, useTopRated } from "@/hooks/useRecommendations";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { RecommendationSkeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import Link from "next/link";

function Section({ title, children, href }: { title: string; children: React.ReactNode; href?: string }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">{title}</h2>
        {href && <Link href={href} className="text-sm text-gray-300 underline underline-offset-4 hover:text-white">View all</Link>}
      </div>
      {children}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: hybridRecs, isLoading: loadingHybrid } = useRecommendations("hybrid", 10);
  const { data: trending, isLoading: loadingTrending } = useTrending();
  const { data: topRated, isLoading: loadingTopRated } = useTopRated();

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.full_name || user?.username}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Here are your personalized recommendations</p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Recommended" value={hybridRecs?.total_count || "—"} />
        <StatCard label="Trending" value={trending?.length || "—"} />
        <StatCard label="Top Rated" value={topRated?.length || "—"} />
        <StatCard label="Algorithms" value="5" />
      </div>

      <Section title="Recommended for You" href="/recommendations">
        {loadingHybrid ? (
          <RecommendationSkeleton />
        ) : hybridRecs?.recommendations?.length ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {hybridRecs.recommendations.slice(0, 10).map((item, i) => (
              <RecommendationCard key={item.item_id} item={item} index={i} />
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400">No recommendations yet. Start interacting with items or train a model from the admin panel.</p>
            <Link href="/recommendations">
              <Button className="mt-4">Browse Recommendations</Button>
            </Link>
          </Card>
        )}
      </Section>

      <Section title="Trending Now">
        {loadingTrending ? (
          <RecommendationSkeleton />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {trending?.slice(0, 10).map((item, i) => (
              <RecommendationCard
                key={item.id}
                item={{
                  item_id: item.id, title: item.title, image_url: item.image_url,
                  category: item.category, genres: item.genres, avg_rating: item.avg_rating,
                  score: item.popularity_score, confidence: 0.8, reason: "Trending now",
                  similarity_pct: Math.round(item.popularity_score * 100), algorithm: "popularity",
                }}
                index={i}
              />
            ))}
          </div>
        )}
      </Section>

      <Section title="Top Rated">
        {loadingTopRated ? (
          <RecommendationSkeleton />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {topRated?.slice(0, 10).map((item, i) => (
              <RecommendationCard
                key={item.id}
                item={{
                  item_id: item.id, title: item.title, image_url: item.image_url,
                  category: item.category, genres: item.genres, avg_rating: item.avg_rating,
                  score: item.avg_rating / 5, confidence: 0.85, reason: "Highest rated",
                  similarity_pct: Math.round((item.avg_rating / 5) * 100), algorithm: "content_based",
                }}
                index={i}
              />
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}
