"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { BarChart3 } from "lucide-react";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({ email: "", username: "", password: "", fullName: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form.email, form.username, form.password, form.fullName);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-600">
            <BarChart3 className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl">Create Account</CardTitle>
          <p className="text-sm text-gray-500 dark:text-gray-400">Join the recommendation platform</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Full Name" placeholder="John Doe" value={form.fullName} onChange={(e) => setForm({ ...form, fullName: e.target.value })} />
            <Input label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            <Input label="Username" placeholder="johndoe" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
            <Input label="Password" type="password" placeholder="Min 6 characters" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
          <div className="mt-3 text-center text-sm">
            <Link href="/auth/login" className="text-primary-600 hover:underline">Already have an account? Sign in</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
