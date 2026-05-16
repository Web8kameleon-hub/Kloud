export default function Head() {
  const pageUrl = 'https://kameleon.life/developers';
  const imageUrl = 'https://kameleon.life/og-image.png';
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'TechArticle',
    headline: 'Kameleon Life Developer API Documentation',
    description:
      'Official API documentation for Kameleon Life with endpoint references, examples, billing usage metrics, and authentication guides.',
    url: pageUrl,
    about: ['API documentation', 'AI API', 'developer portal'],
    publisher: {
      '@type': 'Organization',
      name: 'Kameleon Life',
      url: 'https://kameleon.life',
    },
  };

  return (
    <>
      <title>Kameleon Life API Docs | Developer Portal</title>
      <meta
        name="description"
        content="Browse Kameleon Life API documentation with live endpoints, code examples, metered usage pricing, and developer integration guides."
      />
      <meta
        name="keywords"
        content="kameleon life api docs,developer api portal,ai api documentation,rest api examples,api pricing,metered billing"
      />
      <link rel="canonical" href={pageUrl} />

      <meta property="og:type" content="article" />
      <meta property="og:title" content="Kameleon Life API Docs | Developer Portal" />
      <meta
        property="og:description"
        content="Developer portal with endpoint references, live API tests, SDK examples, and billing metrics."
      />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:image" content={imageUrl} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kameleon Life API Docs" />
      <meta
        name="twitter:description"
        content="Official developer docs and endpoint references for Kameleon Life APIs."
      />
      <meta name="twitter:image" content={imageUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
