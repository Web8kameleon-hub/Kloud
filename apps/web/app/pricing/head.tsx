export default function Head() {
  const pageUrl = 'https://kameleon.life/pricing';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: 'Kloud Subscription Plans',
    brand: {
      '@type': 'Brand',
      name: 'Kameleon Life',
    },
    description:
      'Transparent pricing plans for AI services, enterprise operations, and Curiosity Ocean access.',
    offers: {
      '@type': 'AggregateOffer',
      priceCurrency: 'EUR',
      lowPrice: '0',
      highPrice: '29.99',
      offerCount: '3',
      availability: 'https://schema.org/InStock',
    },
    url: pageUrl,
  };

  return (
    <>
      <title>Kloud Pricing | AI Services Plans for Teams and Enterprise</title>
      <meta
        name="description"
        content="Compare Kloud pricing plans for AI services, Curiosity Ocean access, research tools, and enterprise operational features."
      />
      <meta
        name="keywords"
        content="ai platform pricing,enterprise ai pricing,curiosity ocean pricing,saas ai plans,industrial ai subscription,team ai pricing"
      />
      <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="website" />
      <meta property="og:title" content="Kloud Pricing | AI Services Plans for Teams and Enterprise" />
      <meta
        property="og:description"
        content="Simple, transparent AI platform pricing with free, pro, and team options."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kloud Pricing" />
      <meta
        name="twitter:description"
        content="Transparent pricing for AI services, research tools, and enterprise features."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
