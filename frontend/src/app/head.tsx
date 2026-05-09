/**
 * HEAD METADATA - Production Level
 * SEO, Performance Monitoring, Analytics Integration
 * Kloud Cloud - Final Phase Optimization
 */

declare global {
  interface Window {
    webVitals?: any;
  }
}

export default function Head() {
  return (
    <>
      {/* Primary Meta Tags */}
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      <meta name="description" content="Kloud Industrial Cloud Platform - Real-time AI monitoring, advanced analytics, and distributed orchestration" />
      <meta name="keywords" content="industrial cloud, AI monitoring, Analytical Intelligence, Creative Intelligence, ASI, real-time analytics" />
      <meta name="author" content="Kloud Team" />
      <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
      <meta name="theme-color" content="#1a1a2e" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

      {/* Open Graph */}
      <meta property="og:type" content="website" />
      <meta property="og:title" content="Kloud Industrial Cloud Platform" />
      <meta property="og:description" content="Advanced AI monitoring and distributed orchestration for industrial applications" />
      <meta property="og:image" content="/og-image.png" />
      <meta property="og:site_name" content="Kloud Cloud" />
      <meta property="og:locale" content="en_US" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Kloud Industrial Cloud Platform" />
      <meta name="twitter:description" content="Real-time AI monitoring and analytics" />
      <meta name="twitter:image" content="/twitter-image.png" />

      {/* Performance & Monitoring */}
      <meta name="timing-allow-origin" content="*" />
      <meta name="x-ua-compatible" content="IE=edge" />

      {/* PWA Manifest */}
      <link rel="manifest" href="/manifest.json" />
      <link rel="icon" href="/favicon.ico" type="image/x-icon" />
      <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

      {/* Preload Critical Resources */}
      <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      <link rel="preload" href="/styles/globals.css" as="style" />
      <link rel="prefetch" href="/api/health" as="fetch" crossOrigin="use-credentials" />

      {/* DNS Prefetch */}
      <link rel="dns-prefetch" href="//api.kloud.com" />
      <link rel="dns-prefetch" href="//analytics.kloud.com" />
      <link rel="dns-prefetch" href="//cdn.kloud.com" />

      {/* Performance Monitoring */}
      <script
        async
        src="https://cdn.jsdelivr.net/npm/web-vitals@3/dist/web-vitals.iife.js"
        onLoad={() => {
          if (window.webVitals) {
            window.webVitals.getCLS(metric => console.log('CLS:', metric.value));
            window.webVitals.getFID(metric => console.log('FID:', metric.value));
            window.webVitals.getFCP(metric => console.log('FCP:', metric.value));
            window.webVitals.getLCP(metric => console.log('LCP:', metric.value));
            window.webVitals.getTTFB(metric => console.log('TTFB:', metric.value));
          }
        }}
      />
    {/* Error Tracking Meta */}
    <meta name="error-tracking" content="enabled" />
      {/* Analytics - Google Tag Manager */}
      <script
        async
        src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID || 'G-XXXXXXXXXX'}`}
      />
      <script
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_ID || 'G-XXXXXXXXXX'}', {
              'page_path': window.location.pathname,
              'debug_mode': ${process.env.NODE_ENV !== 'production'}
            });
          `,
        }}
      />

      {/* Service Worker Registration */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            if ('serviceWorker' in navigator) {
              window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').catch(err => 
                  console.warn('ServiceWorker registration failed:', err)
                );
              });
            }
          `,
        }}
      />

      {/* Real-time Monitoring Script */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            (function() {
              const sessionId = '${Math.random().toString(36).substr(2, 9)}';
              const startTime = Date.now();
              
              // Performance Observer
              if (window.PerformanceObserver) {
                try {
                  const perfObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                      console.log('[PERF]', entry.name, entry.duration.toFixed(2) + 'ms');
                    }
                  });
                  perfObserver.observe({ entryTypes: ['navigation', 'resource', 'paint', 'measure'] });
                } catch(e) {
                  console.warn('PerformanceObserver not supported');
                }
              }
              
              // Error Tracking
              window.addEventListener('error', (event) => {
                console.error('[ERROR]', event.error);
                navigator.sendBeacon('/api/errors', JSON.stringify({
                  sessionId,
                  type: 'js_error',
                  message: event.message,
                  stack: event.error?.stack,
                  timestamp: new Date().toISOString()
                }));
              });
              
              // Unhandled Promise Rejection
              window.addEventListener('unhandledrejection', (event) => {
                console.error('[UNHANDLED]', event.reason);
                navigator.sendBeacon('/api/errors', JSON.stringify({
                  sessionId,
                  type: 'unhandled_rejection',
                  message: String(event.reason),
                  timestamp: new Date().toISOString()
                }));
              });
            })();
          `,
        }}
      />

      {/* Title - Dynamic based on Page */}
      <title>Kloud Industrial Cloud | AI Monitoring & Orchestration</title>

      {/* Canonical URL */}
      <link rel="canonical" href="https://kloud.com" />

      {/* Alternate Links */}
      <link rel="alternate" hrefLang="en" href="https://kloud.com" />
      <link rel="alternate" hrefLang="sq" href="https://kloud.com/sq" />

      {/* Color Scheme */}
      <meta name="color-scheme" content="dark light" />
      <style
        dangerouslySetInnerHTML={{
          __html: `
            :root {
              color-scheme: dark;
              --primary: #1a1a2e;
              --accent: #16c784;
              --danger: #ef4444;
            }
            @media (prefers-color-scheme: light) {
              :root {
                color-scheme: light;
                --primary: #ffffff;
              }
            }
          `,
        }}
      />
    </>
  )
}

