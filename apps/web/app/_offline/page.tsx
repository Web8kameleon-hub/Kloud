"use client";

import Link from "next/link";

export default function OfflinePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Offline Icon */}
        <div className="mb-8">
          <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-violet-500/20 to-purple-500/20 flex items-center justify-center border border-violet-500/30">
            <svg
              className="w-12 h-12 text-violet-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-white mb-4">
          Je Offline
        </h1>

        {/* Description */}
        <p className="text-gray-400 mb-8">
          Nuk kemi lidhje me internetin. Kontrollo lidhjen dhe provo përsëri.
        </p>

        {/* Retry Button */}
        <button
          onClick={() => window.location.reload()}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-violet-500/25"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Provo Përsëri
        </button>

        {/* Cached Content Notice */}
        <div className="mt-8 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
          <p className="text-sm text-gray-500">
            🔒 Disa faqe të ruajtura janë të disponueshme offline.
          </p>
          <Link
            href="/"
            className="text-violet-400 hover:text-violet-300 text-sm mt-2 inline-block"
          >
            Shko në faqen kryesore →
          </Link>
        </div>

        {/* Kloud Branding */}
        <div className="mt-12 flex items-center justify-center gap-2 text-gray-600">
          <span className="text-2xl">🧠</span>
          <span className="font-medium">Kloud Cloud</span>
        </div>
      </div>
    </div>
  );
}

