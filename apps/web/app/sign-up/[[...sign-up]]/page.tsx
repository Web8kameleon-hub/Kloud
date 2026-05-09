/**
 * Kloud Cloud - Sign Up Page
 * 
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { SignUp } from "@clerk/nextjs";

const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function SignUpPage() {
  if (!isClerkConfigured) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Kloud Cloud</h1>
          <p className="text-gray-400 text-lg">Sign up is currently unavailable. Please contact support.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">C</span>
            </div>
            <span className="text-2xl font-bold text-white">Kloud Cloud</span>
          </div>
          <p className="text-gray-400">Create your account to get started.</p>
        </div>

        {/* Features Preview */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="text-center">
            <div className="w-10 h-10 mx-auto bg-purple-500/20 rounded-lg flex items-center justify-center mb-2">
              <span className="text-purple-400">🧠</span>
            </div>
            <span className="text-xs text-gray-400">AI Analytics</span>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 mx-auto bg-blue-500/20 rounded-lg flex items-center justify-center mb-2">
              <span className="text-blue-400">📊</span>
            </div>
            <span className="text-xs text-gray-400">Real-time Data</span>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 mx-auto bg-green-500/20 rounded-lg flex items-center justify-center mb-2">
              <span className="text-green-400">🔒</span>
            </div>
            <span className="text-xs text-gray-400">Enterprise Security</span>
          </div>
        </div>

        {/* Clerk Sign Up */}
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "bg-slate-800/50 backdrop-blur-xl border border-slate-700 shadow-2xl",
              headerTitle: "text-white",
              headerSubtitle: "text-gray-400",
              socialButtonsBlockButton: "bg-slate-700 border-slate-600 text-white hover:bg-slate-600",
              socialButtonsBlockButtonText: "text-white",
              dividerLine: "bg-slate-600",
              dividerText: "text-gray-400",
              formFieldLabel: "text-gray-300",
              formFieldInput: "bg-slate-700 border-slate-600 text-white placeholder-gray-400",
              formButtonPrimary: "bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700",
              footerActionLink: "text-green-400 hover:text-green-300",
              identityPreviewText: "text-white",
              identityPreviewEditButton: "text-green-400",
            },
          }}
        />

        {/* Plan Info */}
        <div className="text-center mt-8 p-4 bg-slate-800/30 rounded-xl border border-slate-700">
          <p className="text-gray-300 text-sm font-medium mb-2">
            🎁 Start with Free Plan
          </p>
          <ul className="text-gray-400 text-xs space-y-1">
            <li>✓ 50 API calls/day</li>
            <li>✓ Basic analytics</li>
            <li>✓ Community support</li>
          </ul>
          <p className="text-purple-400 text-xs mt-3">
            Upgrade anytime for more features →
          </p>
        </div>
      </div>
    </div>
  );
}

