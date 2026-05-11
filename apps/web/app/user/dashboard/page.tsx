/**
 * Kloud Cloud - User Dashboard
 * 
 * Protected dashboard with subscription info, usage stats, and quick actions
 * 
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

// Conditional Clerk imports
const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let useUser: any = () => ({ user: null, isLoaded: true });
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let UserButton: any = () => null;

if (isClerkConfigured) {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const clerk = require("@clerk/nextjs");
  useUser = clerk.useUser;
  UserButton = clerk.UserButton;
}

interface UserStats {
  apiCalls: number;
  apiLimit: number;
  storage: string;
  projects: number;
  plan: string;
  billingCycle: string;
}

interface SovereignEvent {
  timestamp_ms: number;
  endpoint: string;
  action: string;
  stigma_level: number;
  ndb_score: number;
  outcome: string;
}

interface SovereignData {
  source: string;
  status: {
    metrics?: {
      active_peers?: number;
      avg_latency_ms?: number;
      bandwidth_kbps?: number;
      load?: number;
    };
    ndb_score?: number;
    ndb_delta?: number;
    ndb_threshold?: number;
    state?: string;
    tide?: string;
  };
  security: {
    node_id?: number;
    event_count?: number;
    high_risk?: boolean;
  };
  events: SovereignEvent[];
  localState: Array<{
    key: string;
    raw: string;
    decoded: Record<string, unknown> | null;
  }>;
}

export default function UserDashboardPage() {
  const { user, isLoaded } = useUser();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [recentChats, setRecentChats] = useState<Array<{id: string, title: string, updatedAt: string}>>([]);
  const [sovereignData, setSovereignData] = useState<SovereignData | null>(null);
  const [sovereignError, setSovereignError] = useState<string>("");

  useEffect(() => {
    if (isLoaded && user) {
      // Fetch user stats
      fetchUserStats();
      fetchRecentChats();
      fetchSovereignData();
    } else if (isLoaded && !user && isClerkConfigured) {
      // Redirect to sign in if not authenticated and Clerk is configured
      window.location.href = "/sign-in";
    }
  }, [isLoaded, user]);

  const fetchUserStats = async () => {
    // In production, fetch from API
    setStats({
      apiCalls: 127,
      apiLimit: 500,
      storage: "2.4 GB",
      projects: 3,
      plan: "Professional",
      billingCycle: "Monthly",
    });
  };

  const fetchRecentChats = async () => {
    try {
      const response = await fetch("/api/chat");
      if (response.ok) {
        const data = await response.json();
        setRecentChats(data.sessions || []);
      }
    } catch {
      // Use empty array on error
    }
  };

  const fetchSovereignData = async () => {
    try {
      const res = await fetch("/api/sovereign/user-dashboard", { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`failed_${res.status}`);
      }
      const payload = await res.json();
      setSovereignData(sanitizeSovereignData(payload));
      setSovereignError("");
    } catch {
      setSovereignError("Sovereign telemetry is temporarily unavailable.");
    }
  };

  const sanitizeSovereignData = (payload: SovereignData): SovereignData => ({
    ...payload,
    localState: (payload.localState || []).map((entry) => ({
      key: entry.key,
      raw: "[hidden]",
      decoded: null,
    })),
  });

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">C</span>
                </div>
                <span className="text-white font-semibold hidden sm:block">Kloud Cloud</span>
              </Link>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400 text-sm">Dashboard</span>
            </div>
            
            <div className="flex items-center gap-4">
              <Link href="/modules/open-webui" className="text-purple-400 hover:text-purple-300 text-sm">
                🤖 AI Chat
              </Link>
              <Link href="/pricing" className="text-slate-400 hover:text-white text-sm">
                Upgrade
              </Link>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome back! 👋</h1>
          <p className="text-slate-400">
            Here&apos;s an overview of your Kloud Cloud activity.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="API Calls Today"
            value={`${stats?.apiCalls || 0}/${stats?.apiLimit || 500}`}
            icon="📊"
            color="purple"
            progress={(stats?.apiCalls || 0) / (stats?.apiLimit || 500) * 100}
          />
          <StatCard
            title="Storage Used"
            value={stats?.storage || "0 GB"}
            icon="💾"
            color="blue"
          />
          <StatCard
            title="Active Projects"
            value={String(stats?.projects || 0)}
            icon="📁"
            color="green"
          />
          <StatCard
            title="Current Plan"
            value={stats?.plan || "Free"}
            icon="⭐"
            color="yellow"
            subtitle={stats?.billingCycle}
          />
        </div>

        {/* Sovereign Fabric */}
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Sovereign Fabric Telemetry</h2>
            <button
              onClick={fetchSovereignData}
              className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm transition-colors"
            >
              Refresh
            </button>
          </div>

          {sovereignError ? (
            <p className="text-amber-300 text-sm">{sovereignError}</p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-5">
                <StatCard
                  title="TIDE"
                  value={sovereignData?.status?.tide || "Low"}
                  icon="🌊"
                  color="blue"
                  subtitle={sovereignData?.status?.state || "active"}
                />
                <StatCard
                  title="NDB Score"
                  value={Number(sovereignData?.status?.ndb_score || 0).toFixed(3)}
                  icon="🧠"
                  color="purple"
                  subtitle={`delta ${Number(sovereignData?.status?.ndb_delta || 0).toFixed(3)}`}
                />
                <StatCard
                  title="Active Peers"
                  value={String(sovereignData?.status?.metrics?.active_peers || 0)}
                  icon="🔗"
                  color="green"
                  subtitle={`${sovereignData?.status?.metrics?.avg_latency_ms || 0} ms`}
                />
                <StatCard
                  title="State Keys"
                  value={String(sovereignData?.localState?.length || 0)}
                  icon="🗂️"
                  color="yellow"
                  subtitle={`${sovereignData?.security?.event_count || 0} events`}
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4">
                  <h3 className="text-white font-medium mb-3">Recent Security Events</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-slate-400 border-b border-slate-700">
                          <th className="py-2 pr-3">Endpoint</th>
                          <th className="py-2 pr-3">Action</th>
                          <th className="py-2 pr-3">Stigma</th>
                          <th className="py-2">Outcome</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(sovereignData?.events || []).slice(0, 6).map((e) => (
                          <tr key={`${e.timestamp_ms}-${e.endpoint}`} className="border-b border-slate-800 text-slate-200">
                            <td className="py-2 pr-3">{e.endpoint}</td>
                            <td className="py-2 pr-3">{e.action}</td>
                            <td className="py-2 pr-3">L{e.stigma_level}</td>
                            <td className="py-2">{e.outcome}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4">
                  <h3 className="text-white font-medium mb-3">Local CRDT State</h3>
                  {(sovereignData?.localState || []).length === 0 ? (
                    <p className="text-slate-400 text-sm">No local keys yet</p>
                  ) : (
                    <div className="space-y-3">
                      {(sovereignData?.localState || []).slice(0, 3).map((entry) => (
                        <div key={entry.key} className="rounded-lg bg-slate-800/70 p-3 border border-slate-700">
                          <p className="text-emerald-300 text-sm font-medium">{entry.key}</p>
                          <p className="text-slate-300 text-xs mt-1 break-all">
                            Value hidden for privacy
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <QuickAction href="/modules/open-webui" icon="🤖" label="AI Assistant" />
                <QuickAction href="/modules/aviation-weather" icon="✈️" label="Aviation Weather" />
                <QuickAction href="/modules/behavioral" icon="🧠" label="Behavioral AI" />
                <QuickAction href="/modules/excel-dashboard" icon="📊" label="Excel Dashboard" />
                <QuickAction href="/modules/user-data" icon="📈" label="My Data" />
                <QuickAction href="/developers" icon="🔧" label="API Docs" />
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Recent Conversations</h2>
              {recentChats.length > 0 ? (
                <div className="space-y-3">
                  {recentChats.slice(0, 5).map((chat) => (
                    <Link
                      key={chat.id}
                      href={`/modules/open-webui?session=${chat.id}`}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">💬</span>
                        <div>
                          <p className="text-white text-sm font-medium">{chat.title}</p>
                          <p className="text-slate-400 text-xs">
                            {new Date(chat.updatedAt).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <span className="text-slate-400">→</span>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <span className="text-4xl mb-4 block">💬</span>
                  <p className="text-slate-400 mb-4">No conversations yet</p>
                  <Link
                    href="/modules/open-webui"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm transition-colors"
                  >
                    Start Chatting
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Account Info */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Account</h2>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold">
                    •
                  </div>
                  <div>
                    <p className="text-white font-medium">Authenticated user</p>
                    <p className="text-slate-400 text-sm">Profile details hidden</p>
                  </div>
                </div>
                <div className="pt-4 border-t border-slate-700 space-y-2">
                  <Link href="/account" className="block text-slate-400 hover:text-white text-sm">
                    ⚙️ Account Settings
                  </Link>
                  <Link href="/subscription" className="block text-slate-400 hover:text-white text-sm">
                    💳 Subscription
                  </Link>
                  <Link href="/billing" className="block text-slate-400 hover:text-white text-sm">
                    📄 Billing History
                  </Link>
                </div>
              </div>
            </div>

            {/* Upgrade CTA */}
            {stats?.plan === "Free" && (
              <div className="bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-xl border border-purple-500/30 p-6">
                <h3 className="text-white font-semibold mb-2">🚀 Upgrade to Pro</h3>
                <p className="text-slate-300 text-sm mb-4">
                  Get 10x more API calls, advanced analytics, and priority support.
                </p>
                <Link
                  href="/pricing"
                  className="block w-full text-center py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm transition-colors"
                >
                  View Plans
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ 
  title, 
  value, 
  icon, 
  color, 
  progress, 
  subtitle 
}: { 
  title: string; 
  value: string; 
  icon: string; 
  color: string;
  progress?: number;
  subtitle?: string;
}) {
  const colorClasses: Record<string, string> = {
    purple: "from-purple-500/20 to-purple-600/10 border-purple-500/30",
    blue: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
    green: "from-green-500/20 to-green-600/10 border-green-500/30",
    yellow: "from-yellow-500/20 to-yellow-600/10 border-yellow-500/30",
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} rounded-xl border p-4`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <span className="text-slate-400 text-xs">{subtitle}</span>
      </div>
      <p className="text-slate-400 text-sm">{title}</p>
      <p className="text-white text-2xl font-bold">{value}</p>
      {progress !== undefined && (
        <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
          <div 
            className="h-full bg-purple-500 rounded-full transition-all"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </div>
  );
}

function QuickAction({ href, icon, label }: { href: string; icon: string; label: string }) {
  return (
    <Link
      href={href}
      className="flex flex-col items-center gap-2 p-4 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
    >
      <span className="text-2xl">{icon}</span>
      <span className="text-slate-300 text-sm text-center">{label}</span>
    </Link>
  );
}

