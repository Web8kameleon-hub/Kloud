export default function Head() {
  const pageUrl = 'https://kameleon.life/platform';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: 'Kloud Platform Architecture Services',
    serviceType: 'AI Infrastructure and Industrial Intelligence Platform',
    provider: {
      '@type': 'Organization',
      name: 'Kameleon Life',
      url: 'https://kameleon.life',
    },
    areaServed: 'Worldwide',
    url: pageUrl,
    description:
      'Global AI infrastructure services, distributed execution, telemetry intelligence, and enterprise operational governance.',
  };

  return (
    <>
      <title>AI Infrastructure Platform Services | Kloud Architecture</title>
      <meta
        name="description"
        content="Explore Kloud global platform services: AI infrastructure, distributed execution, telemetry analytics, and enterprise-grade operational governance."
      />
      <meta
        name="keywords"
        content="ai infrastructure platform,industrial intelligence platform,distributed execution engine,enterprise ai services,operational governance platform,global ai platform"
      />
      <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="website" />
      <meta property="og:title" content="AI Infrastructure Platform Services | Kloud Architecture" />
      <meta
        property="og:description"
        content="Kloud platform services for industrial AI, distributed systems, telemetry intelligence, and large-scale operations."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kloud Platform Services" />
      <meta
        name="twitter:description"
        content="Global AI infrastructure and operational intelligence services for enterprise teams."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
