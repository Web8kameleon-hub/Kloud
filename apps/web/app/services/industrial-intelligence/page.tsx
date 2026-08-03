export const metadata = {
  title: "Industrial Intelligence Services",
  description:
    "Industrial Intelligence Services by Kloud: predictive analytics, operational intelligence, IoT telemetry analysis, and AI-driven optimization for enterprise operations.",
  alternates: {
    canonical: "/services/industrial-intelligence",
  },
};

export default function IndustrialIntelligencePage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Industrial Intelligence Services</h1>
      <p className="mt-6 text-lg text-gray-300">
        Turn production data into strategic decisions with sovereign analytics,
        live telemetry, and adaptive operational intelligence.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Core capabilities</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Predictive analytics for uptime and maintenance planning</li>
          <li>IoT telemetry analytics for machine and process visibility</li>
          <li>Operational intelligence dashboards for leadership and teams</li>
          <li>AI-supported anomaly detection before failure propagation</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Why enterprises choose Kloud</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Decision support with measurable operational outcomes</li>
          <li>Secure, policy-governed data handling</li>
          <li>Scalable intelligence across distributed environments</li>
        </ul>
      </section>
    </main>
  );
}
