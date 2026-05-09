import { NextResponse } from 'next/server';

/**
 * Root API endpoint - Returns API info and available endpoints
 */
export async function GET() {
  return NextResponse.json({
    name: 'Clisonix Cloud API',
    version: '1.0.0',
    status: 'operational',
    timestamp: new Date().toISOString(),
    documentation: 'https://clisonix.com/developers',
    company: {
      brand: 'Clisonix Cloud',
      legal_name: 'ABA GmbH',
      owner: 'Ledjan Ahmati',
      support: 'support@clisonix.com',
    },
    billing: {
      model: 'pay-as-you-go',
      meter_events: ['api_request', 'ocean_chat', 'vision_job', 'audio_job', 'export_job'],
      base_currency: 'EUR',
      stripe_checkout_endpoint: '/api/billing/checkout',
    },
    auth: {
      provider: 'Clerk',
      supported_login: ['email', 'phone_sms'],
      note: 'Phone/SMS login requires Clerk phone number sign-in to be enabled in dashboard configuration.',
    },
    endpoints: {
      health: {
        'GET /api/asi/health': 'ASI Trinity health status',
        'GET /api/asi/trinity': 'Full ASI Trinity metrics',
        'GET /api/reporting/health': 'Reporting service health',
        'GET /api/reporting/dashboard': 'Dashboard metrics',
      },
      modules: {
        'GET /api/ocean': 'Curiosity Ocean AI chat',
        'GET /api/pulse': 'Pulse real-time data',
        'GET /api/vision': 'Vision AI processing',
        'GET /api/grid': 'Grid computing status',
      },
      billing: {
        'POST /api/billing/checkout': 'Create Stripe checkout session',
        'GET /api/billing/subscription': 'Read active subscription',
        'GET /api/billing/invoices': 'List invoices',
      }
    },
    support: 'support@clisonix.com'
  });
}
