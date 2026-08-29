const CITY_DATA: Record<
  string,
  { country: string; domain: string; summary: string }
> = {
  elbasan: {
    country: "Albania",
    domain: "University & AI Research",
    summary:
      "Applied AI and scientific collaboration with focus on education, telemetry, and operational intelligence.",
  },
  tirana: {
    country: "Albania",
    domain: "Medical Intelligence",
    summary:
      "Clinical and biomedical analytics for research-grade intelligence workflows.",
  },
  durres: {
    country: "Albania",
    domain: "Research & IoT",
    summary:
      "Data-intensive experimentation and sensor workflows for industrial observability.",
  },
  vlore: {
    country: "Albania",
    domain: "Marine & Environmental",
    summary:
      "Environmental monitoring, marine signal analysis, and ecological telemetry.",
  },
  shkoder: {
    country: "Albania",
    domain: "University Research",
    summary:
      "Cross-disciplinary studies in resilient systems and sustainable intelligence pipelines.",
  },
  korce: {
    country: "Albania",
    domain: "Agricultural Science",
    summary:
      "Data-driven agricultural monitoring and predictive analytics for field operations.",
  },
  sarande: {
    country: "Albania",
    domain: "Ecological Systems",
    summary:
      "Biodiversity and ecosystem signal processing for long-term operational visibility.",
  },
  prishtina: {
    country: "Kosovo",
    domain: "Medical Systems",
    summary:
      "Medical-grade telemetry and diagnostic intelligence in distributed settings.",
  },
  kostur: {
    country: "North Macedonia",
    domain: "Medical Research",
    summary:
      "Healthcare-oriented analytics and controlled research data workflows.",
  },
  athens: {
    country: "Greece",
    domain: "National Research",
    summary:
      "Multidisciplinary intelligence workflows and enterprise-grade observability.",
  },
  rome: {
    country: "Italy",
    domain: "Research Center",
    summary:
      "Large-scale research operations with AI-assisted execution and governance.",
  },
  zurich: {
    country: "Switzerland",
    domain: "Finance & Intelligence",
    summary:
      "Financial analytics and secure decision-support pipelines.",
  },
  beograd: {
    country: "Serbia",
    domain: "Industrial Optimization",
    summary:
      "Operational optimization and process intelligence for production environments.",
  },
  sofia: {
    country: "Bulgaria",
    domain: "Chemistry & Materials",
    summary:
      "Material and chemistry-oriented research with AI telemetry tracking.",
  },
  zagreb: {
    country: "Croatia",
    domain: "Biotechnology",
    summary:
      "Biotech analytics and controlled experiment orchestration.",
  },
  ljubljana: {
    country: "Slovenia",
    domain: "Quantum Systems",
    summary:
      "Advanced computing research with robust execution governance.",
  },
  vienna: {
    country: "Austria",
    domain: "Neuroscience",
    summary:
      "Neural signal analysis and cognitive telemetry pipelines.",
  },
  prague: {
    country: "Czech Republic",
    domain: "Robotics",
    summary:
      "Automation and robotics workflows with runtime observability.",
  },
  budapest: {
    country: "Hungary",
    domain: "Data Analytics",
    summary:
      "High-volume analytics, dashboards, and operational data intelligence.",
  },
  bucharest: {
    country: "Romania",
    domain: "Nanotechnology",
    summary:
      "Precision-oriented research pipelines and experimental intelligence.",
  },
  istanbul: {
    country: "Turkey",
    domain: "Trade & Logistics",
    summary:
      "Supply chain and logistics intelligence with real-time operations telemetry.",
  },
  cairo: {
    country: "Egypt",
    domain: "Archeology",
    summary:
      "Preservation data workflows and historical intelligence operations.",
  },
  jerusalem: {
    country: "Palestine",
    domain: "Cultural Heritage",
    summary:
      "Cultural systems preservation supported by secure AI-assisted workflows.",
  },
};

export async function generateStaticParams() {
  return Object.keys(CITY_DATA).map((city) => ({ city }));
}

export async function generateMetadata({ params }: { params: Promise<{ city: string }> }) {
  const { city: cityParam } = await params;
  const city = cityParam.toLowerCase();
  const data = CITY_DATA[city];

  if (!data) {
    return {
      title: "Lab Not Found | Kloud",
      description: "Requested laboratory profile could not be found.",
    };
  }

  const cityName = city.charAt(0).toUpperCase() + city.slice(1);

  return {
    title: `${cityName} Lab | Kloud by Kameleon Life`,
    description: `${cityName} laboratory profile: ${data.domain} in ${data.country}. ${data.summary}`,
    alternates: {
      canonical: `/labs/${city}`,
    },
  };
}

export default async function LabCityPage({ params }: { params: Promise<{ city: string }> }) {
  const { city: cityParam } = await params;
  const city = cityParam.toLowerCase();
  const data = CITY_DATA[city];

  if (!data) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-bold">Lab not found</h1>
      </main>
    );
  }

  const cityName = city.charAt(0).toUpperCase() + city.slice(1);

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-bold tracking-tight">{cityName} Laboratory</h1>
      <p className="mt-4 text-lg text-neutral-700">{data.summary}</p>

      <section className="mt-8 rounded-xl border border-neutral-200 p-5">
        <h2 className="text-2xl font-semibold">Technical Profile</h2>
        <p className="mt-3 text-neutral-800">
          <strong>Country:</strong> {data.country}
        </p>
        <p className="mt-1 text-neutral-800">
          <strong>Domain:</strong> {data.domain}
        </p>
      </section>

      <section className="mt-8">
        <h2 className="text-2xl font-semibold">Collaboration Intent</h2>
        <p className="mt-3 text-neutral-700">
          This location supports academic-industrial collaboration on sovereign AI operations, telemetry observability,
          and distributed execution under the Kloud by Kameleon Life framework.
        </p>
      </section>
    </main>
  );
}
