export const metadata = {
  title: "Company | Ledjan Ahmati · ABA GmbH · Bochum Germany",
  description:
    "Kloud and Kameleon Life are built by Ledjan Ahmati under ABA GmbH in Bochum, Germany. Enterprise AI, sovereign infrastructure, and operational intelligence services.",
  alternates: {
    canonical: "/company",
  },
};

export default function CompanyPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Company</h1>
      <p className="mt-6 text-lg text-gray-300">
        Kloud is developed and operated by Ledjan Ahmati and ABA GmbH, based in Bochum, Germany.
        Our mission is to deliver sovereign intelligence infrastructure for enterprise operations.
      </p>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">Identity and leadership</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Founder and creator: Ledjan Ahmati</li>
          <li>Operating entity: ABA GmbH</li>
          <li>Location: Bochum, Germany</li>
          <li>Contact: clisonix@pm.me</li>
        </ul>
      </section>

      <section className="mt-10 space-y-4">
        <h2 className="text-2xl font-semibold">What we deliver</h2>
        <ul className="list-disc space-y-2 pl-6 text-gray-300">
          <li>Sovereign Intelligence Fabric for AI and infrastructure operations</li>
          <li>Cognitive telemetry and observability for production systems</li>
          <li>Distributed execution with governance, trust, and policy control</li>
          <li>Enterprise-grade security posture and operational reliability</li>
        </ul>
      </section>
    </main>
  );
}
