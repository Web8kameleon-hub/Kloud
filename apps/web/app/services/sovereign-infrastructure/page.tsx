export const metadata = {
  title: "Sovereign Infrastructure Services",
  description:
    "Sovereign Infrastructure Services by Kloud: secure API gateway, edge routing governance, distributed execution, and zero-trust operational control.",
  alternates: {
    canonical: "/services/sovereign-infrastructure",
  },
};

export default function SovereignInfrastructurePage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Sovereign Infrastructure Services</h1>
      <p className="mt-6 text-lg text-gray-300">
        Build and operate AI infrastructure with full control over routing,
        trust policy, runtime consistency, and deployment integrity.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Infrastructure capabilities</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Secure API gateway and policy-enforced service access</li>
          <li>Edge routing governance across distributed nodes</li>
          <li>CRDT-backed execution consistency for resilient operations</li>
          <li>Zero-downtime rollout patterns for enterprise production</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Security and control</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Zero-trust architecture with explicit verification</li>
          <li>Operational governance in one control surface</li>
          <li>Trust posture visibility with incident-aware telemetry</li>
        </ul>
      </section>
    </main>
  );
}
