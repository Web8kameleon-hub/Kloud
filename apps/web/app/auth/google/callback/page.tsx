"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("Completing Google sign-in...");

  useEffect(() => {
    const run = async () => {
      try {
        const code = searchParams.get("code") || "";
        const state = searchParams.get("state") || "";

        if (!code || !state) {
          throw new Error("Missing Google callback parameters");
        }

        const res = await fetch(
          `/api/internal-auth/google/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`,
          { method: "GET" }
        );

        const data = (await res.json()) as {
          success?: boolean;
          token?: string;
          user?: {
            id: string;
            name: string;
            email: string | null;
            phone: string | null;
          };
          returnUrl?: string | null;
          error?: string;
        };

        if (!res.ok || !data.success || !data.token) {
          throw new Error(data.error || "Google sign-in failed");
        }

        localStorage.setItem("kloud_auth_token", data.token);
        if (data.user?.id) localStorage.setItem("kloud_user_id", data.user.id);
        if (data.user?.name) localStorage.setItem("kloud_user_name", data.user.name);
        if (data.user?.email) localStorage.setItem("kloud_user_email", data.user.email);
        if (data.user?.phone) localStorage.setItem("kloud_user_phone", data.user.phone);

        router.replace(data.returnUrl || "/modules/account");
      } catch (err) {
        setMessage(err instanceof Error ? err.message : "Google sign-in failed");
      }
    };

    void run();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <div className="max-w-md rounded-xl border border-slate-700 bg-slate-900/80 p-6 text-center">
        <h1 className="text-xl font-semibold">Google Callback</h1>
        <p className="mt-3 text-slate-300">{message}</p>
      </div>
    </div>
  );
}
