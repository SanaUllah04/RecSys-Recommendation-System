"use client";

import { useState, useEffect, useCallback, createContext, useContext } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { User, TokenResponse } from "@/types";
import toast from "react-hot-toast";

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function useAuth(): AuthContextType {
  return useContext(AuthContext);
}

export function useAuthProvider(): AuthContextType {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api.get("/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<TokenResponse>("/auth/login", { email, password });
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    setUser(res.data.user);
    toast.success("Welcome back!");
    router.push("/dashboard");
  }, [router]);

  const register = useCallback(async (email: string, username: string, password: string, fullName?: string) => {
    const res = await api.post<TokenResponse>("/auth/register", {
      email, username, password, full_name: fullName,
    });
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    setUser(res.data.user);
    toast.success("Account created!");
    router.push("/dashboard");
  }, [router]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    router.push("/auth/login");
    toast.success("Logged out");
  }, [router]);

  return { user, loading, login, register, logout, isAuthenticated: !!user };
}
