/** @type {import('next-sitemap').IConfig} */
const config = {
  siteUrl: process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life',
  generateRobotsTxt: false, // We have custom robots.txt
  generateIndexSitemap: true,
  sitemapSize: 7000,
  changefreq: 'daily',
  priority: 0.7,
  
  // Exclude internal/api routes
  exclude: [
    '/api/*',
    '/server-sitemap.xml',
    '/_next/*',
    '/sign-in/*',
    '/sign-up/*',
    '/auth/*',
    '/404',
    '/500'
  ],
  alternateRefs: [
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/en`, hreflang: 'en' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/sq`, hreflang: 'sq' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/de`, hreflang: 'de' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/it`, hreflang: 'it' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/fr`, hreflang: 'fr' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/es`, hreflang: 'es' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/pt`, hreflang: 'pt' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/tr`, hreflang: 'tr' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/ar`, hreflang: 'ar' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/hi`, hreflang: 'hi' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/zh`, hreflang: 'zh' },
    { href: `${process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life'}/ja`, hreflang: 'ja' },
    { href: process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL || 'https://kameleon.life', hreflang: 'x-default' },
  ],
  
  // Additional paths to include
  additionalPaths: async (config) => {
    const result = [];
    
    // High priority pages
    const highPriority = ['/', '/modules', '/pricing', '/platform', '/security', '/status', '/ocean', '/developers'];
    for (const path of highPriority) {
      result.push({
        loc: path,
        changefreq: 'daily',
        priority: 1.0,
        lastmod: new Date().toISOString(),
      });
    }
    
    // Module pages - medium-high priority
    const modules = [
      '/asi-demo',
      '/debate',
      '/dashboard',
      '/user/dashboard',
      '/terms',
      '/modules/mood-journal',
      '/modules/daily-habits',
      '/modules/focus-timer',
      '/modules/phone-sensors',
      '/modules/curiosity-ocean',
      '/modules/web-reader',
      '/modules/eeg-analysis',
      '/modules/neural-biofeedback',
      '/modules/spectrum-analyzer',
      '/modules/weather-dashboard',
      '/modules/fitness-dashboard',
      '/modules/data-collection',
      '/modules/reporting-dashboard'
    ];
    
    for (const path of modules) {
      result.push({
        loc: path,
        changefreq: 'weekly',
        priority: 0.8,
        lastmod: new Date().toISOString(),
      });
    }
    
    return result;
  },
  
  // Transform function for all pages
  transform: async (config, path) => {
    // Custom priority based on path
    let priority = config.priority;
    let changefreq = config.changefreq;
    
    if (path === '/') {
      priority = 1.0;
      changefreq = 'daily';
    } else if (path.startsWith('/modules')) {
      priority = 0.8;
      changefreq = 'weekly';
    } else if (path === '/pricing' || path === '/company') {
      priority = 0.9;
      changefreq = 'weekly';
    }
    
    return {
      loc: path,
      changefreq,
      priority,
      lastmod: config.autoLastmod ? new Date().toISOString() : undefined,
      alternateRefs: config.alternateRefs ?? [],
    };
  },
};

export default config;

