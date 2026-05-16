/**
 * Kloud User Account & Billing Dashboard
 * Manage subscriptions, billing, profile settings
 */

"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useTranslation } from '@/lib/i18n'

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  plan: 'free' | 'starter' | 'professional' | 'enterprise'
  company?: string
  phone?: string
  timezone: string
  language: string
  createdAt: string
}

interface Subscription {
  id: string
  plan: string
  status: 'active' | 'canceled' | 'past_due' | 'trialing'
  currentPeriodStart: string
  currentPeriodEnd: string
  cancelAtPeriodEnd: boolean
  amount: number
  currency: string
  interval: 'month' | 'year'
}

interface Invoice {
  id: string
  date: string
  amount: number
  currency: string
  status: 'paid' | 'pending' | 'failed'
  pdfUrl?: string
}

interface PaymentMethod {
  id: string
  type: 'card' | 'paypal' | 'bank'
  last4?: string
  brand?: string
  expiryMonth?: number
  expiryYear?: number
  isDefault: boolean
}

interface ApiKey {
  id: string
  key: string
  name: string
  createdAt: string
  lastUsed?: string
}

interface BillingAddress {
  line1: string
  line2?: string
  city: string
  state?: string
  postal_code: string
  country: string
  name?: string
  phone?: string
}

const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    interval: 'month',
    features: [
      '3 Data Sources',
      '1,000 Data Points/month',
      'Basic Analytics',
      'Community Support',
      '7-day Data Retention'
    ],
    color: 'gray'
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    interval: 'month',
    features: [
      '10 Data Sources',
      '50,000 Data Points/month',
      'Advanced Analytics',
      'Email Support',
      '30-day Data Retention',
      'API Access',
      'Excel Export'
    ],
    color: 'blue',
    popular: false
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 99,
    interval: 'month',
    features: [
      'Unlimited Data Sources',
      '500,000 Data Points/month',
      'Real-time Analytics',
      'Priority Support',
      '1-year Data Retention',
      'Full API Access',
      'All Export Formats',
      'Custom Dashboards',
      'Team Collaboration (5 users)'
    ],
    color: 'purple',
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 299,
    interval: 'month',
    features: [
      'Unlimited Everything',
      'Dedicated Infrastructure',
      '24/7 Phone Support',
      'Unlimited Data Retention',
      'SSO & SAML',
      'Custom Integrations',
      'SLA Guarantee',
      'Unlimited Team Members',
      'On-premise Option'
    ],
    color: 'orange'
  }
]

