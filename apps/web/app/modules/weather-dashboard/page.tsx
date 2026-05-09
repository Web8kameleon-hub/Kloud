'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { Cloud, Brain, Thermometer, Wind, Droplets, AlertTriangle, Activity, RefreshCw, Sun, Gauge, Zap } from 'lucide-react';

/**
 * BIOMETRIC ENVIRONMENT MONITOR
 * Kloud Environmental Neuroscience Module
 * 
 * Analyzes how weather conditions affect cognitive performance
 * Real Open-Meteo API + Neural Performance Correlation
 * 
 * Rate Limited: Max 1 request per 30 seconds to avoid 429 errors
 */

// Simple cache to avoid excessive API calls
const weatherCache: { data: WeatherData[] | null; timestamp: number } = { data: null, timestamp: 0 };
const CACHE_DURATION = 60000; // 1 minute cache
const MIN_REQUEST_INTERVAL = 30000; // 30 seconds between requests

interface WeatherData {
    city: string;
    country: string;
    temperature: number;
    humidity: number;
    windSpeed: number;
    pressure: number;
    weatherCode: number;
    uvIndex: number;
}

interface CognitiveImpact {
    overall: 'optimal' | 'moderate' | 'challenging';
    score: number; // 0-100
    factors: {
        temperature: { impact: string; recommendation: string };
        pressure: { impact: string; migraineRisk: number };
        humidity: { impact: string; recommendation: string };
  };
    neurofeedbackAdvice: string;
    sessionQuality: string;
}

interface APIResponse {
    weather: WeatherData[];
    cognitive: CognitiveImpact;
    alertActive: boolean;
    timestamp: string;
    responseTime: number;
}

