# 🔗 HYBRID BIOMETRIC SYSTEM - DOKUMENTIM KOMPLET

## Përmbledhje

Sistemi **Hybrid Biometric** lejon:
1. **Telefon** - Mbërthen sensorët nativik (accelerometer, gyroscope, heart rate, temperature)
2. **Klinika/Spitale** - Integrohet me aparate profesionale (EEG, ECG, SpO2, pulse, pressure)
3. **Dashboard Unified** - Shfaq të dy burimet në kohë reale

---

## 🏗️ ARKITEKTURA

```
┌─────────────────┐                    ┌──────────────────┐
│   USER PHONE    │                    │  CLINIC/HOSPITAL │
│   📱 Sensors    │                    │  🏥 Devices      │
│ • Accelerometer │                    │ • EEG            │
│ • Gyroscope     │                    │ • ECG            │
│ • Heart Rate    │────────┬───────────┤ • SpO2           │
│ • Temperature   │        │           │ • Blood Pressure │
│ • Proximity     │        │           │ • Temperature    │
└─────────────────┘        │           │ • Spirometer     │
                           │           └──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   HYBRID    │
                    │ BIOMETRIC   │
                    │    API      │ (Hybrid Biometric API v1.0)
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐        ┌───▼────┐        ┌───▼────┐
    │  Cloud │        │  Clinic│        │ Local  │
    │ Storage│        │ Server │        │ Phone  │
    └────────┘        └────────┘        └────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  DASHBOARD  │
                    │   UNIFIED   │
                    │ 🔗 Hybrid   │
                    │   Monitor   │
                    └─────────────┘
```

---

## 📦 KOMPONENTA KRYESORE

### 1. **Mobile Hybrid SDK** (`sdk/mobile-hybrid-sdk.ts`)

Mbërthen gjithçka për telefonin:

```typescript
import {
  PhoneSensorCollector,
  ClinicDeviceIntegration,
  HybridBiometricSessionManager,
  initializeHybridSystem,
} from '@/sdk/mobile-hybrid-sdk';

// Inicijalizim
const { phoneCollector, sessionManager } = await initializeHybridSystem({
  clinicConfig: {
    clinicId: 'clinic_001',
    clinicName: 'UniversityClinc',
    apiEndpoint: 'https://clinic-api.example.com',
    apiKey: 'your-clinic-api-key',
    supportedDevices: ['EEG', 'ECG', 'SpO2'],
  },
});

// Fillo sesion hibrid
const session = await sessionManager.startSession(userId, 'hybrid');

// Mbyll sesion
const finishedSession = await sessionManager.stopSession();

// Sinkronizo në cloud
await sessionManager.syncToCloud('https://api.example.com', authToken);
```

---

### 2. **Backend API** (`apps/api/hybrid_biometric_api.py`)

FastAPI backend për menaxhim të të dhënave:

#### **A. Phone Sensor Endpoints**

```bash
# Dërgim lexim sensori
POST /api/phone/sensor-reading
{
  "accelerometer": {"x": 0.5, "y": 1.2, "z": 9.8, "timestamp": 1673500000000},
  "gyroscope": {"x": 10, "y": 5, "z": 2, "timestamp": 1673500000000},
  "heart_rate": {"bpm": 72, "confidence": 0.85, "timestamp": 1673500000000},
  "temperature": {"celsius": 36.8, "timestamp": 1673500000000},
  "session_id": "session_user123_1673500000000",
  "user_id": "user123"
}

Response:
{
  "status": "received",
  "session_id": "session_user123_1673500000000",
  "reading_count": 150
}

# Merrni sesionin e telefonit
GET /api/phone/session/{session_id}

# Merrni sesionet aktive
GET /api/phone/active-sessions?user_id=user123
```

#### **B. Clinical Device Endpoints**

