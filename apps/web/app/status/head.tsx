export default function Head() {
  const pageUrl = 'https://kameleon.life/status';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: 'Kameleon Life Status',
    description:
      'Real-time status for Kameleon Life services, uptime monitoring, incidents, and platform availability.',
    url: pageUrl,
    isPartOf: {
      '@type': 'WebSite',
      name: 'Kameleon Life',
      url: 'https://kameleon.life',
    },
  };

  return (
    <>
      <title>Kameleon Life Status | Real-Time Uptime and Incidents</title>
      <meta
        name="description"
        content="Track real-time Kameleon Life uptime, incidents, and service health for API, AI engines, database, and web platform."
      />
      <meta
        name="keywords"
        content="kameleon life status,kameleon status page,api uptime monitor,ai platform status,incident history,service health"
      />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="website" />
      <meta property="og:title" content="Kameleon Life Status | Real-Time Uptime and Incidents" />
      <meta
        property="og:description"
        content="Live status dashboard for Kameleon Life services with uptime and incident transparency."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kameleon Life Status" />
      <meta
        name="twitter:description"
        content="Live uptime and incident tracking for Kameleon Life services."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
