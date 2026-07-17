export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Item {
  id: number;
  title: string;
  description: string | null;
  category: string | null;
  genres: string | null;
  tags: string | null;
  image_url: string | null;
  release_date: string | null;
  avg_rating: number;
  rating_count: number;
  popularity_score: number;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface RecommendationItem {
  item_id: number;
  title: string;
  image_url: string | null;
  category: string | null;
  genres: string | null;
  avg_rating: number;
  score: number;
  confidence: number;
  reason: string;
  similarity_pct: number;
  algorithm: string;
}

export interface RecommendationResponse {
  user_id: number;
  algorithm: string;
  recommendations: RecommendationItem[];
  generated_at: string;
  total_count: number;
  cached?: boolean;
  response_time_ms?: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface DashboardStats {
  total_users: number;
  total_items: number;
  total_interactions: number;
  total_ratings: number;
  active_users_24h: number;
  total_recommendations: number;
  avg_rating: number;
  top_categories: { name: string; count: number }[];
  interaction_types: { type: string; count: number }[];
}

export interface ModelVersion {
  id: number;
  version: string;
  algorithm: string;
  metrics: Record<string, unknown> | null;
  parameters: Record<string, unknown> | null;
  training_data_size: number;
  training_duration_seconds: number;
  is_active: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type Algorithm = "popularity" | "content_based" | "collaborative" | "matrix_factorization" | "hybrid";

export const ALGORITHM_LABELS: Record<Algorithm, string> = {
  popularity: "Popularity Based",
  content_based: "Content-Based",
  collaborative: "Collaborative Filtering",
  matrix_factorization: "Matrix Factorization",
  hybrid: "Hybrid",
};

export const ALGORITHM_COLORS: Record<Algorithm, string> = {
  popularity: "#f59e0b",
  content_based: "#3b82f6",
  collaborative: "#10b981",
  matrix_factorization: "#8b5cf6",
  hybrid: "#ef4444",
};
