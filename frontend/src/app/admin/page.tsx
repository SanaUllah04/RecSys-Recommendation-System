"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useDashboardStats, useAdminModels, useTrainModel } from "@/hooks/useRecommendations";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ALGORITHM_LABELS, Algorithm } from "@/types";
import { motion } from "framer-motion";
import {
  Users, Package, Star, BarChart3, Settings, Play, Brain,
  TrendingUp, Activity, Database, Clock, Cpu
} from "lucide-react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from "chart.js";
import { Pie, Bar } from "react-chartjs-2";
import toast from "react-hot-toast";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: any; color: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  const { user } = useAuth();
  const { data: stats, isLoading: loadingStats } = useDashboardStats();
  const { data: models, isLoading: loadingModels } = useAdminModels();
  const trainMutation = useTrainModel();
  const [trainingAlgo, setTrainingAlgo] = useState("hybrid");

  if (!user?.is_admin) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Card className="p-8 text-center">
          <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-900 dark:text-white">Admin Access Required</p>
          <p className="text-gray-500 mt-2">You need admin privileges to access this page</p>
        </Card>
      </div>
    );
  }

  const handleTrain = async () => {
    try {
      toast.loading(`Training ${trainingAlgo} model...`, { id: "train" });
      const result = await trainMutation.mutateAsync({ algorithm: trainingAlgo });
      toast.success(`Model trained in ${result.training_duration}s`, { id: "train" });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Training failed", { id: "train" });
    }
  };

  const algoOptions: Algorithm[] = ["hybrid", "popularity", "content_based", "collaborative", "matrix_factorization"];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Settings className="h-8 w-8 text-primary-600" />
          Admin Dashboard
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Manage models, users, and system configuration</p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Users" value={stats?.total_users || "—"} icon={Users} color="bg-gradient-to-br from-blue-500 to-blue-700" />
        <StatCard label="Total Items" value={stats?.total_items || "—"} icon={Package} color="bg-gradient-to-br from-green-500 to-green-700" />
        <StatCard label="Interactions" value={stats?.total_interactions || "—"} icon={Activity} color="bg-gradient-to-br from-purple-500 to-purple-700" />
        <StatCard label="Avg Rating" value={stats?.avg_rating ? `${stats.avg_rating}★` : "—"} icon={Star} color="bg-gradient-to-br from-amber-500 to-orange-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Cpu className="h-5 w-5" /> Train Model</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              {algoOptions.map((algo) => (
                <button
                  key={algo}
                  onClick={() => setTrainingAlgo(algo)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    trainingAlgo === algo ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"
                  }`}
                >
                  {ALGORITHM_LABELS[algo]}
                </button>
              ))}
            </div>
            <Button onClick={handleTrain} disabled={trainMutation.isPending} className="w-full">
              <Play className="h-4 w-4 mr-2" />
              {trainMutation.isPending ? "Training..." : `Train ${ALGORITHM_LABELS[trainingAlgo as Algorithm]} Model`}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Database className="h-5 w-5" /> Models</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingModels ? (
              <div className="space-y-2">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="h-12 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />)}</div>
            ) : models?.length ? (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {models.slice(0, 10).map((m) => (
                  <div key={m.id} className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{m.version}</p>
                      <p className="text-xs text-gray-500">{m.training_data_size} items | {m.training_duration_seconds}s</p>
                    </div>
                    <Badge variant={m.is_active ? "success" : "secondary"}>{m.is_active ? "Active" : "Inactive"}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm text-center py-4">No models trained yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5" /> Categories Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.top_categories?.length ? (
              <div className="h-64">
                <Pie
                  data={{
                    labels: stats.top_categories.map((c) => c.name),
                    datasets: [{
                      data: stats.top_categories.map((c) => c.count),
                      backgroundColor: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4"],
                    }],
                  }}
                  options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom", labels: { color: "#94a3b8" } } } }}
                />
              </div>
            ) : (
              <p className="text-gray-500 text-sm text-center py-8">No category data</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><TrendingUp className="h-5 w-5" /> Interaction Types</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.interaction_types?.length ? (
              <div className="h-64">
                <Bar
                  data={{
                    labels: stats.interaction_types.map((i) => i.type),
                    datasets: [{
                      label: "Count",
                      data: stats.interaction_types.map((i) => i.count),
                      backgroundColor: "#3b82f6",
                      borderRadius: 6,
                    }],
                  }}
                  options={{
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
                      y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
                    },
                  }}
                />
              </div>
            ) : (
              <p className="text-gray-500 text-sm text-center py-8">No interaction data</p>
            )}
          </CardContent>
        </Card>
      </div>

      {stats?.top_categories && (
        <Card>
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.top_categories.map((cat) => {
                const maxCount = Math.max(...stats.top_categories.map((c) => c.count));
                return (
                  <div key={cat.name} className="flex items-center gap-4">
                    <span className="w-24 text-sm font-medium text-gray-700 dark:text-gray-300">{cat.name}</span>
                    <div className="flex-1">
                      <Progress value={cat.count} max={maxCount} />
                    </div>
                    <span className="text-sm text-gray-500 w-12 text-right">{cat.count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
