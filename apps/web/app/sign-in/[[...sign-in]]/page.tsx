"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

type LoginResult = {
  success: boolean;
  challengeId?: string;
  devOtpCode?: string;
  error?: string;
};

type VerifyResult = {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    name: string;
    email: string | null;
    phone: string | null;
  };
  error?: string;
};

export default function SignInPage() {
  const router = useRouter();
  const onboardingTarget = "/modules/account?tab=subscription&onboarding=1";
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [channel, setChannel] = useState<"sms" | "email">("sms");
  const [remember, setRemember] = useState(true);
  const [challengeId, setChallengeId] = useState<string | null>(null);
  const [otpCode, setOtpCode] = useState("");
  const [devOtpCode, setDevOtpCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const persistSession = (token: string, user: VerifyResult["user"]) => {
    localStorage.setItem("kloud_auth_token", token);
    if (user?.id) localStorage.setItem("kloud_user_id", user.id);
    if (user?.name) localStorage.setItem("kloud_user_name", user.name);
    if (user?.email) localStorage.setItem("kloud_user_email", user.email);
    if (user?.phone) localStorage.setItem("kloud_user_phone", user.phone);
  };

  // Safe parse: error responses can have an empty body, which would otherwise
  // throw "Unexpected end of JSON input" on res.json().
  const safeJson = async <T,>(res: Response): Promise<T> => {
    const text = await res.text();
    if (!text) {
      throw new Error(
        res.ok ? "Empty response from server" : `Server error (${res.status})`,
      );
    }
    try {
      return JSON.parse(text) as T;
    } catch {
      throw new Error(`Unexpected server response (${res.status})`);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/internal-auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Kloud-Node-Id": typeof window !== "undefined" ? window.location.hostname : "web-client",
        },
        body: JSON.stringify({ identifier, password, channel, remember }),
      });
      const data = await safeJson<LoginResult>(res);
      if (!res.ok || !data.success || !data.challengeId) {
        throw new Error(data.error || "Login failed");
      }
      setChallengeId(data.challengeId);
      setDevOtpCode(data.devOtpCode || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!challengeId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/internal-auth/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Kloud-Node-Id": typeof window !== "undefined" ? window.location.hostname : "web-client",
        },
        body: JSON.stringify({ challengeId, code: otpCode }),
      });
      const data = await safeJson<VerifyResult>(res);
      if (!res.ok || !data.success || !data.token) {
        throw new Error(data.error || "OTP verification failed");
      }
      persistSession(data.token, data.user);
      router.push(onboardingTarget);
    } catch (err) {
      setError(err instanceof Error ? err.message : "OTP verification failed");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-cyan-950 to-slate-900 p-4 text-white">
      <div className="mx-auto mt-14 max-w-md rounded-2xl border border-cyan-700/50 bg-slate-900/80 p-6 shadow-2xl">
        <h1 className="text-3xl font-bold">Sign In</h1>
        <p className="mt-1 text-sm text-cyan-100/80">Internal auth only: Email OTP / SMS OTP</p>

        {!challengeId ? (
          <div className="mt-6 space-y-3">
            <input
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="Email or phone"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value as "sms" | "email")}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            >
              <option value="sms">SMS OTP</option>
              <option value="email">Email OTP</option>
            </select>
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="h-4 w-4 rounded border-slate-600 bg-slate-800"
              />
              Remember this device (persistent session)
            </label>
            <button
              disabled={loading}
              onClick={handleLogin}
              className="w-full rounded-lg bg-cyan-600 px-4 py-2 font-semibold hover:bg-cyan-500 disabled:opacity-60"
            >
              {loading ? "Signing in..." : "Continue"}
            </button>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            <input
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              placeholder="Enter OTP code"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <button
              disabled={loading}
              onClick={handleVerify}
              className="w-full rounded-lg bg-cyan-600 px-4 py-2 font-semibold hover:bg-cyan-500 disabled:opacity-60"
            >
              {loading ? "Verifying..." : "Verify OTP"}
            </button>
            {devOtpCode && (
              <p className="rounded-md border border-amber-500/50 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
                Dev OTP: {devOtpCode}
              </p>
            )}
          </div>
        )}

        {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}

        <p className="mt-6 text-sm text-slate-300">
          No account? <Link href="/sign-up" className="text-cyan-300 hover:text-cyan-200">Create one</Link>
        </p>
      </div>
    </div>
  );
}

