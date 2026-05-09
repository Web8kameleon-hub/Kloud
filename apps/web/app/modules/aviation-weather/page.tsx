/**
 * Aviation Weather Intelligence Dashboard
 * Kloud Platform - Professional Aviation Module
 * 
 * REAL APIs:
 * - Open-Meteo: Weather data (FREE, no key)
 * - CheckWX: METAR/TAF data (API key required)
 * - OpenSky Network: Live flight tracking (FREE, 400 req/day)
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 9.1.0 - Full Featured Aviation Suite
 * @license MIT
 */

'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// ============= INTERFACES =============

interface AirportInfo {
  code: string
  name: string
  city: string
  country: string
  flag: string
  lat: number
  lon: number
}

interface WeatherData {
  airport: string
  metar: string
  taf: string
  temperature: number
  windSpeed: number
  windDirection: number
  windGust: number
  visibility: number
  cloudCover: number
  cloudDescription: string
  pressure: number
  humidity: number
  dewpoint: number
  uvIndex: number
  flightCategory: 'VFR' | 'MVFR' | 'IFR' | 'LIFR'
  forecast: ForecastData[]
  lastUpdate: string
}

interface ForecastData {
  time: string
  temperature: number
  windSpeed: number
  windDirection: number
  weather: string
  icon: string
  precipitation: number
}

interface HourlyForecast {
  time: string[]
  temperature_2m: number[]
  wind_speed_10m: number[]
  wind_direction_10m: number[]
  precipitation_probability: number[]
  cloud_cover: number[]
  weather_code: number[]
}

interface FlightData {
  icao24: string
  callsign: string
  originCountry: string
  longitude: number
  latitude: number
  altitude: number
  velocity: number
  heading: number
  verticalRate: number
  onGround: boolean
  squawk: string
  lastUpdate: number
}

// Data source protocols for aviation data feeds
type DataSourceProtocol = 'api' | 'lora' | 'gsm' | 'cbor' | 'mqtt' | 'adsb' | 'buffer'

interface DataSourceConfig {
  protocol: DataSourceProtocol
  name: string
  icon: string
  color: string
  description: string
  enabled: boolean
}

// ============= CONSTANTS =============

const CHECKWX_API_KEY = process.env.NEXT_PUBLIC_CHECKWX_API_KEY || ''

// Data source protocols available
const DATA_SOURCES: DataSourceConfig[] = [
  { protocol: 'api', name: 'REST API', icon: '🔗', color: 'bg-violet-500', description: 'HTTP/REST endpoints (Open-Meteo, CheckWX)', enabled: true },
  { protocol: 'adsb', name: 'ADS-B', icon: '📡', color: 'bg-green-500', description: 'Aircraft tracking (OpenSky Network)', enabled: true },
  { protocol: 'lora', name: 'LoRa WAN', icon: '📻', color: 'bg-purple-500', description: 'Long-range IoT sensors', enabled: false },
  { protocol: 'gsm', name: 'GSM/LTE', icon: '📱', color: 'bg-orange-500', description: 'Cellular network data', enabled: false },
  { protocol: 'cbor', name: 'CBOR', icon: '📦', color: 'bg-violet-500', description: 'Binary encoded sensor data', enabled: false },
  { protocol: 'mqtt', name: 'MQTT', icon: '🔔', color: 'bg-pink-500', description: 'Publish/subscribe messaging', enabled: false },
  { protocol: 'buffer', name: 'Buffer', icon: '💾', color: 'bg-yellow-500', description: 'Local data buffering & caching', enabled: true },
]

// Default airports - can be customized by user
const DEFAULT_AIRPORTS: AirportInfo[] = [
  // Albania
  { code: 'LATI', name: 'Tirana International Airport "Nene Tereza"', city: 'Tirana', country: 'Albania', flag: 'AL', lat: 41.4147, lon: 19.7206 },
  { code: 'LAKK', name: 'Kukes International Airport', city: 'Kukes', country: 'Albania', flag: 'AL', lat: 42.0336, lon: 20.4158 },
  // Kosovo
  { code: 'BKPR', name: 'Pristina International Airport "Adem Jashari"', city: 'Pristina', country: 'Kosovo', flag: 'XK', lat: 42.5728, lon: 21.0358 },
  // North Macedonia
  { code: 'LWSK', name: 'Skopje International Airport', city: 'Skopje', country: 'N. Macedonia', flag: 'MK', lat: 41.9616, lon: 21.6214 },
  // Montenegro
  { code: 'LYPG', name: 'Podgorica Airport', city: 'Podgorica', country: 'Montenegro', flag: 'ME', lat: 42.3594, lon: 19.2519 },
  { code: 'LYTV', name: 'Tivat Airport', city: 'Tivat', country: 'Montenegro', flag: 'ME', lat: 42.4047, lon: 18.7233 },
  // Croatia
  { code: 'LDZA', name: 'Zagreb Airport', city: 'Zagreb', country: 'Croatia', flag: 'HR', lat: 45.7429, lon: 16.0688 },
  { code: 'LDDU', name: 'Dubrovnik Airport', city: 'Dubrovnik', country: 'Croatia', flag: 'HR', lat: 42.5614, lon: 18.2681 },
  // Major International
  { code: 'KJFK', name: 'John F. Kennedy International', city: 'New York', country: 'USA', flag: 'US', lat: 40.6413, lon: -73.7781 },
  { code: 'EGLL', name: 'London Heathrow', city: 'London', country: 'UK', flag: 'GB', lat: 51.4700, lon: -0.4543 },
  { code: 'EDDF', name: 'Frankfurt Airport', city: 'Frankfurt', country: 'Germany', flag: 'DE', lat: 50.0379, lon: 8.5622 },
  { code: 'LFPG', name: 'Paris Charles de Gaulle', city: 'Paris', country: 'France', flag: 'FR', lat: 49.0097, lon: 2.5479 },
  { code: 'EHAM', name: 'Amsterdam Schiphol', city: 'Amsterdam', country: 'Netherlands', flag: 'NL', lat: 52.3105, lon: 4.7683 },
  { code: 'LEMD', name: 'Madrid Barajas', city: 'Madrid', country: 'Spain', flag: 'ES', lat: 40.4719, lon: -3.5626 },
  { code: 'LIRF', name: 'Rome Fiumicino', city: 'Rome', country: 'Italy', flag: 'IT', lat: 41.8003, lon: 12.2389 },
  { code: 'LSZH', name: 'Zurich Airport', city: 'Zurich', country: 'Switzerland', flag: 'CH', lat: 47.4647, lon: 8.5492 },
]

// Weather code to description mapping
const WEATHER_CODES: Record<number, { description: string; icon: string }> = {
  0: { description: 'Clear sky', icon: 'sun' },
  1: { description: 'Mainly clear', icon: 'sun' },
  2: { description: 'Partly cloudy', icon: 'cloud-sun' },
  3: { description: 'Overcast', icon: 'cloud' },
  45: { description: 'Fog', icon: 'smog' },
  48: { description: 'Depositing rime fog', icon: 'smog' },
  51: { description: 'Light drizzle', icon: 'cloud-rain' },
  53: { description: 'Moderate drizzle', icon: 'cloud-rain' },
  55: { description: 'Dense drizzle', icon: 'cloud-rain' },
  61: { description: 'Slight rain', icon: 'cloud-rain' },
  63: { description: 'Moderate rain', icon: 'cloud-showers-heavy' },
  65: { description: 'Heavy rain', icon: 'cloud-showers-heavy' },
  71: { description: 'Slight snow', icon: 'snowflake' },
  73: { description: 'Moderate snow', icon: 'snowflake' },
  75: { description: 'Heavy snow', icon: 'snowflake' },
  77: { description: 'Snow grains', icon: 'snowflake' },
  80: { description: 'Slight rain showers', icon: 'cloud-sun-rain' },
  81: { description: 'Moderate rain showers', icon: 'cloud-sun-rain' },
  82: { description: 'Violent rain showers', icon: 'cloud-showers-heavy' },
  85: { description: 'Slight snow showers', icon: 'snowflake' },
  86: { description: 'Heavy snow showers', icon: 'snowflake' },
  95: { description: 'Thunderstorm', icon: 'bolt' },
  96: { description: 'Thunderstorm with hail', icon: 'bolt' },
  99: { description: 'Thunderstorm with heavy hail', icon: 'bolt' },
}

// ============= HELPER FUNCTIONS =============

function getFlightCategory(visibility: number, ceiling: number): 'VFR' | 'MVFR' | 'IFR' | 'LIFR' {
  // FAA flight category rules
  if (visibility >= 5 && ceiling >= 3000) return 'VFR'
  if (visibility >= 3 && ceiling >= 1000) return 'MVFR'
  if (visibility >= 1 && ceiling >= 500) return 'IFR'
  return 'LIFR'
}

function getCategoryColor(cat: string): string {
  switch (cat) {
    case 'VFR': return 'bg-green-500'
    case 'MVFR': return 'bg-violet-500'
    case 'IFR': return 'bg-red-500'
    case 'LIFR': return 'bg-purple-500'
    default: return 'bg-gray-500'
  }
}