```bash
# Regjistrim aparati klinike
POST /api/clinic/device/register
{
  "device_type": "EEG",
  "device_id": "eeg_001",
  "device_name": "Emotiv EPOC+ EEG Headset",
  "clinic_id": "clinic_001",
  "api_key": "secure_key_here",
  "supported_channels": 14,
  "sample_rate": 256
}

Response:
{
  "status": "registered",
  "device_id": "eeg_001",
  "message": "Device EEG registered successfully"
}

# Dërgim lexim klinike
POST /api/clinic/device/{device_id}/reading
{
  "device_type": "EEG",
  "device_id": "eeg_001",
  "device_name": "Emotiv EPOC+",
  "clinic_id": "clinic_001",
  "value": [50.5, 48.2, 52.1, 49.8, ...],
  "unit": "μV",
  "quality": 95,
  "timestamp": 1673500000000,
  "metadata": {"channels": 14, "electrode": "AF3-F3"}
}

# Merrni leximin e fundit
GET /api/clinic/device/{device_id}/latest

# Merrni të gjitha leximet e klinikës
GET /api/clinic/readings/{clinic_id}?device_type=EEG
```

#### **C. Hybrid Session Endpoints**

```bash
# Fillo sesion hibrid
POST /api/session/start-hybrid
{
  "user_id": "user123",
  "clinic_id": "clinic_001",
  "data_source": "hybrid"  // "phone" | "clinic" | "hybrid"
}

Response:
{
  "session": {
    "session_id": "session_user123_1673500000000",
    "user_id": "user123",
    "clinic_id": "clinic_001",
    "start_time": 1673500000000,
    "data_source": "hybrid",
    "sync_status": "local"
  },
  "status": "started"
}

# Mbyll sesion
POST /api/session/{session_id}/stop

# Merrni detajet e sesionit
GET /api/session/{session_id}

# Merrni të gjitha sesionet e përdoruesit
GET /api/user/{user_id}/sessions
```

#### **D. Analytics Endpoints**

```bash
# Analiza sesioni
GET /api/analytics/session/{session_id}

Response:
{
  "session_id": "session_user123_1673500000000",
  "duration_ms": 600000,
  "heart_rate": {
    "avg": 72.5,
    "min": 60,
    "max": 95
  },
  "temperature": {
    "avg": 36.8,
    "min": 36.5,
    "max": 37.2
  },
  "readings_count": 600
}

# Analiza klinike
GET /api/clinic/{clinic_id}/analytics
```

#### **E. WebSocket Real-Time Streaming**

```typescript
// Client
const ws = new WebSocket('wss://api.example.com/ws/clinic/clinic_001/stream');

ws.onmessage = (event) => {
  const reading = JSON.parse(event.data);
  console.log('🏥 Clinical reading:', reading);
  // {
  //   "type": "clinical_reading",
  //   "device_id": "eeg_001",
  //   "device_type": "EEG",
  //   "value": [50.5, 48.2, ...],
  //   "unit": "μV",
  //   "quality": 95,
  //   "timestamp": 1673500000000
  // }
};
```

---

## 📱 TELEFON - SENSORË I PËRSHTSHËM

### Sensorët e Mbështetur:

1. **Accelerometer** - Lëvizja fizike (m/s²)
2. **Gyroscope** - Rrotullimi (deg/s)
3. **Heart Rate Sensor** - PPG ose sensor i built-in
4. **Temperature Sensor** - ThermalManager (Android) ose simulim
5. **Proximity** - Distanca në cm

### Shembull i Përdorimit:

```typescript
import { PhoneSensorCollector } from '@/sdk/mobile-hybrid-sdk';

const collector = new PhoneSensorCollector();

// Fillo dëgjimin
await collector.startListening({
  sampleRate: 100,  // Hz
  bufferSize: 1000, // samples
});

// Merrni të dhënat aktuale
const currentData = await collector.getCurrentData();
console.log(currentData);
// {
//   accelerometer: {x: 0.5, y: 1.2, z: 9.8, timestamp: ...},
//   gyroscope: {x: 10, y: 5, z: 2, timestamp: ...},
//   heartRate: {bpm: 72, confidence: 0.85, timestamp: ...},
//   temperature: {celsius: 36.8, timestamp: ...}
// }

// Merrni buffer-in
const bufferedData = collector.getBufferedData();

// Ndaloni dëgjimin
collector.stopListening();
```

