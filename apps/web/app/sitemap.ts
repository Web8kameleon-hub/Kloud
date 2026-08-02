const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://kameleon.life";

export default function sitemap() {
  const now = new Date();

  const routes = [
    "",
    "/developers",
    "/dashboard",
    "/company",
    "/security",
    "/status",
    "/modules",
    "/research-partnerships",
    "/release-notes",
    "/services/ai-operations-platform",
    "/services/industrial-intelligence",
    "/services/sovereign-infrastructure",
    "/services/observability-telemetry",
  ];

  const labCities = [
    "elbasan",
    "tirana",
    "durres",
    "vlore",
    "shkoder",
    "korce",
    "sarande",
    "prishtina",
    "kostur",
    "athens",
    "rome",
    "zurich",
    "beograd",
    "sofia",
    "zagreb",
    "ljubljana",
    "vienna",
    "prague",
    "budapest",
    "bucharest",
    "istanbul",
    "cairo",
    "jerusalem",
  ];

  const labRoutes = labCities.map((city) => `/labs/${city}`);
  const allRoutes = [...routes, ...labRoutes];

  return allRoutes.map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: now,
    changeFrequency: route === "" ? "daily" : "weekly",
    priority: route === "" ? 1 : 0.8,
  }));
}