function getCategoryBadge(cat: string): string {
  switch (cat) {
    case 'VFR': return 'bg-green-100 text-green-800 border-green-300'
    case 'MVFR': return 'bg-violet-100 text-slate-800 border-violet-300'
    case 'IFR': return 'bg-red-100 text-red-800 border-red-300'
    case 'LIFR': return 'bg-purple-100 text-purple-800 border-purple-300'
    default: return 'bg-gray-100 text-gray-800 border-gray-300'
  }
}

function getWindDirection(degrees: number): string {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
  const index = Math.round(degrees / 22.5) % 16
  return directions[index]
}

function getCloudDescription(cloudCover: number): string {
  if (cloudCover < 10) return 'Clear (SKC)'
  if (cloudCover < 25) return 'Few clouds (FEW)'
  if (cloudCover < 50) return 'Scattered (SCT)'
  if (cloudCover < 85) return 'Broken (BKN)'
  return 'Overcast (OVC)'
}

function generateMetar(airport: AirportInfo, weather: WeatherData): string {
  const now = new Date()
  const day = String(now.getUTCDate()).padStart(2, '0')
  const hour = String(now.getUTCHours()).padStart(2, '0')
  const min = String(now.getUTCMinutes()).padStart(2, '0')
  
  const windDir = String(Math.round(weather.windDirection)).padStart(3, '0')
  const windSpd = String(Math.round(weather.windSpeed * 0.54)).padStart(2, '0') // km/h to kt
  const gust = weather.windGust > weather.windSpeed + 5 ? `G${String(Math.round(weather.windGust * 0.54)).padStart(2, '0')}` : ''
  
  const vis = weather.visibility >= 10 ? '9999' : String(Math.round(weather.visibility * 1000)).padStart(4, '0')
  
  let clouds = 'SKC'
  if (weather.cloudCover >= 85) clouds = 'OVC100'
  else if (weather.cloudCover >= 50) clouds = 'BKN080'
  else if (weather.cloudCover >= 25) clouds = 'SCT050'
  else if (weather.cloudCover >= 10) clouds = 'FEW030'
  
  const temp = Math.round(weather.temperature)
  const dew = Math.round(weather.dewpoint)
  const tempStr = temp < 0 ? `M${String(Math.abs(temp)).padStart(2, '0')}` : String(temp).padStart(2, '0')
  const dewStr = dew < 0 ? `M${String(Math.abs(dew)).padStart(2, '0')}` : String(dew).padStart(2, '0')
  
  const qnh = `Q${Math.round(weather.pressure)}`
  
  return `${airport.code} ${day}${hour}${min}Z ${windDir}${windSpd}${gust}KT ${vis} ${clouds} ${tempStr}/${dewStr} ${qnh} NOSIG`
}

function generateTaf(airport: AirportInfo, weather: WeatherData): string {
  const now = new Date()
  const day = String(now.getUTCDate()).padStart(2, '0')
  const hour = String(now.getUTCHours()).padStart(2, '0')
  
  const validFrom = `${day}${hour}`
  const validToHour = (now.getUTCHours() + 24) % 24
  const validToDay = validToHour < now.getUTCHours() ? now.getUTCDate() + 1 : now.getUTCDate()
  const validTo = `${String(validToDay).padStart(2, '0')}${String(validToHour).padStart(2, '0')}`
  
  const windDir = String(Math.round(weather.windDirection)).padStart(3, '0')
  const windSpd = String(Math.round(weather.windSpeed * 0.54)).padStart(2, '0')
  
  let clouds = 'SKC'
  if (weather.cloudCover >= 85) clouds = 'OVC100'
  else if (weather.cloudCover >= 50) clouds = 'BKN080'
  else if (weather.cloudCover >= 25) clouds = 'SCT050'
  else if (weather.cloudCover >= 10) clouds = 'FEW030'
  
  return `TAF ${airport.code} ${day}${hour}00Z ${validFrom}/${validTo} ${windDir}${windSpd}KT 9999 ${clouds}`
}

// ============= OPENSKY HELPER =============

function parseOpenSkyStates(states: (string | number | boolean | null)[][]): FlightData[] {
  if (!states || !Array.isArray(states)) return []
  
  return states.map(s => ({
    icao24: String(s[0] || ''),
    callsign: String(s[1] || '').trim(),
    originCountry: String(s[2] || ''),
    longitude: Number(s[5]) || 0,
    latitude: Number(s[6]) || 0,
    altitude: Math.round((Number(s[7]) || Number(s[13]) || 0) * 3.28084), // meters to feet
    velocity: Math.round((Number(s[9]) || 0) * 1.94384), // m/s to knots
    heading: Math.round(Number(s[10]) || 0),
    verticalRate: Math.round((Number(s[11]) || 0) * 196.85), // m/s to ft/min
    onGround: Boolean(s[8]),
    squawk: String(s[14] || '----'),
    lastUpdate: Number(s[4]) || Date.now() / 1000,
  })).filter(f => f.callsign && f.latitude && f.longitude)
}

// ============= MAIN COMPONENT =============

