export const metadata = {
  title: "AI Operations Platform",
  description:
    "Enterprise AI Operations Platform by Kloud: orchestration, multi-agent execution, real-time decision intelligence, and governed production pipelines.",
  alternates: {
    canonical: "/services/ai-operations-platform",
  },
};

export default function AIOperationsPlatformPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">AI Operations Platform</h1>
      <p className="mt-6 text-lg text-gray-300">
        Kloud provides a sovereign AI operations platform for enterprise teams
        that need predictable execution, policy control, and measurable reliability.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">What this service includes</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Multi-agent AI orchestration with governed routing</li>
          <li>Real-time and batch inference pipelines</li>
          <li>Operational decision intelligence with telemetry feedback loops</li>
          <li>Trust policy enforcement for production AI workloads</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Business outcomes</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Faster incident response with runtime visibility</li>
          <li>Lower operational risk through policy-driven execution</li>
          <li>Higher service uptime and predictable AI performance</li>
        </ul>
      </section>
    </main>
  );
}