---

## 🏥 KLINIKA - INTEGRIMI I APARATEVE

### Aparate të Mbështurura:

| Device Type | Shembull | Parametrat | Unit |
|------------|---------|-----------|------|
| **EEG** | Emotiv EPOC+ | 14 channels | μV |
| **ECG** | Polar H10 | Heart activity | mV |
| **SpO2** | Pulse Oximeter | Oxygen saturation | % |
| **Blood Pressure** | Omron | Systolic/Diastolic | mmHg |
| **Temperature** | Digital probe | Body temp | °C |
| **Spirometer** | MGC Ultima | Lung capacity | L |

### Setup - Integrimi i Klinikës:

```python
# Backend setup
from apps.api.hybrid_biometric_api import app, ClinicIntegrationConfig

# 1. Register clinic
clinic_config = ClinicIntegrationConfig(
    clinic_id="clinic_001",
    clinic_name="University Clinic",
    api_endpoint="https://clinic-api.example.com",
    api_key="secure_key",
    supported_devices=["EEG", "ECG", "SpO2", "BloodPressure"],
    ws_url="wss://clinic-api.example.com/ws",
    sync_interval=5000,
)

# 2. Register EEG device
eeg_device = ClinicalDeviceRegistration(
    device_type=DeviceType.EEG,
    device_id="eeg_001",
    device_name="Emotiv EPOC+ EEG Headset",
    clinic_id="clinic_001",
    api_key="device_key",
    supported_channels=14,
    sample_rate=256,
)

# 3. Send readings
clinical_reading = ClinicalDeviceReading(
    device_type=DeviceType.EEG,
    device_id="eeg_001",
    device_name="Emotiv EPOC+",
    clinic_id="clinic_001",
    value=[50.5, 48.2, 52.1, 49.8, 51.3, 50.8, 49.5, 51.2, 50.1, 49.9, 52.3, 50.5, 51.1, 49.7],
    unit="μV",
    quality=95,
    timestamp=int(time.time() * 1000),
    metadata={"channels": 14, "sample_rate": 256},
)
```

---

## 🖥️ DASHBOARD HIBRID

Location: `/apps/web/app/modules/hybrid-biometric-dashboard/page.tsx`

### Karakteristika:

✅ **Real-time Monitoring**
- Live heart rate chart
- Live temperature chart
- Live movement/acceleration data

✅ **Dual Data Sources**
- Phone sensors (left side)
- Clinical devices (right side)
- Combined analysis

✅ **Session Management**
- Start/Stop sessions
- Select data source (phone/clinic/hybrid)
- Session statistics

✅ **Quality Indicators**
- Data quality scores (0-100%)
- Connection status
- Sync status

✅ **Analytics**
- Min/Max/Avg calculations
- Duration tracking
- Readings count

---

## 🔐 SIGURIA

### Authentication Flow:

```
1. Clinic registers with API key
2. Phone app gets auth token
3. Clinical device gets device key
4. All requests signed with token/key
5. Data encrypted in transit (HTTPS/WSS)
6. CORS protection enabled
```

### Example - Clinic Authorization:

```python
# Clinic authentication
@app.post("/auth/token")
async def get_clinic_token(clinic_id: str, timestamp: int, signature: str):
    # Verify clinic credentials
    if verify_clinic_signature(clinic_id, signature):
        token = generate_jwt_token(clinic_id)
        return {"token": token, "expires_in": 3600}
    raise HTTPException(status_code=401)

# Device authorization
@app.post("/api/clinic/device/register")
async def register_clinic_device(device: ClinicalDeviceRegistration):
    # Verify device key
    if not verify_device_key(device.clinic_id, device.api_key):
        raise HTTPException(status_code=401)
    # Register device
    ...
```

