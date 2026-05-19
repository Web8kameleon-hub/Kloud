export default function Head() {
  const pageUrl = 'https://kameleon.life/ocean';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: 'Ocean Core AI Orchestration Service',
    serviceType: 'AI Orchestration and Operational Assistant',
    provider: {
      '@type': 'Organization',
      name: 'Kameleon Life',
      url: 'https://kameleon.life',
    },
    areaServed: 'Worldwide',
    url: pageUrl,
    description:
      'Ocean Core delivers real-time AI orchestration, technical guidance, operational routing, and enterprise knowledge workflows.',
  };

  return (
    <>
      <title>Ocean Core AI Service | Real-Time Orchestration Assistant</title>
      <meta
        name="description"
        content="Use Ocean Core for real-time AI orchestration, technical guidance, troubleshooting workflows, and enterprise operational assistance."
      />
      <meta
        name="keywords"
        content="ocean core ai,ai orchestration assistant,enterprise ai assistant,technical ai copilot,real-time ai routing,knowledge workflow ai"
      />
      <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="website" />
      <meta property="og:title" content="Ocean Core AI Service | Real-Time Orchestration Assistant" />
      <meta
        property="og:description"
        content="Interactive AI service for technical operations, routing, and knowledge-driven decision workflows."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Ocean Core AI Service" />
      <meta
        name="twitter:description"
        content="Real-time AI orchestration and enterprise technical guidance with Ocean Core."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
