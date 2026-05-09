/**
 * KLOUD REAL PUBLIC DATA SOURCES
 * ==================================
 * NO MOCK DATA - ONLY REAL PUBLIC APIs
 * If data is unavailable, return "no_data" status
 */

import * as os from "os";
import * as crypto from "crypto";

// =================================================================================
// PUBLIC API CONFIGURATION - FREE, NO API KEY REQUIRED
// =================================================================================

const PUBLIC_APIS = {
  // Open-Meteo - Free weather API, no key needed
  OPEN_METEO: "https://api.open-meteo.com/v1/forecast",

  // USGS Earthquake API - Real-time seismic data
  USGS_EARTHQUAKES: "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary",

  // Open-Notify - ISS Location (real satellite data)
  ISS_LOCATION: "http://api.open-notify.org/iss-now.json",

  // CoinGecko - Real crypto prices (free tier)
  COINGECKO: "https://api.coingecko.com/api/v3",

  // ThingSpeak Public Channels - Real IoT sensor data
  THINGSPEAK_PUBLIC: "https://api.thingspeak.com/channels",

  // Public air quality from OpenAQ
  OPENAQ: "https://api.openaq.org/v3",
};

// Known public ThingSpeak channels with real sensor data
const PUBLIC_THINGSPEAK_CHANNELS = [
  {
    id: "12397",
    name: "Weather Station Boulder",
    fields: ["temperature", "humidity", "pressure"],
  },
  { id: "9", name: "Public Temperature Sensor", fields: ["temperature"] },
  { id: "417", name: "Air Quality Sensor", fields: ["pm25", "pm10", "co2"] },
];

// =================================================================================
// FETCH WITH TIMEOUT AND ERROR HANDLING
// =================================================================================

interface FetchResult<T> {
  success: boolean;
  data: T | null;
  error?: string;
  source: string;
  timestamp: string;
}

async function safeFetch<T>(
  url: string,
  source: string,
  timeoutMs: number = 10000,
): Promise<FetchResult<T>> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        "User-Agent": "Kloud-Industrial-Backend/1.0",
      },
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
        source,
        timestamp: new Date().toISOString(),
      };
    }

    const data = (await response.json()) as T;
    return {
      success: true,
      data,
      source,
      timestamp: new Date().toISOString(),
    };
  } catch (err) {
    clearTimeout(timeoutId);
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      data: null,
      error: message.includes("aborted") ? "Request timeout" : message,
      source,
      timestamp: new Date().toISOString(),
    };
  }
}

// =================================================================================
// REAL WEATHER DATA (Open-Meteo - No API Key)
// =================================================================================

interface OpenMeteoResponse {
  latitude: number;
  longitude: number;
  current: {
    temperature_2m: number;
    relative_humidity_2m: number;
    apparent_temperature: number;
    precipitation: number;
    wind_speed_10m: number;
    wind_direction_10m: number;
    surface_pressure: number;
  };
  current_units: Record<string, string>;
}

export async function getRealWeatherData(
  lat: number = 52.52,
  lon: number = 13.41,
) {
  const url = `${PUBLIC_APIS.OPEN_METEO}?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure&timezone=auto`;

  const result = await safeFetch<OpenMeteoResponse>(url, "open-meteo");

  if (!result.success || !result.data) {
    return {
      status: "no_data",
      reason: result.error || "Weather data unavailable",
      source: "open-meteo",
      location: { lat, lon },
      timestamp: result.timestamp,
    };
  }

  const current = result.data.current;
  return {
    status: "real_data",
    source: "open-meteo",
    location: {
      latitude: result.data.latitude,
      longitude: result.data.longitude,
    },
    sensors: {
      temperature_c: current.temperature_2m,
      humidity_percent: current.relative_humidity_2m,
      feels_like_c: current.apparent_temperature,
      precipitation_mm: current.precipitation,
      wind_speed_kmh: current.wind_speed_10m,
      wind_direction_deg: current.wind_direction_10m,
      pressure_hpa: current.surface_pressure,
    },
    units: result.data.current_units,
    data_quality: "verified_real",
    timestamp: result.timestamp,
  };
}

// =================================================================================
// REAL EARTHQUAKE DATA (USGS - No API Key)
// =================================================================================

interface USGSEarthquake {
  type: string;
  features: Array<{
    properties: {
      mag: number;
      place: string;
      time: number;
      updated: number;
      type: string;
      title: string;
      status: string;
    };
    geometry: {
      coordinates: [number, number, number];
    };
  }>;
  metadata: {
    generated: number;
    url: string;
    title: string;
    count: number;
  };
}

