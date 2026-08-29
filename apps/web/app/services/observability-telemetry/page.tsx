export const metadata = {
  title: "Observability and Telemetry Services",
  description:
    "Observability and Telemetry Services by Kloud: agent telemetry, AI observability, runtime monitoring, anomaly detection, and distributed systems visibility.",
  alternates: {
    canonical: "/services/observability-telemetry",
  },
};

export default function ObservabilityTelemetryPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Observability and Telemetry Services</h1>
      <p className="mt-6 text-lg text-gray-300">
        Gain deep runtime awareness with cognitive telemetry signals, service health
        supervision, and distributed system monitoring designed for enterprise AI operations.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Telemetry stack coverage</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Behavioral telemetry signals (BTI, DAS, PFD)</li>
          <li>Runtime monitoring for AI pipelines and APIs</li>
          <li>Anomaly tracking with operational context</li>
          <li>Distributed systems observability across nodes</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Operational value</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Faster root-cause analysis and incident response</li>
          <li>Higher confidence in AI production stability</li>
          <li>Unified monitoring posture for platform teams</li>
        </ul>
      </section>
    </main>
  );
}