---

## 🚀 DEPLOYMENT

### Local Development:

```bash
# 1. Install dependencies
pip install fastapi uvicorn pydantic

# 2. Run API
python apps/api/hybrid_biometric_api.py
# API runs on: http://localhost:8001

# 3. Dashboard available at:
# http://localhost:3000/modules/hybrid-biometric-dashboard
```

### Production (Hetzner):

```bash
# 1. Copy files to server
scp -r apps/api/hybrid_biometric_api.py root@server:/opt/kloud/apps/api/

# 2. Update docker-compose.yml
hybrid-api:
  build:
    context: ./apps/api
    dockerfile: Dockerfile.hybrid
  ports:
    - "8001:8000"
  environment:
    - API_ENDPOINT=https://api.kloud.com
    - WS_URL=wss://api.kloud.com/ws
  volumes:
    - ./data/hybrid:/data

# 3. Start service
docker compose up -d hybrid-api
```

---

## 📊 PËRVOJAT - USE CASES

### Scenario 1: Home Monitoring
```
User (Patient) telah
├─ Phone sensors
│  ├─ Heart rate (PPG camera)
│  ├─ Temperature (built-in)
│  └─ Movement (accelerometer)
└─ Cloud sync every 5 min

Doctor checks dashboard remotely
```

### Scenario 2: Clinic Session
```
Patient in clinic
├─ Phone sensors + Clinic EEG/ECG
│  ├─ Real-time EEG (14 channels)
│  ├─ ECG (1 channel)
│  ├─ SpO2 (pulse oximetry)
│  └─ Phone movement + HR
└─ Local clinic server + cloud backup

Doctor analyzes hybrid data
```

### Scenario 3: Athletic Training
```
Athlete with wearable + phone
├─ Heart rate variability (HRV)
├─ VO2 estimation
├─ Acceleration patterns
└─ Real-time feedback

Coach monitors performance
```

---

## 🔗 INTEGRIMI ME KLINIKE

### Links i OpenSource për EEG:

1. **OpenBCI** - https://openbci.com/
   - Open-source EEG boards
   - API i mirë dokumentuar
   - Community support

2. **BrainFlow** - https://brainflow.readthedocs.io/
   - Multi-device support
   - Python SDK
   - 20+ device support

3. **MNE-Python** - https://mne.tools/
   - Neuroscience data analysis
   - Real-time processing
   - Signal filtering

### Klinike të Njohura me Integrim:

- **UniversityClinics** - EEG + ECG
- **NeuroLabs** - Advanced EEG
- **Sleep Clinics** - Sleep stage monitoring
- **Cardiac Centers** - ECG/SpO2

---

## 📈 METRIKA I MONITORUAR

### Phone Sensors:
- Heart Rate Variability (HRV)
- Movement patterns
- Temperature fluctuations
- Proximity events

### Clinical Devices:
- EEG power bands (alpha, beta, gamma, delta, theta)
- ECG intervals (QRS, PR)
- SpO2 trends
- Blood pressure patterns

### Combined Analytics:
- Correlation analysis
- Anomaly detection
- Stress indicators
- Sleep quality estimation

---

## ✅ CHECKLIST IMPLEMENTIM

- [ ] Backend API i deployuar
- [ ] Mobile SDK integruar
- [ ] Dashboard working
- [ ] Phone sensors collecting data
- [ ] Clinic devices registered
- [ ] Real-time streaming active
- [ ] Analytics endpoint working
- [ ] Cloud sync working
- [ ] Security configured
- [ ] Documentation complete

---

## 📞 SUPPORT

For issues or integration help:
- GitHub: https://github.com/LedjanAhmati/Kloud-cloud
- Email: support@kloud.com
- Docs: https://kloud-docs.example.com

---

**Sistema e Plotë Hybrid Biometric ready! 🚀**