export async function getRealEarthquakeData(
  period: "hour" | "day" | "week" = "day",
  minMagnitude: "significant" | "all_4.5" | "all_2.5" | "all_1.0" = "all_4.5",
) {
  const url = `${PUBLIC_APIS.USGS_EARTHQUAKES}/${minMagnitude}_${period}.geojson`;

  const result = await safeFetch<USGSEarthquake>(url, "usgs-earthquakes");

  if (!result.success || !result.data) {
    return {
      status: "no_data",
      reason: result.error || "Earthquake data unavailable",
      source: "usgs",
      period,
      timestamp: result.timestamp,
    };
  }

  const earthquakes = result.data.features.slice(0, 20).map((eq) => ({
    magnitude: eq.properties.mag,
    location: eq.properties.place,
    coordinates: {
      longitude: eq.geometry.coordinates[0],
      latitude: eq.geometry.coordinates[1],
      depth_km: eq.geometry.coordinates[2],
    },
    time: new Date(eq.properties.time).toISOString(),
    type: eq.properties.type,
    status: eq.properties.status,
  }));

  return {
    status: "real_data",
    source: "usgs-earthquakes",
    period,
    total_count: result.data.metadata.count,
    returned_count: earthquakes.length,
    events: earthquakes,
    metadata: {
      title: result.data.metadata.title,
      generated: new Date(result.data.metadata.generated).toISOString(),
    },
    data_quality: "verified_real",
    timestamp: result.timestamp,
  };
}

// =================================================================================
// REAL ISS SATELLITE LOCATION (Open-Notify - No API Key)
// =================================================================================

interface ISSResponse {
  message: string;
  iss_position: {
    latitude: string;
    longitude: string;
  };
  timestamp: number;
}

export async function getRealISSLocation() {
  const result = await safeFetch<ISSResponse>(
    PUBLIC_APIS.ISS_LOCATION,
    "open-notify-iss",
  );

  if (!result.success || !result.data || result.data.message !== "success") {
    return {
      status: "no_data",
      reason: result.error || "ISS location unavailable",
      source: "open-notify",
      timestamp: result.timestamp,
    };
  }

  return {
    status: "real_data",
    source: "open-notify",
    satellite: "International Space Station",
    position: {
      latitude: parseFloat(result.data.iss_position.latitude),
      longitude: parseFloat(result.data.iss_position.longitude),
    },
    unix_timestamp: result.data.timestamp,
    orbital_info: {
      altitude_km: 408, // Average ISS altitude
      velocity_kmh: 27600, // Average ISS velocity
      orbit_period_min: 92,
    },
    data_quality: "verified_real",
    timestamp: result.timestamp,
  };
}

// =================================================================================
// REAL CRYPTO PRICES (CoinGecko - Free, Rate Limited)
// =================================================================================

interface CoinGeckoPrice {
  [coin: string]: {
    usd: number;
    usd_24h_change: number;
    last_updated_at: number;
  };
}

export async function getRealCryptoPrices(
  coins: string[] = ["bitcoin", "ethereum"],
) {
  const coinList = coins.join(",");
  const url = `${PUBLIC_APIS.COINGECKO}/simple/price?ids=${coinList}&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true`;

  const result = await safeFetch<CoinGeckoPrice>(url, "coingecko");

  if (!result.success || !result.data) {
    return {
      status: "no_data",
      reason: result.error || "Crypto prices unavailable",
      source: "coingecko",
      requested_coins: coins,
      timestamp: result.timestamp,
    };
  }

  const prices = Object.entries(result.data).map(([coin, data]) => ({
    coin,
    price_usd: data.usd,
    change_24h_percent: Number(data.usd_24h_change?.toFixed(2) || 0),
    last_updated: new Date(data.last_updated_at * 1000).toISOString(),
  }));

  return {
    status: "real_data",
    source: "coingecko",
    prices,
    data_quality: "verified_real",
    timestamp: result.timestamp,
  };
}

// =================================================================================
// REAL IoT SENSOR DATA (ThingSpeak Public Channels)
// =================================================================================

interface ThingSpeakFeed {
  channel: {
    id: number;
    name: string;
    description: string;
    latitude: string;
    longitude: string;
    created_at: string;
    updated_at: string;
    last_entry_id: number;
  };
  feeds: Array<{
    created_at: string;
    entry_id: number;
    field1?: string;
    field2?: string;
    field3?: string;
    field4?: string;
    field5?: string;
  }>;
}

