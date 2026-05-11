/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: process.env.SITE_URL || 'https://kameleon.life',
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
    '/404',
    '/500'
  ],
  
  // Additional paths to include
  additionalPaths: async (config) => {
    const result = [];
    
    // High priority pages
    const highPriority = ['/', '/modules', '/pricing', '/company', '/developers'];
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
      '/modules/mood-journal',
      '/modules/daily-habits',
      '/modules/focus-timer',
      '/modules/phone-sensors',
      '/modules/curiosity-ocean',
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

