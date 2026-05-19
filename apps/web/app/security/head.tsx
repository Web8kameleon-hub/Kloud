export default function Head() {
  const pageUrl = 'https://kameleon.life/security';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: 'Kloud Security and Compliance Services',
    serviceType: 'Enterprise Security and Trust Governance',
    provider: {
      '@type': 'Organization',
      name: 'Kameleon Life',
      url: 'https://kameleon.life',
    },
    areaServed: 'Worldwide',
    url: pageUrl,
    description:
      'Enterprise security services with encryption, zero-trust architecture, audit logging, and compliance-ready controls.',
  };

  return (
    <>
      <title>Enterprise Security Services | Zero-Trust AI Infrastructure</title>
      <meta
        name="description"
        content="Kloud security services include zero-trust architecture, encryption, audit logging, API security, and compliance-ready controls for enterprise AI systems."
      />
      <meta
        name="keywords"
        content="enterprise security services,zero trust architecture,ai infrastructure security,api security platform,compliance ready ai,gdpr security controls"
      />
      <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="website" />
      <meta property="og:title" content="Enterprise Security Services | Zero-Trust AI Infrastructure" />
      <meta
        property="og:description"
        content="Security-first architecture with encryption, threat protection, governance, and compliance for production AI platforms."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kloud Security Services" />
      <meta
        name="twitter:description"
        content="Zero-trust security and compliance controls for enterprise AI and distributed infrastructure."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