export async function getRealIoTSensorData(
  channelId: string = "12397",
  results: number = 10,
) {
  const url = `${PUBLIC_APIS.THINGSPEAK_PUBLIC}/${channelId}/feeds.json?results=${results}`;

  const result = await safeFetch<ThingSpeakFeed>(url, "thingspeak");

  if (!result.success || !result.data) {
    return {
      status: "no_data",
      reason: result.error || "IoT sensor data unavailable",
      source: "thingspeak",
      channel_id: channelId,
      timestamp: result.timestamp,
    };
  }

  const channel = result.data.channel;
  const feeds = result.data.feeds
    .map((feed) => ({
      entry_id: feed.entry_id,
      timestamp: feed.created_at,
      readings: {
        field1: feed.field1 ? parseFloat(feed.field1) : null,
        field2: feed.field2 ? parseFloat(feed.field2) : null,
        field3: feed.field3 ? parseFloat(feed.field3) : null,
        field4: feed.field4 ? parseFloat(feed.field4) : null,
        field5: feed.field5 ? parseFloat(feed.field5) : null,
      },
    }))
    .filter((f) => Object.values(f.readings).some((v) => v !== null));

  if (feeds.length === 0) {
    return {
      status: "no_data",
      reason: "Channel has no recent sensor readings",
      source: "thingspeak",
      channel: {
        id: channel.id,
        name: channel.name,
      },
      timestamp: result.timestamp,
    };
  }

  return {
    status: "real_data",
    source: "thingspeak",
    channel: {
      id: channel.id,
      name: channel.name,
      description: channel.description,
      location: {
        latitude: channel.latitude ? parseFloat(channel.latitude) : null,
        longitude: channel.longitude ? parseFloat(channel.longitude) : null,
      },
      last_entry_id: channel.last_entry_id,
      updated_at: channel.updated_at,
    },
    sensor_readings: feeds,
    reading_count: feeds.length,
    data_quality: "verified_real",
    timestamp: result.timestamp,
  };
}

// =================================================================================
// AGGREGATED REAL SENSOR DASHBOARD
// =================================================================================

export async function getAllRealSensorData() {
  const startTime = Date.now();

  // Fetch all data sources in parallel
  const [weather, earthquakes, iss, cryptoData, iot] = await Promise.all([
    getRealWeatherData(),
    getRealEarthquakeData("day", "all_4.5"),
    getRealISSLocation(),
    getRealCryptoPrices(["bitcoin", "ethereum", "solana"]),
    getRealIoTSensorData(),
  ]);

  const fetchTime = Date.now() - startTime;

  // Count successful data sources
  const sources = [weather, earthquakes, iss, cryptoData, iot];
  const successCount = sources.filter((s) => s.status === "real_data").length;
  const failedCount = sources.filter((s) => s.status === "no_data").length;

  return {
    dashboard_id: crypto.randomUUID(),
    data_sources: {
      weather,
      earthquakes,
      satellite_tracking: iss,
      crypto_markets: cryptoData,
      iot_sensors: iot,
    },
    summary: {
      total_sources: sources.length,
      successful: successCount,
      unavailable: failedCount,
      success_rate_percent: Number(
        ((successCount / sources.length) * 100).toFixed(1),
      ),
      fetch_time_ms: fetchTime,
    },
    data_policy: "REAL_DATA_ONLY_NO_MOCK",
    timestamp: new Date().toISOString(),
  };
}

// =================================================================================
// AVAILABLE PUBLIC SENSOR CHANNELS
// =================================================================================

export function getAvailablePublicChannels() {
  return {
    status: "info",
    available_channels: PUBLIC_THINGSPEAK_CHANNELS.map((ch) => ({
      channel_id: ch.id,
      name: ch.name,
      expected_fields: ch.fields,
      api_url: `${PUBLIC_APIS.THINGSPEAK_PUBLIC}/${ch.id}/feeds.json`,
    })),
    data_sources: [
      {
        name: "Open-Meteo Weather",
        description: "Real-time weather from any location",
        requires_key: false,
      },
      {
        name: "USGS Earthquakes",
        description: "Real-time seismic activity worldwide",
        requires_key: false,
      },
      {
        name: "ISS Location",
        description: "Real-time International Space Station position",
        requires_key: false,
      },
      {
        name: "CoinGecko Crypto",
        description: "Real-time cryptocurrency prices",
        requires_key: false,
      },
      {
        name: "ThingSpeak IoT",
        description: "Public IoT sensor channels",
        requires_key: false,
      },
    ],
    data_policy: {
      mock_data: "NEVER",
      fake_data: "NEVER",
      no_data_behavior: "Return status: no_data with reason",
    },
    timestamp: new Date().toISOString(),
  };
}