export default function AccountPage() {
  // i18n translation hook
  const { t, language, setLanguage, isLoaded } = useTranslation()
  const supportEmail = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || 'support@kloud.com'
  
  const [activeTab, setActiveTab] = useState<'overview' | 'billing' | 'subscription' | 'security' | 'settings'>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [isCheckoutLoading, setIsCheckoutLoading] = useState(false)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileSaveMessage, setProfileSaveMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  
  // User data - fetched from API
  const [user, setUser] = useState<User | null>(null)

  // Subscription - fetched from API (null = no active subscription)
  const [subscription, setSubscription] = useState<Subscription | null>(null)

  // Stripe checkout handler
  const getAuthToken = () => {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('kloud_auth_token') || sessionStorage.getItem('kloud_auth_token')
  }

  const handleUpgrade = async (priceId: string, planName: string) => {
    setIsCheckoutLoading(true)
    try {
      const token = getAuthToken()
      const response = await fetch('/api/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          priceId,
          planName,
          successUrl: `${window.location.origin}/modules/account?success=true`,
          cancelUrl: `${window.location.origin}/modules/account?canceled=true`,
        }),
      })
      
      const result = await response.json()
      
      if (result.success && result.url) {
        // Redirect to Stripe Checkout
        window.location.href = result.url
      } else if (result.demo) {
        // Stripe not configured - show message
        alert(t('upgrade.stripeNotConfigured'))
      } else {
        console.error('Checkout error:', result.error)
        alert(t('upgrade.paymentError'))
      }
    } catch (error) {
      console.error('Checkout error:', error)
      alert(t('upgrade.connectionError'))
    } finally {
      setIsCheckoutLoading(false)
    }
  }

  // Save profile handler
  const handleSaveProfile = async () => {
    if (!user) return
    
    setIsSavingProfile(true)
    setProfileSaveMessage(null)
    
    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: user.name,
          email: user.email,
          company: user.company,
          phone: user.phone,
          language: user.language,
          timezone: user.timezone,
        }),
      })
      
      const result = await response.json()
      
      if (result.success) {
        setProfileSaveMessage({ type: 'success', text: t('settings.profileSaved') })
        setTimeout(() => setProfileSaveMessage(null), 3000)
      } else {
        setProfileSaveMessage({ type: 'error', text: t('settings.saveFailed') })
      }
    } catch (error) {
      console.error('Save profile error:', error)
      setProfileSaveMessage({ type: 'error', text: t('settings.connectionError') })
    } finally {
      setIsSavingProfile(false)
    }
  }

  // Invoices - fetched from API (empty = no invoices yet)
  const [invoices, setInvoices] = useState<Invoice[]>([])

  // Payment methods - fetched from API (empty = no payment methods)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])

  // Billing address - fetched from API
  const [billingAddress, setBillingAddress] = useState<BillingAddress | null>(null)
  const [showAddressModal, setShowAddressModal] = useState(false)
  const [isSavingAddress, setIsSavingAddress] = useState(false)

  // API Keys - managed locally (in production would be stored in database)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [copiedKeyId, setCopiedKeyId] = useState<string | null>(null)

  // Generate random API key
  const generateApiKey = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    const prefix = 'sk_live_'
    let key = prefix
    for (let i = 0; i < 32; i++) {
      key += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return key
  }

  // Handle generate new API key
  const handleGenerateApiKey = async () => {
    setIsGeneratingKey(true)
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const newKey: ApiKey = {
      id: `key_${Date.now()}`,
      key: generateApiKey(),
      name: `API Key ${apiKeys.length + 1}`,
      createdAt: new Date().toISOString(),
    }
    
    setApiKeys([...apiKeys, newKey])
    setIsGeneratingKey(false)
  }

  // Handle copy API key
  const handleCopyApiKey = async (key: ApiKey) => {
    try {
      await navigator.clipboard.writeText(key.key)
      setCopiedKeyId(key.id)
      setTimeout(() => setCopiedKeyId(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  // Handle revoke API key
  const handleRevokeApiKey = (keyId: string) => {
    if (confirm(t('security.revokeConfirm'))) {
      setApiKeys(apiKeys.filter(k => k.id !== keyId))
    }
  }

  // Preferences state
  const [preferencesMessage, setPreferencesMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  const [detectedTimezone, setDetectedTimezone] = useState<string | null>(null)

  // Detect timezone automatically on mount
  useEffect(() => {
    try {
      const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      setDetectedTimezone(browserTimezone)
      
      // Load saved preferences from localStorage
      const savedLanguage = localStorage.getItem('kloud_language')
      const savedTimezone = localStorage.getItem('kloud_timezone')
      const savedTheme = localStorage.getItem('kloud_theme')
      
      if (savedLanguage || savedTimezone) {
        // Will apply after user loads
        console.log('Loaded preferences:', { savedLanguage, savedTimezone, savedTheme })
      }
    } catch (error) {
      console.log('Could not detect timezone:', error)
    }
  }, [])

  // Handle language change with persistence
  const handleLanguageChange = (langCode: string) => {
    if (!user) return
    setUser({...user, language: langCode})
    localStorage.setItem('kloud_language', langCode)
    setPreferencesMessage({ type: 'success', text: `${t('preferences.languageChanged')} ${langCode.toUpperCase()}` })
    setTimeout(() => setPreferencesMessage(null), 2000)
  }

  // Handle timezone change with persistence
  const handleTimezoneChange = (timezone: string) => {
    if (!user) return
    setUser({...user, timezone})
    localStorage.setItem('kloud_timezone', timezone)
    setPreferencesMessage({ type: 'success', text: `${t('preferences.timezoneChanged')} ${timezone}` })
    setTimeout(() => setPreferencesMessage(null), 2000)
  }

  // Auto-detect and set timezone from browser
  const handleAutoDetectTimezone = () => {
    if (!user || !detectedTimezone) return
    setUser({...user, timezone: detectedTimezone})
    localStorage.setItem('kloud_timezone', detectedTimezone)
    setPreferencesMessage({ type: 'success', text: `${t('preferences.timezoneChanged')} ${detectedTimezone}` })
    setTimeout(() => setPreferencesMessage(null), 3000)
  }

  // Fetch user profile from API
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('/api/user/profile')
        const result = await response.json()
        if (result.success && result.data) {
          setUser(result.data)
        }
      } catch (error) {
        console.error('Failed to fetch profile:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchProfile()
  }, [])

  // Fetch billing data from Stripe APIs
  useEffect(() => {
    const fetchBillingData = async () => {
      try {
        const token = getAuthToken()
        const authHeaders: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {}

        // Fetch all billing data in parallel
        const [subscriptionRes, invoicesRes, paymentMethodsRes, addressRes] = await Promise.all([
          fetch('/api/billing/subscription', { headers: authHeaders }),
          fetch('/api/billing/invoices', { headers: authHeaders }),
          fetch('/api/billing/payment-methods', { headers: authHeaders }),
          fetch('/api/billing/billing-address', { headers: authHeaders }),
        ])

        const [subscriptionData, invoicesData, paymentMethodsData, addressData] = await Promise.all([
          subscriptionRes.json(),
          invoicesRes.json(),
          paymentMethodsRes.json(),
          addressRes.json(),
        ])

        if (subscriptionData.success && subscriptionData.subscription) {
          setSubscription(subscriptionData.subscription)
        }

        if (invoicesData.success && invoicesData.invoices) {
          setInvoices(invoicesData.invoices)
        }

        if (paymentMethodsData.success && paymentMethodsData.paymentMethods) {
          setPaymentMethods(paymentMethodsData.paymentMethods)
        }

        if (addressData.success && addressData.billingAddress) {
          setBillingAddress(addressData.billingAddress)
        }
      } catch (error) {
        console.error('Failed to fetch billing data:', error)
      }
    }

    fetchBillingData()
  }, [])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('sq-AL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-400/10'
      case 'paid': return 'text-green-400 bg-green-400/10'
      case 'trialing': return 'text-violet-400 bg-violet-400/10'
      case 'canceled': return 'text-red-400 bg-red-400/10'
      case 'past_due': return 'text-yellow-400 bg-yellow-400/10'
      case 'pending': return 'text-yellow-400 bg-yellow-400/10'
      case 'failed': return 'text-red-400 bg-red-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'from-gray-500 to-gray-600'
      case 'starter': return 'from-violet-500 to-violet-600'
      case 'professional': return 'from-purple-500 to-purple-600'
      case 'enterprise': return 'from-orange-500 to-orange-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  // Wait for i18n to load from localStorage to prevent hydration mismatch
  if (!isLoaded || isLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/modules" className="text-gray-400 hover:text-white transition-colors">
                {t('nav.back')}
              </Link>
              <div className="w-px h-6 bg-white/20"></div>
              <h1 className="text-xl font-semibold">👤 {t('account.title')}</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${getPlanColor(subscription?.plan?.toLowerCase() || user.plan)}`}>
                {subscription?.plan || (user.plan.charAt(0).toUpperCase() + user.plan.slice(1))} Plan
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Profile Card */}
        <div className="bg-white/5 rounded-2xl border border-white/10 p-6 mb-8">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-3xl font-bold">
              {user.name.charAt(0)}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{user.name}</h2>
              <p className="text-gray-400">{user.email}</p>
              {user.company && <p className="text-gray-500 text-sm mt-1">🏢 {user.company}</p>}
            </div>
            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              ✏️ {t('account.editProfile')}
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {[
            { id: 'overview', label: t('tabs.overview'), icon: '📊' },
            { id: 'subscription', label: t('tabs.subscription'), icon: '💳' },
            { id: 'billing', label: t('tabs.billing'), icon: '🧾' },
            { id: 'security', label: t('tabs.security'), icon: '🔒' },
            { id: 'settings', label: t('tabs.settings'), icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-violet-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Current Plan */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.currentPlan')}</h3>
              {subscription ? (
                <>
                  <div className={`p-4 rounded-xl bg-gradient-to-r ${getPlanColor(user.plan)} mb-4`}>
                    <div className="text-2xl font-bold">{subscription.plan}</div>
                    <div className="text-white/80">€{subscription.amount}/{subscription.interval === 'month' ? t('subscription.perMonth').replace('/', '') : t('subscription.perYear').replace('/', '')}</div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">{t('overview.status')}:</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(subscription.status)}`}>
                        {subscription.status === 'active' ? t('common.active') : subscription.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">{t('overview.expires')}:</span>
                      <span>{formatDate(subscription.currentPeriodEnd)}</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-4 rounded-xl bg-gray-700/50 mb-4 text-center">
                  <div className="text-xl font-bold text-gray-400">{t('overview.free')}</div>
                  <div className="text-sm text-gray-500">{t('overview.noSubscription')}</div>
                </div>
              )}
              <button 
                onClick={() => setShowUpgradeModal(true)}
                className="w-full mt-4 px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
              >
                🚀 {subscription ? t('overview.upgradePlan') : t('overview.choosePlan')}
              </button>
            </div>

            {/* Usage Stats */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.usage')}</h3>
              <div className="text-center py-6 text-gray-400">
                <div className="text-4xl mb-2">📊</div>
                <div>{t('overview.usageStats')}</div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('overview.quickActions')}</h3>
              <div className="space-y-3">
                <button 
                  onClick={() => setActiveTab('subscription')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">📊</span>
                  <div>
                    <div className="font-medium">{t('overview.manageSubscription')}</div>
                    <div className="text-sm text-gray-400">{t('overview.viewPlan')}</div>
                  </div>
                </button>
                <button 
                  onClick={() => setActiveTab('settings')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">⚙️</span>
                  <div>
                    <div className="font-medium">{t('overview.profileSettings')}</div>
                    <div className="text-sm text-gray-400">{t('overview.editInfo')}</div>
                  </div>
                </button>
                <button 
                  onClick={() => setActiveTab('security')}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
                >
                  <span className="text-2xl">🔒</span>
                  <div>
                    <div className="font-medium">{t('overview.securitySettings')}</div>
                    <div className="text-sm text-gray-400">{t('overview.passwordAnd2FA')}</div>
                  </div>
                </button>
                <a href={`mailto:${supportEmail}`} className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left">
                  <span className="text-2xl">📧</span>
                  <div>
                    <div className="font-medium">{t('overview.contactSupport')}</div>
                    <div className="text-sm text-gray-400">{supportEmail}</div>
                  </div>
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Subscription Tab */}
        {activeTab === 'subscription' && (
          <div className="space-y-6">
            {/* Current Subscription */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('subscription.current')}</h3>
              {subscription ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.plan')}</div>
                      <div className="text-xl font-bold">{subscription.plan}</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.price')}</div>
                      <div className="text-xl font-bold">€{subscription.amount}<span className="text-sm font-normal text-gray-400">{subscription.interval === 'month' ? t('subscription.perMonth') : t('subscription.perYear')}</span></div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.status')}</div>
                      <div className={`inline-block px-2 py-1 rounded-full text-sm ${getStatusColor(subscription.status)}`}>
                        {subscription.status === 'active' ? '✓ ' + t('common.active') : subscription.status}
                      </div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="text-gray-400 text-sm mb-1">{t('subscription.renews')}</div>
                      <div className="text-xl font-bold">{formatDate(subscription.currentPeriodEnd)}</div>
                    </div>
                  </div>
                  <div className="flex gap-3 mt-6">
                    <button 
                      onClick={() => setShowUpgradeModal(true)}
                      className="px-6 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                    >
                      🚀 {t('subscription.upgrade')}
                    </button>
                    <button className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors">
                      {t('subscription.switchToYearly')}
                    </button>
                    <button className="px-6 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg font-medium transition-colors">
                      {t('subscription.cancel')}
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400 mb-4">{t('subscription.noActive')}</div>
                  <button 
                    onClick={() => setShowUpgradeModal(true)}
                    className="px-6 py-3 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                  >
                    🚀 {t('overview.choosePlan')}
                  </button>
                </div>
              )}
            </div>

            {/* Available Plans */}
            <div>
              <h3 className="text-lg font-semibold mb-4">{t('subscription.availablePlans')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {PLANS.map(plan => (
                  <div 
                    key={plan.id}
                    className={`relative p-6 rounded-2xl border transition-all ${
                      user.plan === plan.id 
                        ? 'bg-violet-600/20 border-violet-500' 
                        : 'bg-white/5 border-white/10 hover:border-white/30'
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-600 rounded-full text-xs font-medium">
                        {t('subscription.mostPopular')}
                      </div>
                    )}
                    <div className="text-lg font-bold mb-2">{plan.name}</div>
                    <div className="text-3xl font-bold mb-4">
                      €{plan.price}
                      <span className="text-sm font-normal text-gray-400">{t('subscription.perMonth')}</span>
                    </div>
                    <ul className="space-y-2 mb-6">
                      {plan.features.slice(0, 5).map((feature, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                          <span className="text-green-400">✓</span>
                          {feature}
                        </li>
                      ))}
                      {plan.features.length > 5 && (
                        <li className="text-sm text-gray-500">+{plan.features.length - 5} {t('subscription.more')}</li>
                      )}
                    </ul>
                    {user.plan === plan.id ? (
                      <button disabled className="w-full py-2 bg-white/10 rounded-lg font-medium text-gray-400 cursor-not-allowed">
                        {t('subscription.currentPlan')}
                      </button>
                    ) : (
                      <button 
                        onClick={() => {
                          setSelectedPlan(plan.id)
                          setShowUpgradeModal(true)
                        }}
                        className="w-full py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors"
                      >
                        {PLANS.findIndex(p => p.id === plan.id) > PLANS.findIndex(p => p.id === user.plan) ? t('subscription.upgrade') : t('subscription.downgrade')}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Billing Tab */}
        {activeTab === 'billing' && (
          <div className="space-y-6">
            {/* Payment Methods */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">{t('billing.paymentMethods')}</h3>
                <button className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors">
                  {t('billing.addMethod')}
                </button>
              </div>
              <div className="space-y-3">
                {paymentMethods.length > 0 ? (
                  paymentMethods.map(method => (
                    <div key={method.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center gap-4">
                        <div className="text-3xl">
                          {method.type === 'card' ? '💳' : method.type === 'paypal' ? '🅿️' : '🏦'}
                        </div>
                        <div>
                          <div className="font-medium">
                            {method.brand} •••• {method.last4}
                          </div>
                          <div className="text-sm text-gray-400">
                            {t('billing.expires')} {method.expiryMonth}/{method.expiryYear}
                          </div>
                        </div>
                        {method.isDefault && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                            {t('billing.default')}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors">
                          {t('common.edit')}
                        </button>
                        <button className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm transition-colors">
                          {t('billing.remove')}
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <div className="text-4xl mb-2">💳</div>
                    <div>{t('billing.noMethods')}</div>
                    <div className="text-sm mt-1">{t('billing.addCardToSubscribe')}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Billing Address */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">{t('billing.billingAddress')}</h3>
                <button 
                  onClick={() => setShowAddressModal(true)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors"
                >
                  ✏️ {t('common.edit')}
                </button>
              </div>
              {billingAddress ? (
                <div className="text-gray-300 space-y-1">
                  {billingAddress.name && <p className="font-medium">{billingAddress.name}</p>}
                  <p>{billingAddress.line1}</p>
                  {billingAddress.line2 && <p>{billingAddress.line2}</p>}
                  <p>{billingAddress.city}, {billingAddress.postal_code}</p>
                  {billingAddress.state && <p>{billingAddress.state}</p>}
                  <p>{billingAddress.country}</p>
                  {billingAddress.phone && <p className="text-gray-400 mt-2">📞 {billingAddress.phone}</p>}
                </div>
              ) : (
                <div className="text-gray-400 text-center py-4">
                  <p>{t('billing.addressOnFirstPayment')}</p>
                </div>
              )}
            </div>

            {/* Invoices */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">{t('billing.invoiceHistory')}</h3>
              {invoices.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-gray-400 text-sm border-b border-white/10">
                        <th className="pb-3 font-medium">{t('billing.invoice')}</th>
                        <th className="pb-3 font-medium">{t('billing.date')}</th>
                        <th className="pb-3 font-medium">{t('billing.amount')}</th>
                        <th className="pb-3 font-medium">{t('subscription.status')}</th>
                        <th className="pb-3 font-medium">{t('billing.actions')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {invoices.map(invoice => (
                        <tr key={invoice.id} className="border-b border-white/5">
                          <td className="py-4 font-mono text-sm">{invoice.id}</td>
                          <td className="py-4">{formatDate(invoice.date)}</td>
                          <td className="py-4 font-medium">€{invoice.amount}</td>
                          <td className="py-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(invoice.status)}`}>
                              {invoice.status === 'paid' ? t('billing.paid') : invoice.status}
                            </span>
                          </td>
                          <td className="py-4">
                            {invoice.pdfUrl ? (
                              <a 
                                href={invoice.pdfUrl} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors inline-block"
                              >
                                {t('billing.downloadPDF')}
                              </a>
                            ) : (
                              <button 
                                disabled 
                                className="px-3 py-1 bg-white/5 text-gray-500 rounded-lg text-sm cursor-not-allowed"
                              >
                                {t('billing.downloadPDF')}
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <div className="text-4xl mb-2">🧾</div>
                  <div>{t('billing.noInvoices')}</div>
                  <div className="text-sm mt-1">{t('billing.invoicesAfterPayment')}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {/* Password */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">🔐 {t('security.password')}</h3>
              <p className="text-gray-400 mb-4">{t('security.twoFactorDesc')}</p>
              <button className="px-6 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-medium transition-colors">
                {t('security.changePassword')}
              </button>
            </div>

            {/* Two-Factor Auth */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-2">🛡️ {t('security.twoFactor')}</h3>
                  <p className="text-gray-400">{t('security.twoFactorDesc')}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">{t('security.disabled')}</span>
                  <button className="px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-medium transition-colors">
                    {t('security.enable')}
                  </button>
                </div>
              </div>
            </div>

            {/* Active Sessions */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">📱 {t('security.activeSessions')}</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">💻</span>
                    <div>
                      <div className="font-medium">{t('security.currentSession')}</div>
                      <div className="text-sm text-gray-400">{t('security.thisBrowser')}</div>
                    </div>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {t('common.active')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* API Keys */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">🔑 {t('security.apiKeys')}</h3>
                <button 
                  onClick={handleGenerateApiKey}
                  disabled={isGeneratingKey}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  {isGeneratingKey ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    t('security.generateKey')
                  )}
                </button>
              </div>
              {apiKeys.length > 0 ? (
                <div className="space-y-3">
                  {apiKeys.map(apiKey => (
                    <div key={apiKey.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium">{apiKey.name}</div>
                        <div className="font-mono text-sm text-gray-400 truncate">
                          {apiKey.key.substring(0, 20)}{'*'.repeat(20)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {t('security.created')}: {new Date(apiKey.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <button 
                          onClick={() => handleCopyApiKey(apiKey)}
                          className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
                        >
                          {copiedKeyId === apiKey.id ? t('security.copied') : t('security.copy')}
                        </button>
                        <button 
                          onClick={() => handleRevokeApiKey(apiKey.id)}
                          className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm transition-colors"
                        >
                          {t('security.revoke')}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-400">
                  <div className="text-4xl mb-2">🔑</div>
                  <div>{t('security.noKeys')}</div>
                  <div className="text-sm mt-1">{t('security.generateToUse')}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* Profile Settings */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">👤 {t('settings.profileInfo')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.fullName')}</label>
                  <input 
                    type="text" 
                    value={user.name}
                    onChange={(e) => setUser({...user, name: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.email')}</label>
                  <input 
                    type="email" 
                    value={user.email}
                    onChange={(e) => setUser({...user, email: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.company')}</label>
                  <input 
                    type="text" 
                    value={user.company || ''}
                    onChange={(e) => setUser({...user, company: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.phone')}</label>
                  <input 
                    type="tel" 
                    value={user.phone || ''}
                    onChange={(e) => setUser({...user, phone: e.target.value})}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>
              <div className="mt-6 flex flex-col gap-3">
                <button 
                  onClick={handleSaveProfile}
                  disabled={isSavingProfile}
                  className="w-full md:w-auto px-8 py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isSavingProfile ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      <span>{t('settings.savingChanges')}</span>
                    </>
                  ) : (
                    <span>{t('settings.saveChanges')}</span>
                  )}
                </button>
                {profileSaveMessage && (
                  <div className={`p-3 rounded-lg text-center ${
                    profileSaveMessage.type === 'success' 
                      ? 'bg-green-500/20 border border-green-500/30 text-green-400' 
                      : 'bg-red-500/20 border border-red-500/30 text-red-400'
                  }`}>
                    {profileSaveMessage.text}
                  </div>
                )}
              </div>
            </div>

            {/* Preferences */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">⚙️ {t('preferences.title')}</h3>
                {preferencesMessage && (
                  <span className={`text-sm px-3 py-1 rounded-full ${
                    preferencesMessage.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {preferencesMessage.text}
                  </span>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Language Selection */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-white">🌐 {t('preferences.language')}</label>
                  <p className="text-xs text-gray-400 -mt-2">{t('preferences.languageDesc')}</p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { code: 'sq', name: 'Shqip', flag: '🇦🇱' },
                      { code: 'en', name: 'English', flag: '🇬🇧' },
                      { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
                      { code: 'it', name: 'Italiano', flag: '🇮🇹' },
                      { code: 'fr', name: 'Français', flag: '🇫🇷' },
                      { code: 'es', name: 'Español', flag: '🇪🇸' },
                    ].map(lang => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          handleLanguageChange(lang.code)
                          setLanguage(lang.code as 'en' | 'sq' | 'de' | 'it' | 'fr' | 'es')
                        }}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-all ${
                          user.language === lang.code 
                            ? 'bg-violet-600/30 border-violet-500 text-white' 
                            : 'bg-white/5 border-white/10 text-gray-300 hover:border-white/30'
                        }`}
                      >
                        <span className="text-lg">{lang.flag}</span>
                        <span className="text-sm">{lang.name}</span>
                        {user.language === lang.code && <span className="ml-auto text-violet-400">✓</span>}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Timezone Selection */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="block text-sm font-medium text-white">🕐 {t('preferences.timezone')}</label>
                      <p className="text-xs text-gray-400">{t('preferences.timezoneDesc')}</p>
                    </div>
                    {detectedTimezone && (
                      <button
                        onClick={handleAutoDetectTimezone}
                        className="px-3 py-1 text-xs bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/50 text-purple-300 rounded-lg transition-all"
                      >
                        {t('preferences.autoDetect')}
                      </button>
                    )}
                  </div>
                  {detectedTimezone && user.timezone !== detectedTimezone && (
                    <div className="p-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-xs text-yellow-400">
                      {t('preferences.detectedZone')}: <strong>{detectedTimezone}</strong>
                    </div>
                  )}
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {[
                      { tz: 'Europe/Tirane', label: 'Tirana, Albania', offset: 'UTC+1', flag: '🇦🇱' },
                      { tz: 'Europe/Berlin', label: 'Berlin, Germany', offset: 'UTC+1', flag: '🇩🇪' },
                      { tz: 'Europe/Zurich', label: 'Zurich, Switzerland', offset: 'UTC+1', flag: '🇨🇭' },
                      { tz: 'Europe/Vienna', label: 'Vienna, Austria', offset: 'UTC+1', flag: '🇦🇹' },
                      { tz: 'Europe/Rome', label: 'Rome, Italy', offset: 'UTC+1', flag: '🇮🇹' },
                      { tz: 'Europe/Paris', label: 'Paris, France', offset: 'UTC+1', flag: '🇫🇷' },
                      { tz: 'Europe/London', label: 'London, UK', offset: 'UTC+0', flag: '🇬🇧' },
                      { tz: 'America/New_York', label: 'New York, USA', offset: 'UTC-5', flag: '🇺🇸' },
                      { tz: 'America/Los_Angeles', label: 'Los Angeles, USA', offset: 'UTC-8', flag: '🇺🇸' },
                      { tz: 'Asia/Dubai', label: 'Dubai, UAE', offset: 'UTC+4', flag: '🇦🇪' },
                      { tz: 'Asia/Tokyo', label: 'Tokyo, Japan', offset: 'UTC+9', flag: '🇯🇵' },
                      { tz: 'Australia/Sydney', label: 'Sydney, Australia', offset: 'UTC+11', flag: '🇦🇺' },
                    ].map(zone => (
                      <button
                        key={zone.tz}
                        onClick={() => handleTimezoneChange(zone.tz)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg border transition-all ${
                          user.timezone === zone.tz 
                            ? 'bg-violet-600/30 border-violet-500 text-white' 
                            : 'bg-white/5 border-white/10 text-gray-300 hover:border-white/30'
                        }`}
                      >
                        <span className="text-lg">{zone.flag}</span>
                        <span className="text-sm flex-1 text-left">{zone.label}</span>
                        <span className="text-xs text-gray-400">{zone.offset}</span>
                        {user.timezone === zone.tz && <span className="text-violet-400">✓</span>}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Theme & Display */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <h4 className="text-sm font-medium text-white mb-4">🎨 {t('preferences.theme')}</h4>
                <p className="text-xs text-gray-400 mb-3">{t('preferences.themeDesc')}</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <button className="flex items-center gap-3 px-4 py-3 bg-violet-600/30 border border-violet-500 rounded-lg">
                    <span className="text-lg">🌙</span>
                    <div className="text-left">
                      <div className="text-sm font-medium">{t('preferences.darkMode')}</div>
                      <div className="text-xs text-gray-400">{t('common.active')}</div>
                    </div>
                    <span className="ml-auto text-violet-400">✓</span>
                  </button>
                  <button className="flex items-center gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:border-white/30 transition-all opacity-50 cursor-not-allowed">
                    <span className="text-lg">☀️</span>
                    <div className="text-left">
                      <div className="text-sm font-medium text-gray-400">{t('preferences.lightMode')}</div>
                      <div className="text-xs text-gray-500">{t('common.comingSoon')}</div>
                    </div>
                  </button>
                  <button className="flex items-center gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:border-white/30 transition-all opacity-50 cursor-not-allowed">
                    <span className="text-lg">💻</span>
                    <div className="text-left">
                      <div className="text-sm font-medium text-gray-400">{t('preferences.auto')}</div>
                      <div className="text-xs text-gray-500">{t('common.comingSoon')}</div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">🔔 {t('notifications.title')}</h3>
              <div className="space-y-4">
                {[
                  { id: 'email_alerts', label: t('notifications.emailAlerts'), desc: t('notifications.emailAlertsDesc'), default: true },
                  { id: 'billing', label: t('notifications.billing'), desc: t('notifications.billingDesc'), default: true },
                  { id: 'security', label: t('notifications.security'), desc: t('notifications.securityDesc'), default: true },
                  { id: 'marketing', label: t('notifications.product'), desc: t('notifications.productDesc'), default: false },
                  { id: 'newsletter', label: t('notifications.newsletter'), desc: t('notifications.newsletterDesc'), default: false }
                ].map(item => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div>
                      <div className="font-medium">{item.label}</div>
                      <div className="text-sm text-gray-400">{item.desc}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" defaultChecked={item.default} className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-violet-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-900/20 rounded-2xl border border-red-500/30 p-6">
              <h3 className="text-lg font-semibold mb-4 text-red-400">{t('danger.title')}</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="font-medium">{t('danger.exportData')}</div>
                    <div className="text-sm text-gray-400">{t('danger.exportDataDesc')}</div>
                  </div>
                  <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors">
                    {t('danger.download')}
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="font-medium text-red-400">{t('danger.deleteAccount')}</div>
                    <div className="text-sm text-gray-400">{t('danger.deleteAccountDesc')}</div>
                  </div>
                  <button className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg font-medium transition-colors">
                    {t('danger.deleteButton')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Upgrade Modal - Professional Pricing */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl w-full max-w-4xl border border-white/10 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-8 py-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">{t('upgrade.title')}</h2>
                  <p className="text-violet-100 mt-1">{t('upgrade.subtitle')}</p>
                </div>
                <button 
                  onClick={() => setShowUpgradeModal(false)}
                  className="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
                >
                  ×
                </button>
              </div>
            </div>
            
            {/* Pricing Cards */}
            <div className="p-8">
              <div className="grid md:grid-cols-3 gap-6">
                {/* Starter */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10 hover:border-violet-500/50 transition-all">
                  <div className="text-center mb-6">
                    <span className="text-3xl">🚀</span>
                    <h3 className="text-xl font-bold mt-2">Starter</h3>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">€29</span>
                      <span className="text-gray-400">{t('subscription.perMonth')}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-6 text-sm">
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 10 Data Sources</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 50,000 Data Points</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 100,000 API Calls</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 5 GB Storage</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Email Support</li>
                  </ul>
                  <button className="w-full py-3 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors">
                    {t('subscription.currentPlan')}
                  </button>
                </div>

                {/* Professional - Recommended */}
                <div className="bg-gradient-to-b from-violet-600/20 to-purple-600/20 rounded-xl p-6 border-2 border-violet-500 relative">
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-violet-500 to-purple-500 rounded-full text-xs font-bold">
                    RECOMMENDED
                  </div>
                  <div className="text-center mb-6">
                    <span className="text-3xl">⚡</span>
                    <h3 className="text-xl font-bold mt-2">Professional</h3>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">€99</span>
                      <span className="text-gray-400">{t('subscription.perMonth')}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-6 text-sm">
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 50 Data Sources</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 500,000 Data Points</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 1,000,000 API Calls</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 50 GB Storage</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Priority Support</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Advanced Analytics</li>
                  </ul>
                  <button 
                    onClick={() => handleUpgrade('professional_monthly', 'Professional')}
                    disabled={isCheckoutLoading}
                    className="w-full py-3 bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-400 hover:to-purple-400 rounded-lg font-bold transition-all shadow-lg shadow-violet-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isCheckoutLoading ? t('upgrade.processing') : t('upgrade.upgradeNow')}
                  </button>
                </div>

                {/* Enterprise */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10 hover:border-orange-500/50 transition-all">
                  <div className="text-center mb-6">
                    <span className="text-3xl">🏢</span>
                    <h3 className="text-xl font-bold mt-2">Enterprise</h3>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">€299</span>
                      <span className="text-gray-400">{t('subscription.perMonth')}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-6 text-sm">
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Unlimited Sources</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Unlimited Data Points</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Unlimited API Calls</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 500 GB Storage</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> 24/7 Phone Support</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Dedicated Manager</li>
                    <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Custom Integrations</li>
                  </ul>
                  <a href="mailto:enterprise@kloud.com" className="block w-full py-3 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors text-center">
                    {t('upgrade.contactSales')}
                  </a>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-8 text-center">
                <p className="text-gray-400 text-sm">
                  💳 Secure payment via Stripe • 🔄 Cancel anytime • 📧 Questions? <a href={`mailto:${supportEmail}`} className="text-violet-400 hover:underline">{supportEmail}</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Billing Address Modal */}
      {showAddressModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-2xl border border-white/10 max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">{t('billing.editAddress')}</h2>
              <button 
                onClick={() => setShowAddressModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            <form 
              onSubmit={async (e) => {
                e.preventDefault()
                const form = e.target as HTMLFormElement
                const formData = new FormData(form)
                
                setIsSavingAddress(true)
                try {
                  const token = getAuthToken()
                  const response = await fetch('/api/billing/billing-address', {
                    method: 'PUT',
                    headers: {
                      'Content-Type': 'application/json',
                      ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    },
                    body: JSON.stringify({
                      name: formData.get('name'),
                      line1: formData.get('line1'),
                      line2: formData.get('line2') || undefined,
                      city: formData.get('city'),
                      state: formData.get('state') || undefined,
                      postal_code: formData.get('postal_code'),
                      country: formData.get('country'),
                      phone: formData.get('phone') || undefined,
                    }),
                  })
                  
                  const result = await response.json()
                  if (result.success) {
                    setBillingAddress({
                      name: formData.get('name') as string,
                      line1: formData.get('line1') as string,
                      line2: formData.get('line2') as string || undefined,
                      city: formData.get('city') as string,
                      state: formData.get('state') as string || undefined,
                      postal_code: formData.get('postal_code') as string,
                      country: formData.get('country') as string,
                      phone: formData.get('phone') as string || undefined,
                    })
                    setShowAddressModal(false)
                  } else {
                    alert(result.error || t('settings.saveFailed'))
                  }
                } catch (error) {
                  console.error('Error saving address:', error)
                  alert(t('settings.connectionError'))
                } finally {
                  setIsSavingAddress(false)
                }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.fullName')}</label>
                <input 
                  type="text" 
                  name="name"
                  defaultValue={billingAddress?.name || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.addressLine1')} *</label>
                <input 
                  type="text" 
                  name="line1"
                  required
                  defaultValue={billingAddress?.line1 || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder={t('billing.streetAddress')}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.addressLine2')}</label>
                <input 
                  type="text" 
                  name="line2"
                  defaultValue={billingAddress?.line2 || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder={t('billing.aptSuite')}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.city')} *</label>
                  <input 
                    type="text" 
                    name="city"
                    required
                    defaultValue={billingAddress?.city || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.postalCode')} *</label>
                  <input 
                    type="text" 
                    name="postal_code"
                    required
                    defaultValue={billingAddress?.postal_code || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.stateRegion')}</label>
                  <input 
                    type="text" 
                    name="state"
                    defaultValue={billingAddress?.state || ''}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{t('billing.country')} *</label>
                  <select 
                    name="country"
                    required
                    defaultValue={billingAddress?.country || 'AL'}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  >
                    <option value="AL">Shqipëri</option>
                    <option value="XK">Kosovë</option>
                    <option value="MK">Maqedoni e Veriut</option>
                    <option value="ME">Mali i Zi</option>
                    <option value="DE">Gjermani</option>
                    <option value="IT">Itali</option>
                    <option value="AT">Austri</option>
                    <option value="CH">Zvicër</option>
                    <option value="US">SHBA</option>
                    <option value="GB">Britani e Madhe</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">{t('billing.phone')}</label>
                <input 
                  type="tel" 
                  name="phone"
                  defaultValue={billingAddress?.phone || ''}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-violet-500"
                  placeholder="+355..."
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddressModal(false)}
                  className="flex-1 py-2 bg-white/10 hover:bg-white/20 rounded-lg font-medium transition-colors"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isSavingAddress}
                  className="flex-1 py-2 bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isSavingAddress ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      {t('common.saving')}
                    </>
                  ) : (
                    t('common.save')
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}








