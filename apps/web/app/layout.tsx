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

// 🚀 AGGRESSIVE SEO - Maximum visibility
export const metadata: Metadata = {
  metadataBase: new URL('https://kloud.com'),
  title: {
    default: "Kloud Cloud - AI-Powered Industrial Intelligence Platform",
    template: "%s | Kloud Cloud"
  },
  description: "Kloud Cloud: The next-generation AI platform for industrial intelligence, behavioral science, and real-time analytics. Transform your data into actionable insights with our advanced machine learning solutions.",
  keywords: [
    "AI platform", "industrial intelligence", "machine learning", "behavioral science",
    "real-time analytics", "cloud computing", "neural networks", "data science",
    "IoT analytics", "predictive analytics", "cognitive computing", "deep learning",
    "automation", "smart manufacturing", "Industry 4.0", "digital transformation",
    "Kloud", "AGI", "artificial general intelligence"
  ],
  authors: [
    { name: "Ledjan Ahmati", url: "https://kloud.com" },
    { name: "ABA GmbH", url: "https://aba-gmbh.eu" }
  ],
  creator: "Ledjan Ahmati",
  publisher: "ABA GmbH",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://kloud.com',
    siteName: 'Kloud Cloud',
    title: 'Kloud Cloud - AI-Powered Industrial Intelligence',
    description: 'Transform your industrial operations with AI-powered analytics, behavioral science insights, and real-time monitoring.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Kloud Cloud - Industrial AI Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Kloud Cloud - AI-Powered Industrial Intelligence',
    description: 'Next-generation AI platform for industrial intelligence and behavioral science.',
    images: ['/og-image.png'],
    creator: '@kloud',
  },
  alternates: {
    canonical: 'https://kloud.com',
  },
  category: 'Technology',
};

const softwareApplicationSchema = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Kloud Cloud',
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
    url: 'https://kloud.com',
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.9',
    ratingCount: '150',
  },
  description: 'AI-powered industrial intelligence and behavioral science platform',
  url: 'https://kloud.com',
  author: {
    '@type': 'Organization',
    name: 'Kloud',
    url: 'https://kloud.com',
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
        {/* Organization Schema */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              "name": "Kloud Cloud",
              "url": "https://kloud.com",
              "logo": "https://kloud.com/logo.png",
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
        <link rel="canonical" href="https://kloud.com" />
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










