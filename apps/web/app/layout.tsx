import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { RequestLogger } from "../src/components/telemetry/RequestLogger";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { DynamicFavicon } from "../src/components/DynamicFavicon";



const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://kameleon.life";
const siteName = "Kloud";
const brandName = "Kameleon Life";
const supportedLanguages: Record<string, string> = {
  en: `${siteUrl}/en`,
  sq: `${siteUrl}/sq`,
  de: `${siteUrl}/de`,
  it: `${siteUrl}/it`,
  fr: `${siteUrl}/fr`,
  es: `${siteUrl}/es`,
  pt: `${siteUrl}/pt`,
  tr: `${siteUrl}/tr`,
  ar: `${siteUrl}/ar`,
  hi: `${siteUrl}/hi`,
  zh: `${siteUrl}/zh`,
  ja: `${siteUrl}/ja`,
  'x-default': siteUrl,
};

// 🚀 AGGRESSIVE SEO - Maximum visibility
export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Kloud | Sovereign Intelligence Fabric by Kameleon Life",
    template: "%s | Kloud",
  },
  description:
    "Kloud by Kameleon Life is a sovereign intelligence fabric for AI operations, industrial intelligence, telemetry observability, secure distributed execution, and enterprise governance.",
  keywords: [
    "kloud",
    "kameleon life",
    "kameleon.life",
    "ledjan ahmati",
    "ABA GmbH",
    "Bochum Germany",
    "sovereign intelligence fabric",
    "enterprise ai platform",
    "ai orchestration platform",
    "multi-agent ai platform",
    "ai operations platform",
    "industrial intelligence services",
    "predictive analytics",
    "iot telemetry analytics",
    "operational intelligence platform",
    "sovereign ai cloud",
    "distributed execution engine",
    "secure api gateway",
    "edge routing governance",
    "agent telemetry platform",
    "ai observability",
    "runtime monitoring ai",
    "distributed systems monitoring",
    "real-time decision intelligence",
    "behavioral telemetry",
    "BTI DAS PFD",
    "CRDT runtime consistency",
    "zero trust governance",
    "AI infrastructure",
    "platform reliability",
  ],
  authors: [
    { name: "Ledjan Ahmati", url: siteUrl },
    { name: "ABA GmbH", url: "https://aba-gmbh.eu" }
  ],
  creator: "Ledjan Ahmati",
  publisher: "ABA GmbH",
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  referrer: 'origin-when-cross-origin',
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
    yandex: process.env.NEXT_PUBLIC_YANDEX_VERIFICATION,
    yahoo: process.env.NEXT_PUBLIC_YAHOO_SITE_VERIFICATION,
    other: {
      'msvalidate.01': process.env.NEXT_PUBLIC_BING_SITE_VERIFICATION ?? '',
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    alternateLocale: ['sq_AL', 'de_DE', 'it_IT', 'fr_FR', 'es_ES', 'pt_PT', 'tr_TR', 'ar_SA', 'hi_IN', 'zh_CN', 'ja_JP'],
    url: siteUrl,
    siteName,
    title: "Kloud | Sovereign Intelligence Fabric by Kameleon Life",
    description:
      "Run AI operations with cognitive telemetry, distributed execution, and zero-trust governance in one enterprise control surface.",
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: "Kloud - Sovereign Intelligence Fabric",
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: "Kloud | Sovereign Intelligence Fabric",
    description:
      "Enterprise AI operations platform for industrial intelligence, secure execution, and telemetry observability.",
    images: ['/og-image.png'],
    creator: '@kameleonlife',
  },
  alternates: {
    canonical: siteUrl,
    languages: supportedLanguages,
  },
  category: 'Technology',
};

const softwareApplicationSchema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Kameleon Life',
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  offers: [
    {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'EUR',
    },
    {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
  ],
  creator: {
    '@type': 'Person',
    name: 'Ledjan Ahmati',
    url: siteUrl,
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.9',
    ratingCount: '150',
  },
  description: 'Sovereign intelligence fabric for AI operations, infrastructure governance, and telemetry observability',
  url: siteUrl,
  author: {
    '@type': 'Organization',
    name: 'Kameleon Life',
    url: siteUrl,
  },
};

const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: `${siteName} by ${brandName}`,
  url: siteUrl,
  inLanguage: ['en', 'sq', 'de', 'it', 'fr', 'es', 'pt', 'tr', 'ar', 'hi', 'zh', 'ja'],
  potentialAction: {
    '@type': 'SearchAction',
    target: `${siteUrl}/search?q={search_term_string}`,
    'query-input': 'required name=search_term_string',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Schema.org Structured Data for Rich Snippets */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(softwareApplicationSchema),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(websiteSchema),
          }}
        />
        {/* Organization Schema */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              "name": "ABA GmbH",
              "url": siteUrl,
              "logo": `${siteUrl}/logo.png`,
              "legalName": "ABA GmbH",
              "brand": [
                "Kloud",
                "Kameleon Life"
              ],
              "foundingLocation": {
                "@type": "Place",
                "name": "Bochum, Germany"
              },
              "founder": {
                "@type": "Person",
                "name": "Ledjan Ahmati"
              },
              "owner": {
                "@type": "Person",
                "name": "Ledjan Ahmati"
              },
              "sameAs": [
                "https://github.com/LedjanAhmati/Kloud-cloud",
                "https://twitter.com/kloud"
              ],
              "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "customer support",
                "email": "clisonix@pm.me",
                "availableLanguage": ["English", "Albanian", "German"]
              }
            })
          }}
        />
        <link rel="canonical" href={siteUrl} />
        <meta name="theme-color" content="#6366f1" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Kloud" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
                window.addEventListener('load', function () {
                  navigator.serviceWorker.register('/sw-music-studio.js').catch(function () {});
                });
              }
            `,
          }}
        />
      </head>
      <body
        className={`${inter.variable} antialiased`}
        suppressHydrationWarning
      >
        <RequestLogger />
        {children}
      </body>
    </html>
  );
}










