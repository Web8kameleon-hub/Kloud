import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { RequestLogger } from "../src/components/telemetry/RequestLogger";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { DynamicFavicon } from "../src/components/DynamicFavicon";

// Check if Clerk is configured with a REAL key (not placeholder)
const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '';
const isClerkConfigured = clerkKey.startsWith('pk_') && !clerkKey.includes('YOUR_CLERK');

// Dynamic import for ClerkProvider - only if configured
const ClerkProvider = isClerkConfigured 
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  ? require("@clerk/nextjs").ClerkProvider 
  : ({ children }: { children: React.ReactNode }) => <>{children}</>;


const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://kameleon.life';
const siteName = 'Kameleon Life';
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
    default: "Kameleon Life - AI-Powered Industrial Intelligence Platform",
    template: "%s | Kameleon Life"
  },
  description: "Kameleon Life is the next-generation AI platform for industrial intelligence, behavioral science, EEG analytics, real-time monitoring, and adaptive automation. Transform data into actionable insights.",
  keywords: [
    "kameleon life", "kameleon.life", "ai platform", "industrial intelligence",
    "machine learning platform", "behavioral science ai", "real-time analytics",
    "eeg analysis platform", "neural analytics", "biofeedback analytics",
    "curiosity ocean ai", "multilingual ai assistant", "fastapi microservices",
    "cloud-native ai", "predictive analytics", "cognitive computing",
    "deep learning services", "iot analytics", "telemetry analytics",
    "signal processing ai", "audio synthesis ai", "api orchestration",
    "enterprise api platform", "saas ai infrastructure", "automation platform",
    "smart manufacturing ai", "industry 4.0 ai", "digital transformation",
    "system monitoring ai", "ai observability", "payment enabled saas",
    "stripe sepa paypal integration", "jwt authentication api", "secure api gateway",
    "data intelligence platform", "ai for operations", "adaptive intelligence",
    "kloud cloud", "albi", "alba", "jona", "agi ecosystem",
    "enterprise ai platform", "ai infrastructure", "ai orchestration platform",
    "workflow automation ai", "ai observability platform", "agent telemetry",
    "predictive maintenance ai", "digital twin intelligence", "neurotech platform",
    "llm orchestration", "model serving platform", "real-time decision intelligence",
    "edge ai platform", "distributed systems monitoring", "api-first ai platform",
    "industrial automation software", "adaptive ai assistant", "sovereign ai cloud",
    "ai analytics dashboard", "iot telemetry platform", "event-driven ai",
    "multi-agent platform", "operational ai", "machine intelligence software"
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
    localeAlternate: ['sq_AL', 'de_DE', 'it_IT', 'fr_FR', 'es_ES', 'pt_PT', 'tr_TR', 'ar_SA', 'hi_IN', 'zh_CN', 'ja_JP'],
    url: siteUrl,
    siteName,
    title: 'Kameleon Life - AI-Powered Industrial Intelligence',
    description: 'Transform operations with AI analytics, behavioral science insights, EEG processing, and real-time monitoring.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Kameleon Life - Industrial AI Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Kameleon Life - AI-Powered Industrial Intelligence',
    description: 'AI platform for industrial intelligence, behavioral science, and real-time analytics.',
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
  description: 'AI-powered industrial intelligence and behavioral science platform',
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
  name: siteName,
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
              "name": "Kameleon Life",
              "url": siteUrl,
              "logo": `${siteUrl}/logo.png`,
              "legalName": "ABA GmbH",
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
                "email": "support@kloud.com",
                "availableLanguage": ["English", "Albanian"]
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
        {isClerkConfigured ? (
          <ClerkProvider
            appearance={{
              variables: {
                colorPrimary: '#10b981',
              }
            }}
          >
            <RequestLogger />
            {children}
          </ClerkProvider>
        ) : (
          <>
            <RequestLogger />
            {children}
          </>
        )}
      </body>
    </html>
  );
}