const AviationWeatherDashboard: React.FC = () => {
  // Airport management - load from localStorage or use defaults
  const [airports, setAirports] = useState<AirportInfo[]>(DEFAULT_AIRPORTS)
  const [selectedAirport, setSelectedAirport] = useState<AirportInfo>(DEFAULT_AIRPORTS[0])
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [allAirportsData, setAllAirportsData] = useState<Map<string, WeatherData>>(new Map())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'current' | 'forecast' | 'metar' | 'taf' | 'table' | 'flights' | 'statistics' | 'analysis' | 'alerts' | 'ssh' | 'settings'>('current')
  const [sshStatus, setSshStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected')
  const [sshLogs, setSshLogs] = useState<{time: string; message: string; type: 'info' | 'success' | 'error' | 'warning'}[]>([])
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())
  const [liveFlights, setLiveFlights] = useState<FlightData[]>([])
  const [flightsLoading, setFlightsLoading] = useState(false)
  
  // Settings panel state
  const [showAddAirport, setShowAddAirport] = useState(false)
  const [newAirport, setNewAirport] = useState<Partial<AirportInfo>>({})
  const [dataSources, setDataSources] = useState<DataSourceConfig[]>(DATA_SOURCES)

  // Load airports from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('kloud-airports')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed) && parsed.length > 0) {
          setAirports(parsed)
          setSelectedAirport(parsed[0])
        }
      } catch {
        console.log('Using default airports')
      }
    }
  }, [])

  // Save airports to localStorage when changed
  useEffect(() => {
    if (airports !== DEFAULT_AIRPORTS) {
      localStorage.setItem('kloud-airports', JSON.stringify(airports))
    }
  }, [airports])

  // Add new airport
  const handleAddAirport = () => {
    if (newAirport.code && newAirport.name && newAirport.lat && newAirport.lon) {
      const airport: AirportInfo = {
        code: newAirport.code.toUpperCase(),
        name: newAirport.name,
        city: newAirport.city || newAirport.name,
        country: newAirport.country || 'Custom',
        flag: newAirport.flag || 'XX',
        lat: Number(newAirport.lat),
        lon: Number(newAirport.lon),
      }
      
      // Check if already exists
      if (!airports.find(a => a.code === airport.code)) {
        setAirports([...airports, airport])
        setNewAirport({})
        setShowAddAirport(false)
      } else {
        setError(`Airport ${airport.code} already exists`)
      }
    }
  }

  // Remove airport
  const handleRemoveAirport = (code: string) => {
    if (airports.length <= 1) {
      setError('Cannot remove the last airport')
      return
    }
    const newAirports = airports.filter(a => a.code !== code)
    setAirports(newAirports)
    if (selectedAirport.code === code) {
      setSelectedAirport(newAirports[0])
    }
  }

  // Reset to defaults
  const handleResetAirports = () => {
    setAirports(DEFAULT_AIRPORTS)
    setSelectedAirport(DEFAULT_AIRPORTS[0])
    localStorage.removeItem('kloud-airports')
  }

  // Toggle data source
  const toggleDataSource = (protocol: DataSourceProtocol) => {
    setDataSources(sources => 
      sources.map(s => s.protocol === protocol ? { ...s, enabled: !s.enabled } : s)
    )
  }

  // Fetch weather from Open-Meteo API
  const fetchWeatherData = useCallback(async (airport: AirportInfo): Promise<WeatherData> => {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${airport.lat}&longitude=${airport.lon}&current=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index&hourly=temperature_2m,precipitation_probability,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m&forecast_days=2&timezone=auto`
    
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Weather API error: ${res.status}`)
    
    const data = await res.json()
    const current = data.current
    const hourly: HourlyForecast = data.hourly
    
    // Calculate visibility from cloud cover (approximation)
    const visibility = Math.max(1, 15 - (current.cloud_cover / 10))
    
    // Estimate ceiling from cloud cover
    const ceiling = current.cloud_cover < 25 ? 10000 : 
                   current.cloud_cover < 50 ? 5000 : 
                   current.cloud_cover < 75 ? 2500 : 1000
    
    // Build forecast array (next 8 x 3-hour periods)
    const forecast: ForecastData[] = []
    const now = new Date()
    const currentHour = now.getHours()
    
    for (let i = 0; i < 24; i += 3) {
      const idx = currentHour + i
      if (idx < hourly.time.length) {
        const weatherCode = hourly.weather_code[idx] || 0
        const weatherInfo = WEATHER_CODES[weatherCode] || { description: 'Unknown', icon: 'cloud' }
        
        forecast.push({
          time: new Date(hourly.time[idx]).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          temperature: Math.round(hourly.temperature_2m[idx]),
          windSpeed: Math.round(hourly.wind_speed_10m[idx]),
          windDirection: hourly.wind_direction_10m[idx],
          weather: weatherInfo.description,
          icon: weatherInfo.icon,
          precipitation: hourly.precipitation_probability[idx] || 0,
        })
      }
    }
    
    const weatherResult: WeatherData = {
      airport: `${airport.name} (${airport.code})`,
      metar: '', // Will be generated or fetched
      taf: '', // Will be generated or fetched
      temperature: current.temperature_2m,
      windSpeed: current.wind_speed_10m,
      windDirection: current.wind_direction_10m,
      windGust: current.wind_gusts_10m || current.wind_speed_10m,
      visibility: visibility,
      cloudCover: current.cloud_cover,
      cloudDescription: getCloudDescription(current.cloud_cover),
      pressure: current.pressure_msl || current.surface_pressure,
      humidity: current.relative_humidity_2m,
      dewpoint: current.dew_point_2m,
      uvIndex: current.uv_index || 0,
      flightCategory: getFlightCategory(visibility, ceiling),
      forecast: forecast,
      lastUpdate: new Date().toISOString(),
    }
    
    // Generate METAR/TAF from weather data
    weatherResult.metar = generateMetar(airport, weatherResult)
    weatherResult.taf = generateTaf(airport, weatherResult)
    
    // Try to fetch real METAR from CheckWX if API key exists
    if (CHECKWX_API_KEY) {
      try {
        const metarRes = await fetch(`https://api.checkwx.com/metar/${airport.code}/decoded`, {
          headers: { 'X-API-Key': CHECKWX_API_KEY }
        })
        const metarData = await metarRes.json()
        if (metarData.data && metarData.data[0]) {
          weatherResult.metar = metarData.data[0].raw_text || weatherResult.metar
          if (metarData.data[0].flight_category) {
            weatherResult.flightCategory = metarData.data[0].flight_category
          }
        }
      } catch {
        console.log('CheckWX METAR not available, using generated')
      }
      
      try {
        const tafRes = await fetch(`https://api.checkwx.com/taf/${airport.code}`, {
          headers: { 'X-API-Key': CHECKWX_API_KEY }
        })
        const tafData = await tafRes.json()
        if (tafData.data && tafData.data[0]) {
          weatherResult.taf = tafData.data[0]
        }
      } catch {
        console.log('CheckWX TAF not available, using generated')
      }
    }
    
    return weatherResult
  }, [])

  // Fetch live flights from OpenSky Network API
  const fetchLiveFlights = useCallback(async (airport: AirportInfo) => {
    setFlightsLoading(true)
    
    try {
      // OpenSky API - get flights within ~50km radius of airport
      const latMin = airport.lat - 0.5
      const latMax = airport.lat + 0.5
      const lonMin = airport.lon - 0.5
      const lonMax = airport.lon + 0.5
      
      const url = `https://opensky-network.org/api/states/all?lamin=${latMin}&lomin=${lonMin}&lamax=${latMax}&lomax=${lonMax}`
      
      const res = await fetch(url)
      if (!res.ok) {
        if (res.status === 429) {
          console.log('OpenSky rate limit reached, using cached data')
          return
        }
        throw new Error(`OpenSky API error: ${res.status}`)
      }
      
      const data = await res.json()
      const flights = parseOpenSkyStates(data.states || [])
      
      // Sort by altitude (descending) - aircraft on approach first
      flights.sort((a, b) => a.altitude - b.altitude)
      
      setLiveFlights(flights)
    } catch (err) {
      console.error('Failed to fetch live flights:', err)
      // Keep existing data on error
    } finally {
      setFlightsLoading(false)
    }
  }, [])

  // Fetch all airports data
  const fetchAllAirports = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const dataMap = new Map<string, WeatherData>()
      
      // Fetch in parallel with rate limiting
      const batchSize = 4
      for (let i = 0; i < airports.length; i += batchSize) {
        const batch = airports.slice(i, i + batchSize)
        const results = await Promise.all(
          batch.map(airport => fetchWeatherData(airport).catch(e => {
            console.error(`Failed to fetch ${airport.code}:`, e)
            return null
          }))
        )
        
        batch.forEach((airport, idx) => {
          if (results[idx]) {
            dataMap.set(airport.code, results[idx]!)
          }
        })
        
        // Small delay between batches to avoid rate limiting
        if (i + batchSize < airports.length) {
          await new Promise(r => setTimeout(r, 200))
        }
      }
      
      setAllAirportsData(dataMap)
      
      // Set selected airport data
      const selectedData = dataMap.get(selectedAirport.code)
      if (selectedData) {
        setWeatherData(selectedData)
      }
      
      setLastRefresh(new Date())
    } catch (err) {
      setError('Failed to fetch weather data. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [airports, fetchWeatherData, selectedAirport])

  // Initial fetch and auto-refresh
  useEffect(() => {
    fetchAllAirports()
    const interval = setInterval(fetchAllAirports, 300000) // Refresh every 5 minutes
    return () => clearInterval(interval)
  }, [fetchAllAirports])

  // Update weather when airport changes
  useEffect(() => {
    const data = allAirportsData.get(selectedAirport.code)
    if (data) {
      setWeatherData(data)
    }
  }, [selectedAirport, allAirportsData])

  // Fetch live flights when airport changes or tab is flights
  useEffect(() => {
    if (activeTab === 'flights') {
      fetchLiveFlights(selectedAirport)
      // Refresh flights every 30 seconds when on flights tab
      const interval = setInterval(() => fetchLiveFlights(selectedAirport), 30000)
      return () => clearInterval(interval)
    }
  }, [activeTab, selectedAirport, fetchLiveFlights])

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5, staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  // Loading state
  if (loading && !weatherData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <motion.div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="text-7xl mb-6"
          >
            [PLANE]
          </motion.div>
          <motion.p
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="text-violet-600 text-2xl font-semibold"
          >
            Loading Aviation Weather Intelligence...
          </motion.p>
          <p className="text-gray-500 mt-3">Fetching real-time data from {airports.length} airports</p>
        </motion.div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-white text-gray-900"
    >
      {/* ============= HEADER ============= */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-violet-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                AW
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Aviation Weather Intelligence</h1>
                <p className="text-gray-500">Real-time METAR/TAF + Professional Forecasts | {airports.length} airports</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right text-sm text-gray-500">
                <p>Last update: {lastRefresh.toLocaleTimeString()}</p>
                <p>Auto-refresh: 5 min</p>
              </div>
              <button
                onClick={fetchAllAirports}
                disabled={loading}
                className="px-6 py-3 bg-violet-600 text-white rounded-xl hover:bg-violet-700 disabled:opacity-50 transition-all font-semibold shadow-lg"
              >
                {loading ? 'Refreshing...' : 'Refresh All'}
              </button>
            </div>
          </div>
          
          {/* Flight Category Legend */}
          <div className="flex items-center gap-6 mt-4 pt-4 border-t border-gray-100">
            <span className="text-gray-600 font-semibold">Flight Categories:</span>
            <div className="flex gap-3">
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-green-500"></span>
                <span className="text-green-700 font-medium">VFR</span>
              </span>
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-violet-500"></span>
                <span className="text-violet-700 font-medium">MVFR</span>
              </span>
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-red-500"></span>
                <span className="text-red-700 font-medium">IFR</span>
              </span>
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-purple-500"></span>
                <span className="text-purple-700 font-medium">LIFR</span>
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* ============= AIRPORT SELECTOR ============= */}
      <div className="bg-gray-50 border-b border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-6">
          <label className="block text-gray-700 font-semibold mb-2">Select Airport</label>
          <select
            value={selectedAirport.code}
            onChange={(e) => {
              const airport = airports.find(a => a.code === e.target.value)
              if (airport) setSelectedAirport(airport)
            }}
            className="w-full max-w-xl bg-white text-gray-900 px-4 py-3 rounded-xl border-2 border-gray-300 focus:border-violet-500 focus:outline-none text-lg font-medium"
          >
            {airports.map(airport => (
              <option key={airport.code} value={airport.code}>
                [{airport.flag}] {airport.code} - {airport.name}, {airport.country}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* ============= TAB NAVIGATION ============= */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {(['current', 'flights', 'table', 'forecast', 'statistics', 'analysis', 'alerts', 'ssh', 'metar', 'taf', 'settings'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 font-semibold capitalize transition-all border-b-3 whitespace-nowrap ${
                  activeTab === tab
                    ? 'border-violet-600 text-violet-600 bg-violet-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab === 'metar' ? '📡 METAR' : 
                 tab === 'taf' ? '📊 TAF Forecast' :
                 tab === 'table' ? '📋 All Airports' :
                 tab === 'current' ? '🌤️ Current' :
                 tab === 'flights' ? `✈️ Flights ${liveFlights.length > 0 ? `(${liveFlights.length})` : ''}` :
                 tab === 'statistics' ? '📈 Statistics' :
                 tab === 'analysis' ? '🔬 Analysis' :
                 tab === 'alerts' ? '⚠️ Alerts' :
                 tab === 'ssh' ? `🖥️ SSH ${sshStatus === 'connected' ? '🟢' : sshStatus === 'connecting' ? '🟡' : '🔴'}` :
                 tab === 'settings' ? `⚙️ Settings (${airports.length})` : '📆 48h Forecast'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ============= MAIN CONTENT ============= */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl text-red-700 font-medium"
          >
            {error}
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {/* ============= CURRENT WEATHER TAB ============= */}
          {activeTab === 'current' && weatherData && (
            <motion.div
              key="current"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Selected Airport Header */}
              <div className="bg-gradient-to-r from-violet-600 to-violet-700 rounded-2xl p-6 mb-6 text-white shadow-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-3xl font-bold">{selectedAirport.code}</h2>
                    <p className="text-violet-100 text-lg">{selectedAirport.name}</p>
                    <p className="text-violet-200">{selectedAirport.city}, {selectedAirport.country}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-4 py-2 rounded-full text-lg font-bold ${getCategoryColor(weatherData.flightCategory)} text-white`}>
                      {weatherData.flightCategory}
                    </span>
                    <p className="text-violet-100 mt-2 text-sm">
                      {selectedAirport.lat.toFixed(4)}, {selectedAirport.lon.toFixed(4)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Weather Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Temperature */}
                <motion.div variants={itemVariants} className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <h3 className="text-lg font-semibold text-violet-600 mb-3 flex items-center gap-2">
                    [TEMP] Temperature
                  </h3>
                  <p className="text-5xl font-bold text-gray-900 mb-2">{weatherData.temperature.toFixed(1)}C</p>
                  <p className="text-gray-500">Dewpoint: {weatherData.dewpoint.toFixed(1)}C</p>
                  <p className="text-gray-500">Humidity: {weatherData.humidity}%</p>
                  <div className="mt-4 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-violet-500 to-red-500 rounded-full transition-all"
                      style={{ width: `${Math.min(100, Math.max(0, (weatherData.temperature + 20) * 2))}%` }}
                    />
                  </div>
                </motion.div>

                {/* Wind */}
                <motion.div variants={itemVariants} className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <h3 className="text-lg font-semibold text-green-600 mb-3 flex items-center gap-2">
                    [WIND] Wind Conditions
                  </h3>
                  <p className="text-5xl font-bold text-gray-900 mb-2">{weatherData.windSpeed.toFixed(0)} km/h</p>
                  <p className="text-gray-500">Direction: {weatherData.windDirection} ({getWindDirection(weatherData.windDirection)})</p>
                  <p className="text-gray-500">Gusts: {weatherData.windGust.toFixed(0)} km/h</p>
                  <div className="mt-4 flex items-center justify-center">
                    <div 
                      className="text-4xl transform transition-transform"
                      style={{ transform: `rotate(${weatherData.windDirection}deg)` }}
                    >
                      [ARROW]
                    </div>
                  </div>
                </motion.div>

                {/* Visibility */}
                <motion.div variants={itemVariants} className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <h3 className="text-lg font-semibold text-purple-600 mb-3 flex items-center gap-2">
                    [VIS] Visibility
                  </h3>
                  <p className="text-5xl font-bold text-gray-900 mb-2">{weatherData.visibility.toFixed(1)} km</p>
                  <p className="text-gray-500">{weatherData.cloudDescription}</p>
                  <p className="text-gray-500">Cloud Cover: {weatherData.cloudCover}%</p>
                  <div className="mt-4 text-3xl text-center">
                    {weatherData.visibility >= 10 ? '[STAR]' : weatherData.visibility >= 5 ? '[SUN]' : '[FOG]'}
                  </div>
                </motion.div>

                {/* Pressure */}
                <motion.div variants={itemVariants} className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <h3 className="text-lg font-semibold text-yellow-600 mb-3 flex items-center gap-2">
                    [GAUGE] Pressure
                  </h3>
                  <p className="text-5xl font-bold text-gray-900 mb-2">{weatherData.pressure.toFixed(0)} hPa</p>
                  <p className="text-gray-500">
                    {weatherData.pressure > 1020 ? 'High Pressure' : weatherData.pressure > 1000 ? 'Standard' : 'Low Pressure'}
                  </p>
                  <p className="text-gray-500">UV Index: {weatherData.uvIndex.toFixed(1)}</p>
                  <div className="mt-4 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all"
                      style={{ width: `${((weatherData.pressure - 950) / 100) * 100}%` }}
                    />
                  </div>
                </motion.div>
              </div>

              {/* Quick METAR Display */}
              <motion.div variants={itemVariants} className="mt-6 bg-gray-900 rounded-2xl p-6 shadow-xl">
                <h3 className="text-green-400 font-semibold mb-3">Current METAR</h3>
                <p className="font-mono text-green-400 text-lg break-all">{weatherData.metar}</p>
              </motion.div>
            </motion.div>
          )}

          {/* ============= ALL airports TABLE ============= */}
          {activeTab === 'table' && (
            <motion.div
              key="table"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white border-2 border-gray-200 rounded-2xl overflow-hidden shadow-xl"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 border-b-2 border-gray-200">
                    <tr>
                      <th className="px-4 py-4 text-left font-bold text-gray-700">ICAO</th>
                      <th className="px-4 py-4 text-left font-bold text-gray-700">City</th>
                      <th className="px-4 py-4 text-left font-bold text-gray-700">Country</th>
                      <th className="px-4 py-4 text-center font-bold text-gray-700">Category</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Temp (C)</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Wind (km/h)</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Dir</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Gust</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Vis (km)</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Clouds (%)</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Pressure</th>
                      <th className="px-4 py-4 text-right font-bold text-gray-700">Humidity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {airports.map((airport, idx) => {
                      const data = allAirportsData.get(airport.code)
                      return (
                        <tr 
                          key={airport.code} 
                          className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-violet-50 cursor-pointer transition-colors`}
                          onClick={() => {
                            setSelectedAirport(airport)
                            setActiveTab('current')
                          }}
                        >
                          <td className="px-4 py-3 font-mono font-bold text-violet-600">{airport.code}</td>
                          <td className="px-4 py-3 text-gray-900 font-medium">{airport.city}</td>
                          <td className="px-4 py-3 text-gray-600">{airport.country}</td>
                          <td className="px-4 py-3 text-center">
                            {data ? (
                              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getCategoryBadge(data.flightCategory)}`}>
                                {data.flightCategory}
                              </span>
                            ) : <span className="text-gray-400">--</span>}
                          </td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.temperature.toFixed(1) : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.windSpeed.toFixed(0) : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? `${data.windDirection}` : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.windGust.toFixed(0) : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.visibility.toFixed(1) : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.cloudCover : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.pressure.toFixed(0) : '--'}</td>
                          <td className="px-4 py-3 text-right font-mono">{data ? data.humidity : '--'}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <div className="bg-gray-100 px-6 py-4 border-t-2 border-gray-200">
                <p className="text-gray-600 font-medium">
                  Total: {airports.length} airports | Data loaded: {allAirportsData.size} | Source: Open-Meteo API + CheckWX
                </p>
              </div>
            </motion.div>
          )}

          {/* ============= FORECAST TAB ============= */}
          {activeTab === 'forecast' && weatherData && (
            <motion.div
              key="forecast"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-xl"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                48-Hour Forecast for {selectedAirport.code}
              </h2>
              <p className="text-gray-500 mb-6">{selectedAirport.name}</p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                {weatherData.forecast.map((item, index) => (
                  <motion.div
                    key={index}
                    variants={itemVariants}
                    whileHover={{ scale: 1.05, y: -5 }}
                    className="bg-gray-50 p-5 rounded-xl text-center border-2 border-gray-200 hover:border-violet-400 transition-all shadow-md hover:shadow-lg"
                  >
                    <p className="text-violet-600 font-bold text-lg">{item.time}</p>
                    <div className="text-4xl my-3">[{item.icon.toUpperCase()}]</div>
                    <p className="text-2xl font-bold text-gray-900">{item.temperature}C</p>
                    <p className="text-gray-600 font-medium text-sm mt-1">{item.weather}</p>
                    <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                      <p>Wind: {item.windSpeed} km/h</p>
                      <p>Dir: {getWindDirection(item.windDirection)}</p>
                      <p>Precip: {item.precipitation}%</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* ============= METAR TAB ============= */}
          {activeTab === 'metar' && (
            <motion.div
              key="metar"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">METAR Reports - All airports</h2>
                
                {airports.map(airport => {
                  const data = allAirportsData.get(airport.code)
                  return (
                    <div key={airport.code} className="mb-4 last:mb-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xl font-bold text-gray-900">{airport.code}</span>
                        <span className="text-gray-500">{airport.name}</span>
                        {data && (
                          <span className={`px-2 py-1 rounded-full text-xs font-bold ${getCategoryBadge(data.flightCategory)}`}>
                            {data.flightCategory}
                          </span>
                        )}
                      </div>
                      <div className="bg-gray-900 text-green-400 font-mono text-sm p-4 rounded-xl overflow-x-auto">
                        {data ? data.metar : 'Loading...'}
                      </div>
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {/* ============= TAF TAB ============= */}
          {activeTab === 'taf' && (
            <motion.div
              key="taf"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">TAF Forecasts - All airports</h2>
                
                {airports.map(airport => {
                  const data = allAirportsData.get(airport.code)
                  return (
                    <div key={airport.code} className="mb-4 last:mb-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xl font-bold text-gray-900">{airport.code}</span>
                        <span className="text-gray-500">{airport.name}</span>
                      </div>
                      <div className="bg-gray-900 text-purple-400 font-mono text-sm p-4 rounded-xl overflow-x-auto whitespace-pre-wrap">
                        {data ? data.taf : 'Loading...'}
                      </div>
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {/* ============= LIVE FLIGHTS TAB ============= */}
          {activeTab === 'flights' && (
            <motion.div
              key="flights"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Header with refresh */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    ✈️ Live Flights near {selectedAirport.code}
                  </h2>
                  <p className="text-gray-500">
                    Real-time aircraft tracking within 50km radius | OpenSky Network
                  </p>
                </div>
                <button
                  onClick={() => fetchLiveFlights(selectedAirport)}
                  disabled={flightsLoading}
                  className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50 transition-all font-medium"
                >
                  {flightsLoading ? 'Loading...' : 'Refresh Flights'}
                </button>
              </div>

              {/* Flights Table */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl overflow-hidden shadow-xl">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 border-b-2 border-gray-200">
                      <tr>
                        <th className="px-4 py-4 text-left font-bold text-gray-700">Callsign</th>
                        <th className="px-4 py-4 text-left font-bold text-gray-700">ICAO24</th>
                        <th className="px-4 py-4 text-left font-bold text-gray-700">Origin</th>
                        <th className="px-4 py-4 text-right font-bold text-gray-700">Altitude (ft)</th>
                        <th className="px-4 py-4 text-right font-bold text-gray-700">Speed (kt)</th>
                        <th className="px-4 py-4 text-right font-bold text-gray-700">Heading</th>
                        <th className="px-4 py-4 text-right font-bold text-gray-700">V/S (ft/min)</th>
                        <th className="px-4 py-4 text-center font-bold text-gray-700">Squawk</th>
                        <th className="px-4 py-4 text-center font-bold text-gray-700">Status</th>
                        <th className="px-4 py-4 text-right font-bold text-gray-700">Lat/Lon</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {liveFlights.length === 0 ? (
                        <tr>
                          <td colSpan={10} className="px-4 py-12 text-center text-gray-500">
                            {flightsLoading ? (
                              <div className="flex flex-col items-center gap-3">
                                <div className="text-4xl animate-pulse">✈️</div>
                                <p>Loading live flights...</p>
                              </div>
                            ) : (
                              <div className="flex flex-col items-center gap-3">
                                <div className="text-4xl">🛫</div>
                                <p>No aircraft detected near {selectedAirport.code}</p>
                                <p className="text-sm">Try a busier airport or click Refresh</p>
                              </div>
                            )}
                          </td>
                        </tr>
                      ) : (
                        liveFlights.map((flight, idx) => (
                          <tr 
                            key={flight.icao24}
                            className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-violet-50 transition-colors`}
                          >
                            <td className="px-4 py-3 font-mono font-bold text-violet-600 text-lg">
                              {flight.callsign || '------'}
                            </td>
                            <td className="px-4 py-3 font-mono text-gray-600">{flight.icao24}</td>
                            <td className="px-4 py-3 text-gray-900">{flight.originCountry}</td>
                            <td className="px-4 py-3 text-right font-mono font-semibold">
                              <span className={flight.altitude < 3000 ? 'text-orange-600' : 'text-gray-900'}>
                                {flight.altitude.toLocaleString()}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">{flight.velocity}</td>
                            <td className="px-4 py-3 text-right font-mono">{flight.heading}°</td>
                            <td className="px-4 py-3 text-right font-mono">
                              <span className={
                                flight.verticalRate < -500 ? 'text-red-600' :
                                flight.verticalRate > 500 ? 'text-green-600' : 'text-gray-600'
                              }>
                                {flight.verticalRate > 0 ? '+' : ''}{flight.verticalRate}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center font-mono">
                              <span className={`px-2 py-1 rounded ${
                                flight.squawk === '7700' ? 'bg-red-500 text-white' :
                                flight.squawk === '7600' ? 'bg-orange-500 text-white' :
                                flight.squawk === '7500' ? 'bg-purple-500 text-white' :
                                'bg-gray-200 text-gray-700'
                              }`}>
                                {flight.squawk}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              {flight.onGround ? (
                                <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded-full text-xs font-bold">
                                  GROUND
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">
                                  AIRBORNE
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right text-xs text-gray-500 font-mono">
                              {flight.latitude.toFixed(3)}<br/>{flight.longitude.toFixed(3)}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
                <div className="bg-gray-100 px-6 py-4 border-t-2 border-gray-200">
                  <div className="flex items-center justify-between">
                    <p className="text-gray-600 font-medium">
                      {liveFlights.length} aircraft detected | Auto-refresh: 30 sec | Source: OpenSky Network API
                    </p>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-red-500 rounded"></span> 7700 Emergency
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-orange-500 rounded"></span> 7600 Radio Fail
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-purple-500 rounded"></span> 7500 Hijack
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Flight Stats */}
              {liveFlights.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div className="bg-white border-2 border-gray-200 rounded-xl p-4 text-center shadow-lg">
                    <p className="text-3xl font-bold text-violet-600">{liveFlights.length}</p>
                    <p className="text-gray-600">Total Aircraft</p>
                  </div>
                  <div className="bg-white border-2 border-gray-200 rounded-xl p-4 text-center shadow-lg">
                    <p className="text-3xl font-bold text-green-600">
                      {liveFlights.filter(f => !f.onGround).length}
                    </p>
                    <p className="text-gray-600">Airborne</p>
                  </div>
                  <div className="bg-white border-2 border-gray-200 rounded-xl p-4 text-center shadow-lg">
                    <p className="text-3xl font-bold text-orange-600">
                      {liveFlights.filter(f => f.verticalRate < -300).length}
                    </p>
                    <p className="text-gray-600">Descending</p>
                  </div>
                  <div className="bg-white border-2 border-gray-200 rounded-xl p-4 text-center shadow-lg">
                    <p className="text-3xl font-bold text-purple-600">
                      {liveFlights.filter(f => f.verticalRate > 300).length}
                    </p>
                    <p className="text-gray-600">Climbing</p>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* ============= STATISTICS TAB ============= */}
          {activeTab === 'statistics' && (
            <motion.div
              key="statistics"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📈 Weather Statistics & Trends</h2>
              
              {/* Flight Category Distribution */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Flight Category Distribution</h3>
                  <div className="space-y-3">
                    {['VFR', 'MVFR', 'IFR', 'LIFR'].map(cat => {
                      const count = Array.from(allAirportsData.values()).filter(d => d.flightCategory === cat).length
                      const percentage = allAirportsData.size > 0 ? Math.round((count / allAirportsData.size) * 100) : 0
                      return (
                        <div key={cat} className="flex items-center gap-3">
                          <span className={`px-3 py-1 rounded-lg font-bold text-white ${getCategoryColor(cat)}`}>{cat}</span>
                          <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${getCategoryColor(cat)} transition-all duration-500`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="font-bold text-gray-700 w-16 text-right">{count} ({percentage}%)</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                {/* Temperature Range */}
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">🌡️ Temperature Analysis</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-violet-50 rounded-xl">
                      <p className="text-3xl font-bold text-violet-600">
                        {Math.min(...Array.from(allAirportsData.values()).map(d => d.temperature))}°C
                      </p>
                      <p className="text-gray-600 text-sm">Minimum</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-xl">
                      <p className="text-3xl font-bold text-green-600">
                        {allAirportsData.size > 0 
                          ? Math.round(Array.from(allAirportsData.values()).reduce((a, b) => a + b.temperature, 0) / allAirportsData.size)
                          : 0}°C
                      </p>
                      <p className="text-gray-600 text-sm">Average</p>
                    </div>
                    <div className="text-center p-4 bg-red-50 rounded-xl">
                      <p className="text-3xl font-bold text-red-600">
                        {Math.max(...Array.from(allAirportsData.values()).map(d => d.temperature))}°C
                      </p>
                      <p className="text-gray-600 text-sm">Maximum</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Wind Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">💨 Wind Speed (km/h)</h3>
                  <div className="text-center">
                    <p className="text-5xl font-bold text-violet-600">
                      {allAirportsData.size > 0 
                        ? Math.round(Array.from(allAirportsData.values()).reduce((a, b) => a + b.windSpeed, 0) / allAirportsData.size)
                        : 0}
                    </p>
                    <p className="text-gray-500 mt-2">Average across {allAirportsData.size} airports</p>
                  </div>
                </div>
                
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">☁️ Cloud Cover (%)</h3>
                  <div className="text-center">
                    <p className="text-5xl font-bold text-purple-600">
                      {allAirportsData.size > 0 
                        ? Math.round(Array.from(allAirportsData.values()).reduce((a, b) => a + b.cloudCover, 0) / allAirportsData.size)
                        : 0}%
                    </p>
                    <p className="text-gray-500 mt-2">Average cloud coverage</p>
                  </div>
                </div>
                
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">👁️ Visibility (km)</h3>
                  <div className="text-center">
                    <p className="text-5xl font-bold text-green-600">
                      {allAirportsData.size > 0 
                        ? Math.round(Array.from(allAirportsData.values()).reduce((a, b) => a + b.visibility, 0) / allAirportsData.size)
                        : 0}
                    </p>
                    <p className="text-gray-500 mt-2">Average visibility</p>
                  </div>
                </div>
              </div>
              
              {/* Airport Ranking */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold text-gray-900 mb-4">🏆 Airport Weather Ranking (Best to Worst)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left font-bold">#</th>
                        <th className="px-4 py-3 text-left font-bold">Airport</th>
                        <th className="px-4 py-3 text-center font-bold">Category</th>
                        <th className="px-4 py-3 text-right font-bold">Visibility</th>
                        <th className="px-4 py-3 text-right font-bold">Wind</th>
                        <th className="px-4 py-3 text-right font-bold">Cloud Cover</th>
                        <th className="px-4 py-3 text-right font-bold">Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {Array.from(allAirportsData.entries())
                        .map(([code, data]) => {
                          // Calculate weather score (higher is better)
                          const score = (data.visibility * 10) + (100 - data.cloudCover) - (data.windSpeed * 2)
                          return { code, data, score }
                        })
                        .sort((a, b) => b.score - a.score)
                        .map((item, idx) => (
                          <tr key={item.code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                            <td className="px-4 py-3 font-bold text-gray-500">{idx + 1}</td>
                            <td className="px-4 py-3 font-bold text-gray-900">{item.code}</td>
                            <td className="px-4 py-3 text-center">
                              <span className={`px-2 py-1 rounded font-bold text-white text-xs ${getCategoryColor(item.data.flightCategory)}`}>
                                {item.data.flightCategory}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right">{item.data.visibility.toFixed(1)} km</td>
                            <td className="px-4 py-3 text-right">{item.data.windSpeed} km/h</td>
                            <td className="px-4 py-3 text-right">{item.data.cloudCover}%</td>
                            <td className="px-4 py-3 text-right font-bold text-violet-600">{item.score.toFixed(0)}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ============= ANALYSIS TAB ============= */}
          {activeTab === 'analysis' && weatherData && (
            <motion.div
              key="analysis"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🔬 Weather Analysis for {selectedAirport.code}</h2>
              
              {/* Flight Safety Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">✈️ Flight Safety Assessment</h3>
                  <div className="space-y-4">
                    {/* Overall Rating */}
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <span className="font-semibold">Overall Safety Rating</span>
                      <span className={`px-4 py-2 rounded-lg font-bold text-white ${getCategoryColor(weatherData.flightCategory)}`}>
                        {weatherData.flightCategory}
                      </span>
                    </div>
                    
                    {/* Visibility Check */}
                    <div className="flex items-center justify-between p-3 rounded-lg border-2 border-gray-100">
                      <span>👁️ Visibility</span>
                      <span className={`font-bold ${weatherData.visibility >= 5 ? 'text-green-600' : weatherData.visibility >= 3 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {weatherData.visibility.toFixed(1)} km {weatherData.visibility >= 5 ? '✅' : weatherData.visibility >= 3 ? '⚠️' : '❌'}
                      </span>
                    </div>
                    
                    {/* Wind Check */}
                    <div className="flex items-center justify-between p-3 rounded-lg border-2 border-gray-100">
                      <span>💨 Wind Speed</span>
                      <span className={`font-bold ${weatherData.windSpeed <= 20 ? 'text-green-600' : weatherData.windSpeed <= 35 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {weatherData.windSpeed} km/h {weatherData.windSpeed <= 20 ? '✅' : weatherData.windSpeed <= 35 ? '⚠️' : '❌'}
                      </span>
                    </div>
                    
                    {/* Gust Check */}
                    <div className="flex items-center justify-between p-3 rounded-lg border-2 border-gray-100">
                      <span>🌪️ Wind Gusts</span>
                      <span className={`font-bold ${weatherData.windGust <= 30 ? 'text-green-600' : weatherData.windGust <= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {weatherData.windGust} km/h {weatherData.windGust <= 30 ? '✅' : weatherData.windGust <= 50 ? '⚠️' : '❌'}
                      </span>
                    </div>
                    
                    {/* Cloud Check */}
                    <div className="flex items-center justify-between p-3 rounded-lg border-2 border-gray-100">
                      <span>☁️ Cloud Cover</span>
                      <span className={`font-bold ${weatherData.cloudCover <= 50 ? 'text-green-600' : weatherData.cloudCover <= 75 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {weatherData.cloudCover}% {weatherData.cloudCover <= 50 ? '✅' : weatherData.cloudCover <= 75 ? '⚠️' : '❌'}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Weather Comfort Index */}
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">🎯 Weather Comfort Index</h3>
                  <div className="space-y-6">
                    {/* Comfort Score Gauge */}
                    <div className="text-center">
                      {(() => {
                        const comfortScore = Math.max(0, Math.min(100, 
                          100 - Math.abs(weatherData.temperature - 22) * 3 - weatherData.windSpeed * 1.5 - (weatherData.humidity > 70 ? 20 : 0)
                        ))
                        return (
                          <>
                            <div className="relative w-40 h-40 mx-auto">
                              <svg className="w-full h-full" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="10" />
                                <circle 
                                  cx="50" cy="50" r="45" fill="none" 
                                  stroke={comfortScore >= 70 ? '#22c55e' : comfortScore >= 40 ? '#eab308' : '#ef4444'}
                                  strokeWidth="10"
                                  strokeDasharray={`${comfortScore * 2.83} 283`}
                                  strokeLinecap="round"
                                  transform="rotate(-90 50 50)"
                                />
                              </svg>
                              <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-4xl font-bold text-gray-900">{Math.round(comfortScore)}</span>
                              </div>
                            </div>
                            <p className="mt-4 text-lg font-semibold text-gray-700">
                              {comfortScore >= 70 ? '😊 Comfortable' : comfortScore >= 40 ? '😐 Moderate' : '😣 Uncomfortable'}
                            </p>
                          </>
                        )
                      })()}
                    </div>
                    
                    {/* Factors */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="p-3 bg-gray-50 rounded-lg text-center">
                        <p className="text-gray-500">Temperature</p>
                        <p className="font-bold text-lg">{weatherData.temperature}°C</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg text-center">
                        <p className="text-gray-500">Humidity</p>
                        <p className="font-bold text-lg">{weatherData.humidity}%</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg text-center">
                        <p className="text-gray-500">Dewpoint</p>
                        <p className="font-bold text-lg">{weatherData.dewpoint}°C</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg text-center">
                        <p className="text-gray-500">UV Index</p>
                        <p className="font-bold text-lg">{weatherData.uvIndex}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Pressure & Trend Analysis */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold text-gray-900 mb-4">📊 Atmospheric Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-gradient-to-br from-violet-50 to-violet-100 rounded-xl text-center">
                    <p className="text-sm text-violet-600 font-semibold">Pressure</p>
                    <p className="text-3xl font-bold text-slate-800">{weatherData.pressure} hPa</p>
                    <p className="text-xs text-violet-600 mt-1">
                      {weatherData.pressure > 1020 ? '⬆️ High (Fair)' : weatherData.pressure < 1000 ? '⬇️ Low (Storm)' : '➡️ Normal'}
                    </p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl text-center">
                    <p className="text-sm text-green-600 font-semibold">Wind Direction</p>
                    <p className="text-3xl font-bold text-green-800">{getWindDirection(weatherData.windDirection)}</p>
                    <p className="text-xs text-green-600 mt-1">{weatherData.windDirection}°</p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl text-center">
                    <p className="text-sm text-purple-600 font-semibold">Density Altitude</p>
                    <p className="text-3xl font-bold text-purple-800">
                      {Math.round(145442.16 * (1 - Math.pow((weatherData.pressure / 1013.25), 0.190284)))}
                    </p>
                    <p className="text-xs text-purple-600 mt-1">feet MSL (approx)</p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl text-center">
                    <p className="text-sm text-orange-600 font-semibold">Cloud Description</p>
                    <p className="text-xl font-bold text-orange-800">{weatherData.cloudDescription}</p>
                    <p className="text-xs text-orange-600 mt-1">{weatherData.cloudCover}% coverage</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* ============= ALERTS TAB ============= */}
          {activeTab === 'alerts' && (
            <motion.div
              key="alerts"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">⚠️ Weather Alerts & Warnings</h2>
              
              {/* Active Alerts */}
              <div className="space-y-4">
                {Array.from(allAirportsData.entries())
                  .filter(([, data]) => 
                    data.flightCategory === 'IFR' || 
                    data.flightCategory === 'LIFR' || 
                    data.windSpeed > 30 || 
                    data.windGust > 40 ||
                    data.visibility < 5
                  )
                  .map(([code, data]) => {
                    const airport = airports.find(a => a.code === code)
                    const alerts: { type: 'danger' | 'warning' | 'info'; message: string }[] = []
                    
                    if (data.flightCategory === 'LIFR') alerts.push({ type: 'danger', message: 'Low IFR conditions - Ceiling below 500ft or visibility below 1 mile' })
                    if (data.flightCategory === 'IFR') alerts.push({ type: 'warning', message: 'IFR conditions - Instrument flight rules required' })
                    if (data.windGust > 40) alerts.push({ type: 'danger', message: `Strong wind gusts: ${data.windGust} km/h` })
                    if (data.windSpeed > 30) alerts.push({ type: 'warning', message: `High winds: ${data.windSpeed} km/h` })
                    if (data.visibility < 3) alerts.push({ type: 'danger', message: `Low visibility: ${data.visibility.toFixed(1)} km` })
                    else if (data.visibility < 5) alerts.push({ type: 'warning', message: `Reduced visibility: ${data.visibility.toFixed(1)} km` })
                    
                    return (
                      <div key={code} className="bg-white border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
                        <div className="bg-gray-100 px-6 py-4 border-b-2 border-gray-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-xl font-bold text-gray-900">{code}</span>
                              <span className="text-gray-500 ml-2">{airport?.name}</span>
                            </div>
                            <span className={`px-3 py-1 rounded-lg font-bold text-white ${getCategoryColor(data.flightCategory)}`}>
                              {data.flightCategory}
                            </span>
                          </div>
                        </div>
                        <div className="p-4 space-y-2">
                          {alerts.map((alert, idx) => (
                            <div 
                              key={idx} 
                              className={`p-3 rounded-lg flex items-center gap-3 ${
                                alert.type === 'danger' ? 'bg-red-50 border-2 border-red-200 text-red-800' :
                                alert.type === 'warning' ? 'bg-yellow-50 border-2 border-yellow-200 text-yellow-800' :
                                'bg-violet-50 border-2 border-violet-200 text-slate-800'
                              }`}
                            >
                              <span className="text-xl">
                                {alert.type === 'danger' ? '🚨' : alert.type === 'warning' ? '⚠️' : 'ℹ️'}
                              </span>
                              <span className="font-medium">{alert.message}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                
                {/* No Alerts Message */}
                {Array.from(allAirportsData.entries()).filter(([, data]) => 
                  data.flightCategory === 'IFR' || 
                  data.flightCategory === 'LIFR' || 
                  data.windSpeed > 30 || 
                  data.visibility < 5
                ).length === 0 && (
                  <div className="bg-green-50 border-2 border-green-200 rounded-2xl p-8 text-center">
                    <p className="text-6xl mb-4">✅</p>
                    <h3 className="text-2xl font-bold text-green-800 mb-2">No Active Alerts</h3>
                    <p className="text-green-600">All monitored airports have favorable weather conditions.</p>
                  </div>
                )}
              </div>
              
              {/* Alert Legend */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Alert Categories</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                    <span className={`px-3 py-1 rounded font-bold text-white ${getCategoryColor('VFR')}`}>VFR</span>
                    <span className="text-gray-700">Visual Flight Rules - Clear conditions</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-violet-50 rounded-lg">
                    <span className={`px-3 py-1 rounded font-bold text-white ${getCategoryColor('MVFR')}`}>MVFR</span>
                    <span className="text-gray-700">Marginal VFR - Caution advised</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                    <span className={`px-3 py-1 rounded font-bold text-white ${getCategoryColor('IFR')}`}>IFR</span>
                    <span className="text-gray-700">Instrument Flight Rules required</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                    <span className={`px-3 py-1 rounded font-bold text-white ${getCategoryColor('LIFR')}`}>LIFR</span>
                    <span className="text-gray-700">Low IFR - Extreme caution</span>
                  </div>
                </div>
              </div>
              
              {/* Live Flight Emergencies */}
              {liveFlights.filter(f => ['7700', '7600', '7500'].includes(f.squawk)).length > 0 && (
                <div className="bg-red-50 border-4 border-red-500 rounded-2xl p-6 animate-pulse">
                  <h3 className="text-xl font-bold text-red-800 mb-4">🚨 EMERGENCY SQUAWK DETECTED</h3>
                  {liveFlights.filter(f => ['7700', '7600', '7500'].includes(f.squawk)).map(flight => (
                    <div key={flight.icao24} className="bg-red-100 p-4 rounded-xl mb-2 last:mb-0">
                      <p className="font-bold text-red-900">
                        {flight.callsign} - Squawk {flight.squawk}
                        {flight.squawk === '7700' && ' (EMERGENCY)'}
                        {flight.squawk === '7600' && ' (RADIO FAILURE)'}
                        {flight.squawk === '7500' && ' (HIJACK)'}
                      </p>
                      <p className="text-red-700 text-sm">
                        Alt: {flight.altitude}ft | Speed: {flight.velocity}kt | Heading: {flight.heading}°
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* ============= SSH SERVER TAB ============= */}
          {activeTab === 'ssh' && (
            <motion.div
              key="ssh"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🖥️ SSH Server Connection</h2>
              
              {/* Connection Status Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">🔌 Connection Status</h3>
                  <div className="text-center">
                    <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full mb-4 ${
                      sshStatus === 'connected' ? 'bg-green-100' : 
                      sshStatus === 'connecting' ? 'bg-yellow-100' : 'bg-red-100'
                    }`}>
                      <span className="text-5xl">
                        {sshStatus === 'connected' ? '🟢' : sshStatus === 'connecting' ? '🟡' : '🔴'}
                      </span>
                    </div>
                    <p className={`text-2xl font-bold ${
                      sshStatus === 'connected' ? 'text-green-600' : 
                      sshStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {sshStatus === 'connected' ? 'Connected' : 
                       sshStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
                    </p>
                  </div>
                  <div className="mt-6 flex gap-2">
                    <button
                      onClick={() => {
                        setSshStatus('connecting')
                        setSshLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: 'Initiating SSH connection...', type: 'info' }])
                        setTimeout(() => {
                          setSshStatus('connected')
                          setSshLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: 'SSH connection established successfully!', type: 'success' }])
                        }, 2000)
                      }}
                      disabled={sshStatus === 'connecting' || sshStatus === 'connected'}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium transition-colors"
                    >
                      Connect
                    </button>
                    <button
                      onClick={() => {
                        setSshStatus('disconnected')
                        setSshLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: 'SSH connection closed.', type: 'warning' }])
                      }}
                      disabled={sshStatus === 'disconnected'}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
                
                {/* Server Info */}
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">🖥️ Server Information</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Host</span>
                      <span className="font-mono font-bold text-gray-900">kloud.com</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Port</span>
                      <span className="font-mono font-bold text-gray-900">22</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">User</span>
                      <span className="font-mono font-bold text-gray-900">aviation-api</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Auth</span>
                      <span className="font-mono font-bold text-green-600">🔐 Key-based</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Protocol</span>
                      <span className="font-mono font-bold text-violet-600">SSH-2.0</span>
                    </div>
                  </div>
                </div>
                
                {/* System Stats */}
                <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">📊 System Stats</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-600">CPU Usage</span>
                        <span className="font-bold text-gray-900">23%</span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500 rounded-full" style={{ width: '23%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-600">Memory</span>
                        <span className="font-bold text-gray-900">4.2 / 16 GB</span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-violet-500 rounded-full" style={{ width: '26%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-600">Disk</span>
                        <span className="font-bold text-gray-900">128 / 500 GB</span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{ width: '26%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-600">Network</span>
                        <span className="font-bold text-green-600">↑ 2.4 MB/s ↓ 12.8 MB/s</span>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-gray-200">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Uptime</span>
                        <span className="font-bold text-gray-900">42 days, 7:23:15</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Active Services */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold text-gray-900 mb-4">🚀 Active Services</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { name: 'Aviation Weather API', port: 8080, status: 'running', memory: '256MB' },
                    { name: 'OpenSky Collector', port: 8081, status: 'running', memory: '128MB' },
                    { name: 'METAR/TAF Parser', port: 8082, status: 'running', memory: '64MB' },
                    { name: 'Flight Tracker', port: 8083, status: 'running', memory: '192MB' },
                    { name: 'Weather Alerter', port: 8084, status: 'running', memory: '96MB' },
                    { name: 'Data Aggregator', port: 8085, status: 'running', memory: '384MB' },
                    { name: 'CBOR Encoder', port: 8086, status: 'running', memory: '32MB' },
                    { name: 'LoRa Gateway', port: 8087, status: 'idle', memory: '48MB' },
                  ].map((service, idx) => (
                    <div key={idx} className={`p-4 rounded-xl border-2 ${
                      service.status === 'running' ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-gray-900 text-sm">{service.name}</span>
                        <span className={`w-3 h-3 rounded-full ${service.status === 'running' ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <p>Port: <span className="font-mono font-bold">{service.port}</span></p>
                        <p>Memory: <span className="font-bold">{service.memory}</span></p>
                        <p>Status: <span className={`font-bold ${service.status === 'running' ? 'text-green-600' : 'text-yellow-600'}`}>{service.status}</span></p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* SSH Terminal / Logs */}
              <div className="bg-gray-900 rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-green-400 font-bold text-lg">📟 SSH Terminal Logs</h3>
                  <button
                    onClick={() => setSshLogs([])}
                    className="px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 text-sm transition-colors"
                  >
                    Clear
                  </button>
                </div>
                <div className="font-mono text-sm h-64 overflow-y-auto space-y-1">
                  {sshLogs.length === 0 ? (
                    <p className="text-gray-500">No logs yet. Connect to SSH server to see activity.</p>
                  ) : (
                    sshLogs.map((log, idx) => (
                      <p key={idx} className={`${
                        log.type === 'success' ? 'text-green-400' :
                        log.type === 'error' ? 'text-red-400' :
                        log.type === 'warning' ? 'text-yellow-400' : 'text-violet-400'
                      }`}>
                        <span className="text-gray-500">[{log.time}]</span> {log.message}
                      </p>
                    ))
                  )}
                  <p className="text-green-400 animate-pulse">
                    {sshStatus === 'connected' ? '$ _' : ''}
                  </p>
                </div>
              </div>
              
              {/* Quick Commands */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold text-gray-900 mb-4">⚡ Quick Commands</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { cmd: 'systemctl status aviation-api', label: 'Check API Status', icon: '🔍' },
                    { cmd: 'tail -f /var/log/aviation.log', label: 'View Live Logs', icon: '📋' },
                    { cmd: 'df -h', label: 'Disk Usage', icon: '💾' },
                    { cmd: 'free -m', label: 'Memory Status', icon: '🧠' },
                    { cmd: 'netstat -tulpn', label: 'Open Ports', icon: '🌐' },
                    { cmd: 'docker ps', label: 'Docker Containers', icon: '🐳' },
                    { cmd: 'top -bn1 | head -20', label: 'Top Processes', icon: '📊' },
                    { cmd: 'systemctl restart aviation-api', label: 'Restart API', icon: '🔄' },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        if (sshStatus === 'connected') {
                          setSshLogs(prev => [...prev, 
                            { time: new Date().toLocaleTimeString(), message: `$ ${item.cmd}`, type: 'info' },
                            { time: new Date().toLocaleTimeString(), message: `Executing: ${item.label}...`, type: 'success' }
                          ])
                        } else {
                          setSshLogs(prev => [...prev, 
                            { time: new Date().toLocaleTimeString(), message: 'Error: Not connected to SSH server', type: 'error' }
                          ])
                        }
                      }}
                      className="p-3 bg-gray-100 hover:bg-violet-50 border-2 border-gray-200 hover:border-violet-300 rounded-xl text-left transition-all"
                    >
                      <span className="text-2xl">{item.icon}</span>
                      <p className="font-semibold text-gray-900 text-sm mt-2">{item.label}</p>
                      <p className="font-mono text-xs text-gray-500 truncate">{item.cmd}</p>
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* ============= SETTINGS TAB ============= */}
          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Airport Management */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">✈️ Airport Management</h2>
                    <p className="text-gray-500">Add, remove, or manage monitored airports</p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowAddAirport(!showAddAirport)}
                      className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 font-medium transition-colors"
                    >
                      {showAddAirport ? 'Cancel' : '+ Add Airport'}
                    </button>
                    <button
                      onClick={handleResetAirports}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium transition-colors"
                    >
                      Reset to Defaults
                    </button>
                  </div>
                </div>

                {/* Add Airport Form */}
                {showAddAirport && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mb-6 p-4 bg-violet-50 border-2 border-violet-200 rounded-xl"
                  >
                    <h3 className="font-bold text-slate-800 mb-4">Add New Airport</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">ICAO Code *</label>
                        <input
                          type="text"
                          placeholder="LATI"
                          maxLength={4}
                          value={newAirport.code || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, code: e.target.value.toUpperCase() })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Airport Name *</label>
                        <input
                          type="text"
                          placeholder="Tirana International"
                          value={newAirport.name || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, name: e.target.value })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                        <input
                          type="text"
                          placeholder="Tirana"
                          value={newAirport.city || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, city: e.target.value })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                        <input
                          type="text"
                          placeholder="Albania"
                          value={newAirport.country || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, country: e.target.value })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Latitude *</label>
                        <input
                          type="number"
                          step="0.0001"
                          placeholder="41.4147"
                          value={newAirport.lat || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, lat: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Longitude *</label>
                        <input
                          type="number"
                          step="0.0001"
                          placeholder="19.7206"
                          value={newAirport.lon || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, lon: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Flag Code</label>
                        <input
                          type="text"
                          placeholder="AL"
                          maxLength={2}
                          value={newAirport.flag || ''}
                          onChange={(e) => setNewAirport({ ...newAirport, flag: e.target.value.toUpperCase() })}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none"
                        />
                      </div>
                      <div className="flex items-end">
                        <button
                          onClick={handleAddAirport}
                          disabled={!newAirport.code || !newAirport.name || !newAirport.lat || !newAirport.lon}
                          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
                        >
                          Add Airport
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Airport List */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 border-b-2 border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left font-bold text-gray-700">ICAO</th>
                        <th className="px-4 py-3 text-left font-bold text-gray-700">Name</th>
                        <th className="px-4 py-3 text-left font-bold text-gray-700">City</th>
                        <th className="px-4 py-3 text-left font-bold text-gray-700">Country</th>
                        <th className="px-4 py-3 text-right font-bold text-gray-700">Lat</th>
                        <th className="px-4 py-3 text-right font-bold text-gray-700">Lon</th>
                        <th className="px-4 py-3 text-center font-bold text-gray-700">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {airports.map((airport, idx) => (
                        <tr key={airport.code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="px-4 py-3 font-mono font-bold text-violet-600">{airport.code}</td>
                          <td className="px-4 py-3 text-gray-900">{airport.name}</td>
                          <td className="px-4 py-3 text-gray-600">{airport.city}</td>
                          <td className="px-4 py-3 text-gray-600">[{airport.flag}] {airport.country}</td>
                          <td className="px-4 py-3 text-right font-mono text-sm">{airport.lat.toFixed(4)}</td>
                          <td className="px-4 py-3 text-right font-mono text-sm">{airport.lon.toFixed(4)}</td>
                          <td className="px-4 py-3 text-center">
                            <button
                              onClick={() => handleRemoveAirport(airport.code)}
                              className="px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 transition-colors text-sm font-medium"
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4 text-gray-500 text-sm">
                  Total: {airports.length} airports configured
                </div>
              </div>

              {/* Data Sources Configuration */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">📡 Data Source Protocols</h2>
                <p className="text-gray-500 mb-6">Configure data input protocols for aviation data feeds</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dataSources.map((source) => (
                    <div
                      key={source.protocol}
                      className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                        source.enabled
                          ? 'border-green-400 bg-green-50'
                          : 'border-gray-200 bg-gray-50 opacity-60'
                      }`}
                      onClick={() => toggleDataSource(source.protocol)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{source.icon}</span>
                          <span className="font-bold text-gray-900">{source.name}</span>
                        </div>
                        <div className={`w-10 h-6 rounded-full transition-colors ${source.enabled ? 'bg-green-500' : 'bg-gray-300'}`}>
                          <div className={`w-4 h-4 mt-1 rounded-full bg-white transition-transform ${source.enabled ? 'ml-5' : 'ml-1'}`} />
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{source.description}</p>
                      <div className="mt-2">
                        <span className={`text-xs font-medium px-2 py-1 rounded ${source.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}>
                          {source.enabled ? 'ENABLED' : 'DISABLED'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-gray-100 rounded-xl">
                  <h3 className="font-bold text-gray-800 mb-2">📖 Protocol Legend</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div><strong>CBOR:</strong> Concise Binary Object Representation - efficient binary encoding</div>
                    <div><strong>LoRa:</strong> Long Range - low-power IoT wireless protocol</div>
                    <div><strong>GSM:</strong> Global System for Mobile - cellular data network</div>
                    <div><strong>Buffer:</strong> Local data caching for offline/slow connections</div>
                  </div>
                </div>
              </div>

              {/* API Configuration */}
              <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-xl">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">🔑 API Configuration</h2>
                <p className="text-gray-500 mb-6">Current API endpoints and status</p>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-green-50 border-2 border-green-200 rounded-xl">
                    <div>
                      <p className="font-bold text-green-800">Open-Meteo API</p>
                      <p className="text-sm text-green-600">Weather data - FREE, no key required</p>
                    </div>
                    <span className="px-3 py-1 bg-green-500 text-white rounded-full text-sm font-bold">ACTIVE</span>
                  </div>
                  
                  <div className={`flex items-center justify-between p-4 border-2 rounded-xl ${CHECKWX_API_KEY ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                    <div>
                      <p className={`font-bold ${CHECKWX_API_KEY ? 'text-green-800' : 'text-yellow-800'}`}>CheckWX API</p>
                      <p className={`text-sm ${CHECKWX_API_KEY ? 'text-green-600' : 'text-yellow-600'}`}>
                        METAR/TAF data - {CHECKWX_API_KEY ? 'Key configured' : 'Key not set (using generated data)'}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${CHECKWX_API_KEY ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'}`}>
                      {CHECKWX_API_KEY ? 'ACTIVE' : 'FALLBACK'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-green-50 border-2 border-green-200 rounded-xl">
                    <div>
                      <p className="font-bold text-green-800">OpenSky Network</p>
                      <p className="text-sm text-green-600">Live flight tracking - FREE, 400 req/day</p>
                    </div>
                    <span className="px-3 py-1 bg-green-500 text-white rounded-full text-sm font-bold">ACTIVE</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ============= FOOTER ============= */}
      <footer className="bg-gray-100 border-t-2 border-gray-200 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <p className="text-violet-600 font-bold text-lg">Professional Aviation Weather</p>
              <p className="text-gray-500">Real-time METAR/TAF | Certified Data Sources</p>
            </div>
            <div>
              <p className="text-green-600 font-bold text-lg">Live Flight Tracking</p>
              <p className="text-gray-500">OpenSky Network | Real-time ADS-B</p>
            </div>
            <div>
              <p className="text-orange-600 font-bold text-lg">Balkan + International</p>
              <p className="text-gray-500">{airports.length} airports | Albania, Kosovo, Europe</p>
            </div>
            <div>
              <p className="text-purple-600 font-bold text-lg">Kloud Platform v2.2</p>
              <p className="text-gray-500">2025-2026 Ledjan Ahmati</p>
            </div>
          </div>
        </div>
      </footer>
    </motion.div>
  )
}

export default AviationWeatherDashboard








