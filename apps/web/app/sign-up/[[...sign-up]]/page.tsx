"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

type RegisterResult = {
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

export default function SignUpPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [channel, setChannel] = useState<"sms" | "email">("sms");
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

  const handleRegister = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/internal-auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email: email || undefined,
          phone: phone || undefined,
          password,
          channel,
        }),
      });
      const data = (await res.json()) as RegisterResult;
      if (!res.ok || !data.success || !data.challengeId) {
        throw new Error(data.error || "Registration failed");
      }
      setChallengeId(data.challengeId);
      setDevOtpCode(data.devOtpCode || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ challengeId, code: otpCode }),
      });
      const data = (await res.json()) as VerifyResult;
      if (!res.ok || !data.success || !data.token) {
        throw new Error(data.error || "OTP verification failed");
      }
      persistSession(data.token, data.user);
      router.push("/modules/account");
    } catch (err) {
      setError(err instanceof Error ? err.message : "OTP verification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-cyan-950 to-slate-900 p-4 text-white">
      <div className="mx-auto mt-14 max-w-md rounded-2xl border border-cyan-700/50 bg-slate-900/80 p-6 shadow-2xl">
        <h1 className="text-3xl font-bold">Create Account</h1>
        <p className="mt-1 text-sm text-cyan-100/80">Internal auth with OTP confirmation</p>

        {!challengeId ? (
          <div className="mt-6 space-y-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Full name"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Phone (optional if email set)"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 8 chars)"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            />
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value as "sms" | "email")}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
            >
              <option value="sms">Verify with SMS OTP</option>
              <option value="email">Verify with Email OTP</option>
            </select>
            <button
              disabled={loading}
              onClick={handleRegister}
              className="w-full rounded-lg bg-cyan-600 px-4 py-2 font-semibold hover:bg-cyan-500 disabled:opacity-60"
            >
              {loading ? "Creating account..." : "Register"}
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
              {loading ? "Verifying..." : "Verify and Continue"}
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
          Already have an account? <Link href="/sign-in" className="text-cyan-300 hover:text-cyan-200">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

