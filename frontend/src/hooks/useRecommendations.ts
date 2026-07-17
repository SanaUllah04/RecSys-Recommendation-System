"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { RecommendationResponse, Algorithm, ComparisonResponse, DashboardStats, Item, ModelVersion, PaginatedResponse } from "@/types";

export function useRecommendations(algorithm: Algorithm = "hybrid", limit: number = 20) {
  return useQuery<RecommendationResponse>({
    queryKey: ["recommendations", algorithm, limit],
    queryFn: async () => {
      const res = await api.get("/recommendations/me", { params: { algorithm, limit } });
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

export function useCompareAlgorithms(limit: number = 10) {
  return useQuery<ComparisonResponse>({
    queryKey: ["compare-algorithms", limit],
    queryFn: async () => {
      const res = await api.get("/recommendations/all", { params: { limit } });
      return res.data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useSimilarItems(itemId: number) {
  return useQuery<{ item_id: number; title: string; image_url: string; score: number; similarity_pct: number }[]>({
    queryKey: ["similar-items", itemId],
    queryFn: async () => {
      const res = await api.get(`/recommendations/similar/${itemId}`);
      return res.data;
    },
    enabled: !!itemId,
  });
}

export function useSearch(query: string, category?: string, page: number = 1) {
  return useQuery<PaginatedResponse<Item>>({
    queryKey: ["search", query, category, page],
    queryFn: async () => {
      const res = await api.get("/search/", { params: { q: query, category, page, page_size: 20 } });
      return res.data;
    },
    enabled: true,
  });
}

export function useTrending() {
  return useQuery<Item[]>({
    queryKey: ["trending"],
    queryFn: async () => {
      const res = await api.get("/items/trending");
      return res.data;
    },
  });
}

export function useTopRated() {
  return useQuery<Item[]>({
    queryKey: ["top-rated"],
    queryFn: async () => {
      const res = await api.get("/items/top-rated");
      return res.data;
    },
  });
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["admin-stats"],
    queryFn: async () => {
      const res = await api.get("/admin/stats");
      return res.data;
    },
  });
}

export function useAdminModels() {
  return useQuery<ModelVersion[]>({
    queryKey: ["admin-models"],
    queryFn: async () => {
      const res = await api.get("/admin/models");
      return res.data;
    },
  });
}

export function useTrainModel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (params: { algorithm: string; parameters?: Record<string, unknown> }) => {
      const res = await api.post("/admin/train", params);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-models"] });
      qc.invalidateQueries({ queryKey: ["admin-stats"] });
    },
  });
}

export function useRecordInteraction() {
  return useMutation({
    mutationFn: async (data: { item_id: number; interaction_type: string; duration_seconds?: number }) => {
      const res = await api.post("/recommendations/interaction", data);
      return res.data;
    },
  });
}

export function useRecordRating() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: { item_id: number; rating: number }) => {
      const res = await api.post("/recommendations/rate", data);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}

export function useCategories() {
  return useQuery<{ name: string; count: number }[]>({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await api.get("/search/categories");
      return res.data;
    },
  });
}
