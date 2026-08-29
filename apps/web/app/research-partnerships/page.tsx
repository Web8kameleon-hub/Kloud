export const metadata = {
  title: "Research & Partnerships | Kloud by Kameleon Life",
  description:
    "Academic and industrial collaboration framework by ABA GmbH and Ledjan Ahmati: EU grants, university partnerships, 23-location laboratory network, and applied AI research.",
  alternates: {
    canonical: "/research-partnerships",
  },
};

const LABS = [
  "Elbasan",
  "Tirana",
  "Durrës",
  "Vlorë",
  "Shkodër",
  "Korçë",
  "Sarandë",
  "Prishtina",
  "Kostur",
  "Athens",
  "Rome",
  "Zurich",
  "Beograd",
  "Sofia",
  "Zagreb",
  "Ljubljana",
  "Vienna",
  "Prague",
  "Budapest",
  "Bucharest",
  "Istanbul",
  "Cairo",
  "Jerusalem",
];

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "What is the purpose of Kloud research partnerships?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Kloud research partnerships align academia and industry for sovereign AI operations, industrial intelligence, distributed infrastructure, cybersecurity, and telemetry observability.",
      },
    },
    {
      "@type": "Question",
      name: "Which institutions can collaborate?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Universities, applied research centers, innovation labs, and public-private consortia can collaborate through structured pilot programs and grant-aligned research tracks.",
      },
    },
  ],
};

export default function ResearchPartnershipsPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <h1 className="text-4xl font-bold tracking-tight">Research & Partnerships</h1>
      <p className="mt-4 text-lg text-neutral-700">
        Kloud by Kameleon Life enables applied research partnerships across AI operations, industrial intelligence,
        sovereign infrastructure, and security telemetry. This framework is designed for measurable academic impact
        and production-grade outcomes.
      </p>

      <section className="mt-10">
        <h2 className="text-2xl font-semibold">Institutional Collaboration Model</h2>
        <p className="mt-3 text-neutral-700">
          Collaboration is structured for universities, labs, and innovation ecosystems with clear workstreams:
          architecture research, validation, publication, and production pilot transfer.
        </p>
      </section>

      <section className="mt-10">
        <h2 className="text-2xl font-semibold">Grant & Funding Readiness</h2>
        <p className="mt-3 text-neutral-700">
          The partnership model supports Horizon Europe, Digital Europe, Erasmus+, AKKSHI, and other R&D instruments
          through a joint academic-industrial approach.
        </p>
      </section>

      <section className="mt-10">
        <h2 className="text-2xl font-semibold">23-Location Laboratory Network</h2>
        <ul className="mt-4 grid grid-cols-2 gap-2 text-neutral-800 md:grid-cols-3">
          {LABS.map((lab) => (
            <li key={lab} className="rounded border border-neutral-200 px-3 py-2">
              {lab}
            </li>
          ))}
        </ul>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
    </main>
  );
}