export default function BiometricEnvironmentMonitor() {
    const [data, setData] = useState<APIResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedCity, setSelectedCity] = useState<string>('Tirana');
    const [activeTab, setActiveTab] = useState<'cities' | 'search' | 'coordinates'>('cities');
    const [rateLimited, setRateLimited] = useState(false);
    const lastRequestTime = useRef<number>(0);
    
    // Search state
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [searchResults, setSearchResults] = useState<Array<{name: string; country: string; lat: number; lon: number}>>([]);
    const [searchLoading, setSearchLoading] = useState(false);
    const [searchWeather, setSearchWeather] = useState<WeatherData | null>(null);
    
    // Coordinates state
    const [customLat, setCustomLat] = useState<string>('');
    const [customLon, setCustomLon] = useState<string>('');
    const [coordWeather, setCoordWeather] = useState<WeatherData | null>(null);
    const [coordLoading, setCoordLoading] = useState(false);

    // Albanian cities with real coordinates (default)
    const cities = [
        { name: 'Tirana', lat: 41.3275, lon: 19.8187, country: 'Albania' },
        { name: 'Durrës', lat: 41.3246, lon: 19.4565, country: 'Albania' },
        { name: 'Vlorë', lat: 40.4667, lon: 19.4897, country: 'Albania' },
        { name: 'Shkodër', lat: 42.0693, lon: 19.5033, country: 'Albania' },
        { name: 'Elbasan', lat: 41.1125, lon: 20.0822, country: 'Albania' },
        { name: 'Korçë', lat: 40.6186, lon: 20.7808, country: 'Albania' },
    ];

    // Search for any location using Open-Meteo Geocoding API (FREE, no key)
    const searchLocation = useCallback(async (query: string) => {
        if (query.length < 2) {
            setSearchResults([]);
            return;
        }
        setSearchLoading(true);
        try {
            const response = await fetch(
                `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=10&language=en&format=json`
            );
            const result = await response.json();
            if (result.results) {
                setSearchResults(result.results.map((r: { name: string; country: string; latitude: number; longitude: number; admin1?: string }) => ({
                    name: r.admin1 ? `${r.name}, ${r.admin1}` : r.name,
                    country: r.country,
                    lat: r.latitude,
                    lon: r.longitude
                })));
            } else {
                setSearchResults([]);
            }
        } catch {
            setSearchResults([]);
        } finally {
            setSearchLoading(false);
        }
    }, []);


    // Fetch weather for a specific location
    const fetchWeatherForLocation = useCallback(async (lat: number, lon: number, name: string, country: string): Promise<WeatherData> => {
        const response = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,weather_code&timezone=auto`
        );
        const result = await response.json();
        return {
            city: name,
            country: country,
            temperature: result.current?.temperature_2m ?? 0,
            humidity: result.current?.relative_humidity_2m ?? 0,
            windSpeed: result.current?.wind_speed_10m ?? 0,
            pressure: result.current?.surface_pressure ?? 1013,
            weatherCode: result.current?.weather_code ?? 0,
            uvIndex: 0
        };
    }, []);

    // Manual search handler (when no result is found)
    const handleManualSearch = useCallback(async () => {
        setSearchLoading(true);
        setError(null);
        try {
            // Try geocoding first
            const response = await fetch(
                `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(searchQuery)}&count=1&language=en&format=json`
            );
            const result = await response.json();
            if (result.results && result.results.length > 0) {
                const loc = result.results[0];
                const weather = await fetchWeatherForLocation(loc.latitude, loc.longitude, loc.name, loc.country);
                setSearchWeather(weather);
                setSearchResults([]);
                setSearchQuery(`${loc.name}, ${loc.country}`);
            } else {
                setError('Nuk u gjet asnjë vendndodhje me këtë emër.');
            }
        } catch {
            setError('Dështoi kërkimi manual.');
        } finally {
            setSearchLoading(false);
        }
    }, [searchQuery, fetchWeatherForLocation]);

    // Handle selecting a search result
    const handleSelectSearchResult = useCallback(async (location: {name: string; country: string; lat: number; lon: number}) => {
        setSearchLoading(true);
        try {
            const weather = await fetchWeatherForLocation(location.lat, location.lon, location.name, location.country);
            setSearchWeather(weather);
            setSearchResults([]);
            setSearchQuery(`${location.name}, ${location.country}`);
        } catch {
            setError('Failed to fetch weather for selected location');
        } finally {
            setSearchLoading(false);
        }
    }, [fetchWeatherForLocation]);

    // Handle coordinates search
    const handleCoordinatesSearch = useCallback(async () => {
        const lat = parseFloat(customLat);
        const lon = parseFloat(customLon);
        if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
            setError('Invalid coordinates. Lat: -90 to 90, Lon: -180 to 180');
            return;
        }
        setCoordLoading(true);
        setError(null);
        try {
            const weather = await fetchWeatherForLocation(lat, lon, `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`, 'Coordinates');
            setCoordWeather(weather);
        } catch {
            setError('Failed to fetch weather for coordinates');
        } finally {
            setCoordLoading(false);
        }
    }, [customLat, customLon, fetchWeatherForLocation]);

    const fetchData = useCallback(async (forceRefresh = false) => {
        const now = Date.now();
        
        // Rate limiting check
        if (!forceRefresh && now - lastRequestTime.current < MIN_REQUEST_INTERVAL) {
            const waitTime = Math.ceil((MIN_REQUEST_INTERVAL - (now - lastRequestTime.current)) / 1000);
            setError(`Rate limited. Please wait ${waitTime}s before refreshing.`);
            setRateLimited(true);
            setTimeout(() => setRateLimited(false), MIN_REQUEST_INTERVAL - (now - lastRequestTime.current));
            return;
        }
        
        // Use cache if valid
        if (!forceRefresh && weatherCache.data && (now - weatherCache.timestamp < CACHE_DURATION)) {
            const cachedData = weatherCache.data;
            const currentCity = cachedData.find(w => w.city === selectedCity) || cachedData[0];
            const cognitive = calculateCognitiveImpact(currentCity);
            setData({
                weather: cachedData,
                cognitive,
                alertActive: cognitive.factors.pressure.migraineRisk > 60,
                timestamp: new Date(weatherCache.timestamp).toISOString(),
                responseTime: 0
            });
            setLoading(false);
            return;
        }
        
        const startTime = performance.now();
        setLoading(true);
        lastRequestTime.current = now;

        try {
            // Fetch REAL weather data directly from Open-Meteo API (no API key needed)
            // Use sequential requests with delay to avoid 429
            const weatherData: WeatherData[] = [];
            for (const city of cities) {
                const response = await fetch(
                    `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,weather_code&timezone=Europe/Tirane`
                );
                
                if (response.status === 429) {
                    throw new Error('Too many requests. Please wait a minute before refreshing.');
                }
                
                const result = await response.json();
                weatherData.push({
                    city: city.name,
                    country: city.country,
                    temperature: result.current?.temperature_2m ?? 0,
                    humidity: result.current?.relative_humidity_2m ?? 0,
                    windSpeed: result.current?.wind_speed_10m ?? 0,
                    pressure: result.current?.surface_pressure ?? 1013,
                    weatherCode: result.current?.weather_code ?? 0,
                    uvIndex: 0
                });
                
                // Small delay between requests to avoid rate limiting
                await new Promise(resolve => setTimeout(resolve, 200));
            }
            
            // Update cache
            weatherCache.data = weatherData;
            weatherCache.timestamp = now;

            const endTime = performance.now();

            // Calculate cognitive impact based on environmental factors
            const currentCity = weatherData.find(w => w.city === selectedCity) || weatherData[0];
            const cognitive = calculateCognitiveImpact(currentCity);

            setData({
                weather: weatherData,
                cognitive,
                alertActive: cognitive.factors.pressure.migraineRisk > 60,
                timestamp: new Date().toISOString(),
                responseTime: Math.round(endTime - startTime)
            });
            setError(null);
    } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
        setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCity]);

    const calculateCognitiveImpact = (weather: WeatherData): CognitiveImpact => {
        // Temperature impact (optimal: 18-24°C)
        const tempOptimal = weather.temperature >= 18 && weather.temperature <= 24;
        const tempImpact = tempOptimal ? 'Optimal' : weather.temperature < 18 ? 'Cool - may reduce alertness' : 'Warm - may cause fatigue';
        const tempScore = tempOptimal ? 100 : Math.max(0, 100 - Math.abs(weather.temperature - 21) * 5);

      // Pressure impact (migraine risk when dropping)
      const pressureNormal = weather.pressure >= 1000 && weather.pressure <= 1025;
      const migraineRisk = weather.pressure < 1000 ? Math.min(100, (1000 - weather.pressure) * 2) :
          weather.pressure > 1025 ? Math.min(50, (weather.pressure - 1025)) : 0;
      const pressureImpact = pressureNormal ? 'Stable' : weather.pressure < 1000 ? 'Low - potential headache trigger' : 'High - generally favorable';
      const pressureScore = 100 - migraineRisk;

      // Humidity impact (optimal: 40-60%)
      const humidityOptimal = weather.humidity >= 40 && weather.humidity <= 60;
      const humidityImpact = humidityOptimal ? 'Optimal' : weather.humidity < 40 ? 'Dry - may cause discomfort' : 'Humid - may feel sluggish';
      const humidityScore = humidityOptimal ? 100 : Math.max(0, 100 - Math.abs(weather.humidity - 50));

      // Overall score
      const overallScore = Math.round((tempScore + pressureScore + humidityScore) / 3);
      const overall: 'optimal' | 'moderate' | 'challenging' =
          overallScore >= 70 ? 'optimal' : overallScore >= 40 ? 'moderate' : 'challenging';

      // Neurofeedback session quality prediction
      const sessionQuality = overallScore >= 70 ? 'Excellent - ideal conditions for training' :
          overallScore >= 50 ? 'Good - minor environmental factors' :
              'Consider rescheduling - suboptimal conditions';

      const neurofeedbackAdvice = overall === 'optimal'
          ? '✅ Excellent conditions for neurofeedback sessions. Proceed with normal protocols.'
          : overall === 'moderate'
              ? '⚡ Moderate conditions. Consider shorter sessions or relaxation-focused training.'
              : '⚠️ Challenging conditions. Focus on stress-reduction protocols if proceeding.';

      return {
          overall,
          score: overallScore,
          factors: {
              temperature: {
                  impact: tempImpact,
                  recommendation: tempOptimal ? 'Maintain current conditions' : 'Adjust room temperature if possible'
              },
              pressure: {
                  impact: pressureImpact,
                  migraineRisk
              },
              humidity: {
                  impact: humidityImpact,
                  recommendation: humidityOptimal ? 'Good air quality' : 'Consider using humidifier/dehumidifier'
              }
          },
          neurofeedbackAdvice,
          sessionQuality
      };
  };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 300000); // Update every 5 minutes
        return () => clearInterval(interval);
    }, [fetchData]);

    const getWeatherIcon = (code: number) => {
        if (code === 0 || code === 1) return <Sun className="w-8 h-8 text-yellow-400" />;
        if (code >= 2 && code <= 3) return <Cloud className="w-8 h-8 text-gray-400" />;
        return <Cloud className="w-8 h-8 text-violet-400" />;
    };

    const getImpactColor = (impact: string) => {
        if (impact === 'optimal') return 'text-green-400 bg-green-500/20';
        if (impact === 'moderate') return 'text-yellow-400 bg-yellow-500/20';
        return 'text-red-400 bg-red-500/20';
    };

    const currentWeather = data?.weather.find(w => w.city === selectedCity) || data?.weather[0];

  return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
              <Link href="/modules" className="text-violet-400 hover:text-violet-300 mb-4 inline-flex items-center gap-2">
                  ← Back to Modules
              </Link>

              <div className="flex items-center justify-between mb-8">
                  <div>
                      <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                          <Cloud className="w-8 h-8 text-violet-400" />
                          Biometric Environment Monitor
                      </h1>
                      <p className="text-gray-400 mt-1">
                          Environmental Neuroscience • Weather Impact on Cognitive Performance
                      </p>
                  </div>

                  <button
                      onClick={() => fetchData(true)}
                      disabled={loading || rateLimited}
                      className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                      <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                      {rateLimited ? 'Wait...' : 'Refresh'}
                  </button>
              </div>

              {error && (
                  <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mb-6">
                      <div className="flex items-center gap-2 text-red-400">
                          <AlertTriangle className="w-5 h-5" />
                          <span>{error}</span>
                      </div>
                  </div>
              )}

              {/* Migraine Alert */}
              {data?.alertActive && (
                  <div className="bg-orange-500/20 border border-orange-500/50 rounded-xl p-4 mb-6 animate-pulse">
                      <div className="flex items-center gap-3">
                          <AlertTriangle className="w-6 h-6 text-orange-400" />
                          <div>
                              <p className="text-orange-400 font-semibold">Barometric Pressure Alert</p>
                              <p className="text-orange-300 text-sm">
                                  Low pressure detected ({currentWeather?.pressure.toFixed(0)} hPa).
                                  Migraine risk elevated. Consider preventive measures.
                              </p>
                          </div>
                      </div>
                  </div>
              )}

              {/* TABS - Cities / Search / Coordinates */}
              <div className="flex gap-2 mb-6">
                  <button
                      onClick={() => setActiveTab('cities')}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          activeTab === 'cities' 
                              ? 'bg-violet-600 text-white' 
                              : 'bg-white/10 text-gray-400 hover:bg-white/20'
                      }`}
                  >
                      🏙️ Qytete
                  </button>
                  <button
                      onClick={() => setActiveTab('search')}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          activeTab === 'search' 
                              ? 'bg-violet-600 text-white' 
                              : 'bg-white/10 text-gray-400 hover:bg-white/20'
                      }`}
                  >
                      🔍 Kërko Lokacion
                  </button>
                  <button
                      onClick={() => setActiveTab('coordinates')}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          activeTab === 'coordinates' 
                              ? 'bg-violet-600 text-white' 
                              : 'bg-white/10 text-gray-400 hover:bg-white/20'
                      }`}
                  >
                      📍 Koordinata
                  </button>
              </div>

              {/* SEARCH TAB */}
              {activeTab === 'search' && (
                  <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6 mb-6">
                      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                          🔍 Kërko Çdo Vendndodhje
                      </h2>
                      <p className="text-gray-400 text-sm mb-4">
                          Shkruaj emrin e aeroportit, qytetit, ose vendndodhjes për të marrë motin real
                      </p>
                      <div className="relative">
                          <input
                              type="text"
                              value={searchQuery}
                              onChange={(e) => {
                                  setSearchQuery(e.target.value);
                                  searchLocation(e.target.value);
                              }}
                              placeholder="p.sh. Heathrow, New York, Tokyo Airport..."
                              className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
                          />
                          {searchLoading && (
                              <div className="absolute right-3 top-3">
                                  <RefreshCw className="w-5 h-5 text-violet-400 animate-spin" />
                              </div>
                          )}
                      </div>
                      
                      {/* Search Results Dropdown */}

                      {(searchResults.length > 0 || (searchQuery.length > 2 && !searchLoading)) && (
                          <div className="mt-2 bg-slate-800 border border-slate-600 rounded-lg max-h-60 overflow-y-auto">
                              {searchResults.map((result, idx) => (
                                  <button
                                      key={idx}
                                      onClick={() => handleSelectSearchResult(result)}
                                      className="w-full px-4 py-3 text-left hover:bg-slate-700 transition-colors border-b border-slate-700 last:border-b-0"
                                  >
                                      <span className="text-white font-medium">{result.name}</span>
                                      <span className="text-gray-400 ml-2">{result.country}</span>
                                      <span className="text-gray-500 text-xs ml-2">
                                          ({result.lat.toFixed(2)}°, {result.lon.toFixed(2)}°)
                                      </span>
                                  </button>
                              ))}
                              {/* Manual search option if no results */}
                              {searchResults.length === 0 && searchQuery.length > 2 && !searchLoading && (
                                  <button
                                      onClick={handleManualSearch}
                                      className="w-full px-4 py-3 text-left hover:bg-violet-700 transition-colors border-t border-slate-700 text-violet-300 font-semibold"
                                  >
                                      ➕ Shto manualisht: <span className="font-bold">{searchQuery}</span>
                                  </button>
                              )}
                          </div>
                      )}

                      {/* Search Weather Result */}
                      {searchWeather && (
                          <div className="mt-6 bg-gradient-to-br from-violet-600/20 to-purple-600/20 rounded-xl p-6">
                              <div className="flex items-center justify-between mb-4">
                                  <div>
                                      <h3 className="text-2xl font-bold text-white">{searchWeather.city}</h3>
                                      <p className="text-gray-400">{searchWeather.country}</p>
                                  </div>
                                  <div className="text-right">
                                      {getWeatherIcon(searchWeather.weatherCode)}
                                      <p className="text-4xl font-bold text-white mt-2">
                                          {searchWeather.temperature.toFixed(1)}°C
                                      </p>
                                  </div>
                              </div>
                              <div className="grid grid-cols-3 gap-4">
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Droplets className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{searchWeather.humidity}%</p>
                                      <p className="text-gray-500 text-xs">Lagështi</p>
                                  </div>
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Wind className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{searchWeather.windSpeed.toFixed(1)} km/h</p>
                                      <p className="text-gray-500 text-xs">Erë</p>
                                  </div>
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Gauge className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{searchWeather.pressure.toFixed(0)} hPa</p>
                                      <p className="text-gray-500 text-xs">Presion</p>
                                  </div>
                              </div>
                          </div>
                      )}
                  </div>
              )}

              {/* COORDINATES TAB */}
              {activeTab === 'coordinates' && (
                  <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6 mb-6">
                      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                          📍 Kërko me Koordinata
                      </h2>
                      <p className="text-gray-400 text-sm mb-4">
                          Fut koordinatat GPS për të marrë motin e saktë
                      </p>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                              <label className="text-gray-400 text-sm block mb-1">Latitude (Gj-V)</label>
                              <input
                                  type="text"
                                  value={customLat}
                                  onChange={(e) => setCustomLat(e.target.value)}
                                  placeholder="p.sh. 41.3275"
                                  className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
                              />
                          </div>
                          <div>
                              <label className="text-gray-400 text-sm block mb-1">Longitude (L-P)</label>
                              <input
                                  type="text"
                                  value={customLon}
                                  onChange={(e) => setCustomLon(e.target.value)}
                                  placeholder="p.sh. 19.8187"
                                  className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
                              />
                          </div>
                      </div>
                      <button
                          onClick={handleCoordinatesSearch}
                          disabled={coordLoading || !customLat || !customLon}
                          className="w-full px-4 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2"
                      >
                          {coordLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : '🔍'}
                          Kërko Motin
                      </button>

                      {/* Coordinates Weather Result */}
                      {coordWeather && (
                          <div className="mt-6 bg-gradient-to-br from-green-600/20 to-violet-600/20 rounded-xl p-6">
                              <div className="flex items-center justify-between mb-4">
                                  <div>
                                      <h3 className="text-2xl font-bold text-white">{coordWeather.city}</h3>
                                      <p className="text-gray-400">{coordWeather.country}</p>
                                  </div>
                                  <div className="text-right">
                                      {getWeatherIcon(coordWeather.weatherCode)}
                                      <p className="text-4xl font-bold text-white mt-2">
                                          {coordWeather.temperature.toFixed(1)}°C
                                      </p>
                                  </div>
                              </div>
                              <div className="grid grid-cols-3 gap-4">
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Droplets className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{coordWeather.humidity}%</p>
                                      <p className="text-gray-500 text-xs">Lagështi</p>
                                  </div>
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Wind className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{coordWeather.windSpeed.toFixed(1)} km/h</p>
                                      <p className="text-gray-500 text-xs">Erë</p>
                                  </div>
                                  <div className="text-center bg-white/5 rounded-lg p-3">
                                      <Gauge className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                                      <p className="text-white font-medium">{coordWeather.pressure.toFixed(0)} hPa</p>
                                      <p className="text-gray-500 text-xs">Presion</p>
                                  </div>
                              </div>
                          </div>
                      )}

                      {/* Quick Examples */}
                      <div className="mt-4 text-gray-500 text-xs">
                          <p className="mb-1">Shembuj koordinatash:</p>
                          <div className="flex flex-wrap gap-2">
                              <button onClick={() => { setCustomLat('41.4147'); setCustomLon('19.7206'); }} className="px-2 py-1 bg-slate-800 rounded hover:bg-slate-700">
                                  ✈️ Rinas Airport
                              </button>
                              <button onClick={() => { setCustomLat('48.8566'); setCustomLon('2.3522'); }} className="px-2 py-1 bg-slate-800 rounded hover:bg-slate-700">
                                  🗼 Paris
                              </button>
                              <button onClick={() => { setCustomLat('40.7128'); setCustomLon('-74.0060'); }} className="px-2 py-1 bg-slate-800 rounded hover:bg-slate-700">
                                  🗽 New York
                              </button>
                              <button onClick={() => { setCustomLat('35.6762'); setCustomLon('139.6503'); }} className="px-2 py-1 bg-slate-800 rounded hover:bg-slate-700">
                                  🗾 Tokyo
                              </button>
                          </div>
                      </div>
                  </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Cognitive Impact Panel */}
                  <div className="lg:col-span-1">
                      <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                              <Brain className="w-5 h-5 text-purple-400" />
                              Cognitive Impact Analysis
                          </h2>

                          {data?.cognitive ? (
                              <div className="space-y-4">
                                  {/* Overall Score */}
                                  <div className={`rounded-xl p-6 text-center ${getImpactColor(data.cognitive.overall)}`}>
                                      <p className="text-4xl font-bold">{data.cognitive.score}</p>
                                      <p className="text-sm opacity-80 capitalize">{data.cognitive.overall} Conditions</p>
                                  </div>

                                  {/* Factor Breakdown */}
                                  <div className="space-y-3">
                                      {/* Temperature */}
                                      <div className="bg-white/5 rounded-lg p-3">
                                          <div className="flex items-center justify-between mb-1">
                                              <span className="text-gray-400 flex items-center gap-2">
                                                  <Thermometer className="w-4 h-4" />
                                                  Temperature
                                              </span>
                                              <span className="text-white">{currentWeather?.temperature.toFixed(1)}°C</span>
                                          </div>
                                          <p className="text-xs text-gray-500">{data.cognitive.factors.temperature.impact}</p>
                                      </div>

                                      {/* Pressure */}
                                      <div className="bg-white/5 rounded-lg p-3">
                                          <div className="flex items-center justify-between mb-1">
                                              <span className="text-gray-400 flex items-center gap-2">
                                                  <Gauge className="w-4 h-4" />
                                                  Pressure
                                              </span>
                                              <span className="text-white">{currentWeather?.pressure.toFixed(0)} hPa</span>
                                          </div>
                                          <p className="text-xs text-gray-500">{data.cognitive.factors.pressure.impact}</p>
                                          <div className="mt-2">
                                              <div className="flex justify-between text-xs mb-1">
                                                  <span className="text-gray-500">Migraine Risk</span>
                                                  <span className={data.cognitive.factors.pressure.migraineRisk > 50 ? 'text-red-400' : 'text-green-400'}>
                                                      {data.cognitive.factors.pressure.migraineRisk}%
                                                  </span>
                                              </div>
                                              <div className="w-full bg-gray-700 rounded-full h-1.5">
                                                  <div
                                                      className={`h-1.5 rounded-full ${data.cognitive.factors.pressure.migraineRisk > 50 ? 'bg-red-500' : 'bg-green-500'
                                                          }`}
                                                      style={{ width: `${data.cognitive.factors.pressure.migraineRisk}%` }}
                                                  />
                                              </div>
                                          </div>
                                      </div>

                                      {/* Humidity */}
                                      <div className="bg-white/5 rounded-lg p-3">
                                          <div className="flex items-center justify-between mb-1">
                                              <span className="text-gray-400 flex items-center gap-2">
                                                  <Droplets className="w-4 h-4" />
                                                  Humidity
                                              </span>
                                              <span className="text-white">{currentWeather?.humidity}%</span>
                                          </div>
                                          <p className="text-xs text-gray-500">{data.cognitive.factors.humidity.impact}</p>
                                      </div>
                                  </div>

                                  {/* Session Advice */}
                                  <div className="bg-purple-500/20 rounded-lg p-4 mt-4">
                                      <div className="flex items-center gap-2 mb-2">
                                          <Zap className="w-4 h-4 text-purple-400" />
                                          <span className="text-purple-300 text-sm font-medium">Neurofeedback Advice</span>
                                      </div>
                                      <p className="text-purple-200 text-sm">
                                          {data.cognitive.neurofeedbackAdvice}
                                      </p>
                                  </div>

                                  <div className="text-center pt-2">
                                      <span className="text-xs text-gray-500">
                                          Session Quality: <span className="text-white">{data.cognitive.sessionQuality}</span>
                                      </span>
                  </div>
                </div>
                          ) : (
                              <div className="animate-pulse space-y-4">
                                  <div className="h-32 bg-gray-700/50 rounded-xl" />
                                  <div className="h-20 bg-gray-700/50 rounded" />
                                  <div className="h-20 bg-gray-700/50 rounded" />
                              </div>
                          )}
            </div>
          </div>

                  {/* Weather Data Panel */}
                  <div className="lg:col-span-2">
                      <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                          <div className="flex items-center justify-between mb-4">
                              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                  <Activity className="w-5 h-5 text-violet-400" />
                                  Environmental Data
                              </h2>
                              {data && (
                                  <span className="text-xs text-gray-500 font-mono">
                                      {data.responseTime}ms • {new Date(data.timestamp).toLocaleTimeString()}
                                  </span>
                              )}
                          </div>

                          {/* City Selector */}
                          {data?.weather && (
                              <div className="flex gap-2 mb-6 flex-wrap">
                                  {data.weather.map((city) => (
                                      <button
                                          key={city.city}
                                          onClick={() => setSelectedCity(city.city)}
                          className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${selectedCity === city.city
                                  ? 'bg-violet-600 text-white'
                                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
                              }`}
                      >
                          {city.city}
                      </button>
                  ))}
                </div>
                          )}

                          {/* Current Weather Display */}
                          {currentWeather && (
                              <div className="bg-gradient-to-br from-violet-600/20 to-purple-600/20 rounded-xl p-6 mb-6">
                                  <div className="flex items-center justify-between">
                                      <div>
                                          <h3 className="text-2xl font-bold text-white">{currentWeather.city}</h3>
                                          <p className="text-gray-400">{currentWeather.country}</p>
                                      </div>
                                      <div className="text-right">
                                          {getWeatherIcon(currentWeather.weatherCode)}
                                          <p className="text-4xl font-bold text-white mt-2">
                                              {currentWeather.temperature.toFixed(1)}°C
                                          </p>
                                      </div>
                  </div>

                                  <div className="grid grid-cols-3 gap-4 mt-6">
                                      <div className="text-center">
                                          <Droplets className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                          <p className="text-white font-medium">{currentWeather.humidity}%</p>
                                          <p className="text-gray-500 text-xs">Humidity</p>
                                      </div>
                                      <div className="text-center">
                                          <Wind className="w-5 h-5 text-violet-400 mx-auto mb-1" />
                                          <p className="text-white font-medium">{currentWeather.windSpeed.toFixed(1)} km/h</p>
                                          <p className="text-gray-500 text-xs">Wind</p>
                                      </div>
                                      <div className="text-center">
                                          <Gauge className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                                          <p className="text-white font-medium">{currentWeather.pressure.toFixed(0)} hPa</p>
                                          <p className="text-gray-500 text-xs">Pressure</p>
                                      </div>
                                  </div>
                              </div>
                          )}

                          {/* All Cities Grid */}
                          {data?.weather && (
                              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                  {data.weather.filter(w => w.city !== selectedCity).map((city) => (
                                      <button
                                          key={city.city}
                                          onClick={() => setSelectedCity(city.city)}
                                          className="bg-white/5 rounded-lg p-4 text-left hover:bg-white/10 transition-colors"
                                      >
                                          <div className="flex items-center justify-between mb-2">
                                              <span className="text-white font-medium">{city.city}</span>
                                              {getWeatherIcon(city.weatherCode)}
                                          </div>
                                          <p className="text-2xl font-bold text-white">{city.temperature.toFixed(1)}°C</p>
                                          <p className="text-gray-500 text-xs mt-1">
                                              {city.humidity}% humidity • {city.pressure.toFixed(0)} hPa
                                          </p>
                                      </button>
                                  ))}
                              </div>
                          )}

                          {/* Data Source */}
                          <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-gray-500">
                              <div className="flex items-center gap-4">
                                  <span className="flex items-center gap-1">
                                      <Cloud className="w-3 h-3" />
                                      Open-Meteo API
                                  </span>
                                  <span className="flex items-center gap-1">
                                      <Brain className="w-3 h-3" />
                                      Cognitive Correlation Engine
                                  </span>
                              </div>
                              <span>Real-time data • No simulations</span>
                          </div>
                      </div>
                  </div>
              </div>

              {/* Footer */}
              <div className="mt-8 text-center text-xs text-gray-600">
                  Biometric Environment Monitor • Kloud Environmental Neuroscience • Real API Data
        </div>
      </div>
    </div>
  );
}








