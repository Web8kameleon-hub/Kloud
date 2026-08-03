export const metadata = {
  title: "Release Notes | Kloud by Kameleon Life",
  description:
    "Official release notes for Kloud ecosystem updates: CLX-AI, Hotguard, confidence scoring, validation pipelines, and operational reliability improvements.",
  alternates: {
    canonical: "/release-notes",
  },
};

const notes = [
  {
    version: "clx-ai/v2026.05.07-final",
    summary:
      "Supersedes immutable release with dynamic confidence scoring and improved PowerShell launcher delegation.",
    highlights: [
      "Dynamic confidence scoring in ecosystem_ops_10min.py",
      "PowerShell launcher delegates to run_clx_hotguard.py",
      "Robust import check with OK_CLX_IMPORT",
      "Clarified matched_rate vs avg_confidence telemetry metrics",
    ],
    validation: [
      "validate_package.py -> PASS",
      "pytest suite -> PASS",
      "run_clx_hotguard.py smoke -> PASS",
      "run_clx_hotguard_cli.ps1 smoke -> PASS",
    ],
  },
];

export default function ReleaseNotesPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <h1 className="text-4xl font-bold tracking-tight">Release Notes</h1>
      <p className="mt-4 text-lg text-neutral-700">
        Central changelog for stability, telemetry, security, and runtime upgrades across the Kloud ecosystem.
      </p>

      <div className="mt-10 space-y-8">
        {notes.map((note) => (
          <article key={note.version} className="rounded-xl border border-neutral-200 p-6">
            <h2 className="text-2xl font-semibold">{note.version}</h2>
            <p className="mt-2 text-neutral-700">{note.summary}</p>

            <h3 className="mt-5 text-lg font-semibold">Highlights</h3>
            <ul className="mt-2 list-disc space-y-1 pl-6 text-neutral-800">
              {note.highlights.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>

            <h3 className="mt-5 text-lg font-semibold">Validation</h3>
            <ul className="mt-2 list-disc space-y-1 pl-6 text-neutral-800">
              {note.validation.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </main>
  );
}
