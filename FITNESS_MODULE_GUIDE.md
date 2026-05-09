# Kloud Cloud Fitness Training Module

## Overview

The Fitness Training Module is an enterprise-grade personalized fitness coaching system built on the Kloud Cloud platform. It combines real-time biometric tracking, AI-powered form analysis, and adaptive music generation to deliver personalized workout experiences.

### Key Features

- **👤 User Profiles**: Comprehensive fitness profiles with biometric baselines
- **❤️ Real-time Biometric Tracking**: Heart rate, calories, respiration, blood pressure monitoring
- **😊 Emotional State Detection**: Camera-based pupil tracking for emotion recognition
- **🎥 AI Form Analysis**: MediaPipe-based pose estimation for real-time form correction
- **🤖 Coaching Engine**: Personalized exercise guidance and form feedback
- **🎵 Adaptive Music**: Tempo-adjusted MIDI generation based on workout intensity
- **📊 Analytics Dashboard**: Progress tracking, streaks, personal records
- **⚡ Stress & Recovery**: Stress level detection and recovery recommendations

---

## Architecture

### Core Components

...
┌─────────────────────────────────────────────────────────────┐
│                     Kloud Cloud                          │
│                   Fitness Module v1.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Biometric    │  │ Coaching     │  │ Adaptive     │       │
│  │ Tracker      │  │ Engine       │  │ Music        │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                  │                │
│  ┌──────────────────────────────────────────────────┐        │
│  │        FastAPI Routes (fitness_routes.py)        │        │
│  └──────────────────────────────────────────────────┘        │
│         │                 │                  │                │
│  ┌──────────────────────────────────────────────────┐        │
│  │   SQLAlchemy ORM Models (fitness_models.py)      │        │
│  └──────────────────────────────────────────────────┘        │
│         │                                                     │
│  ┌──────────────────────────────────────────────────┐        │
│  │   PostgreSQL Database                            │        │
│  │   - fitness_users                                │        │
│  │   - workouts                                      │        │
│  │   - exercises                                     │        │
│  │   - biometric_data                               │        │
│  │   - coaching_sessions                            │        │
│  │   - user_achievements                            │        │
│  │   - fitness_stats                                │        │
│  └──────────────────────────────────────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
...

### Database Schema

#### FitnessUser

Main user profile with personal and fitness information.

```python
{
    "id": "uuid",                     # Primary key
    "user_id": "user_email",          # Reference to main user
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "height_cm": 180,
    "weight_kg": 80,
    "fitness_level": "intermediate",  # beginner|intermediate|advanced|elite
    "primary_goal": "muscle_gain",    # weight_loss|muscle_gain|endurance|etc
    "resting_heart_rate": 60,         # BPM at rest
    "max_heart_rate": 190,            # Estimated or measured
    "preferred_intensity": "moderate", # low|moderate|high|hiit
    "workout_duration_minutes": 45,
    "workouts_per_week": 3,
    "camera_enabled": true,           # For emotion detection
    "linked_wearables": {
        "apple_watch": "device_id_123",
        "fitbit": "device_id_456"
    },
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### Workout

Individual workout session.

```python
{
    "id": "uuid",
    "user_id": "uuid",
    "name": "Morning HIIT",
    "workout_type": "cardio",         # cardio|strength|flexibility|etc
    "intensity": "high",              # low|moderate|high|hiit
    "started_at": "2024-01-15T06:00:00Z",
    "ended_at": "2024-01-15T06:45:00Z",
    "duration_minutes": 45,
    "total_calories_burned": 450.5,
    "average_heart_rate": 155,
    "max_heart_rate": 178,
    "min_heart_rate": 120,
    "mood_before": "neutral",
    "mood_after": "excellent",
    "energy_before": 6,               # 1-10 scale
    "energy_after": 3,
    "ai_feedback": "Great form! Keep working on breathing consistency.",
    "adaptive_music_bpm": 145,        # Beats per minute of music
    "completed": true
}
```

#### Exercise

Individual exercise within a workout.

```python
{
    "id": "uuid",
    "workout_id": "uuid",
    "name": "Push-ups",
    "exercise_type": "strength",
    "muscle_groups": ["chest", "triceps", "shoulders"],
    "sets": 3,
    "reps": 12,
    "weight_kg": null,
    "duration_seconds": 180,
    "form_score": 87.5,               # 0-100 scale
    "form_issues": [
        "Hips sagging slightly",
        "Inconsistent range of motion"
    ],
    "recommended_form_corrections": [
        "Engage core more",
        "Lower to full chest contact"
    ],
    "pose_detection_data": {          # MediaPipe output
        "shoulder": {"x": 0.5, "y": 0.3, "z": 0.0},
        "elbow": {"x": 0.6, "y": 0.4, "z": 0.1},
        ...
    },
    "audio_coaching": "Great form! Keep your elbows closer!"
}
```

#### BiometricData

Real-time biometric measurements.

```python
{
    "id": "uuid",
    "user_id": "uuid",
    "biometric_type": "heart_rate",   # heart_rate|calories|emotional_state|etc
    "value": 155,                     # Numeric value
    "unit": "bpm",                    # beats per minute, kcal, %, mmHg, etc
    "measurement_time": "2024-01-15T06:15:30Z",
    "context": "workout",             # rest|workout|recovery|sleep
    "device_type": "smartwatch",      # phone|smartwatch|chest_strap|etc
    "device_id": "watch_123",
    "confidence_score": 0.95          # 0-1 scale
}
```

#### FitnessStats

Aggregated statistics (updated periodically).

```python
{
    "id": "uuid",
    "user_id": "uuid",
    "total_workouts": 52,
    "total_workout_hours": 39.5,
    "total_calories_burned": 18750,
    "total_distance_km": 245.8,
    "total_steps": 425000,
    "current_workout_streak": 8,      # consecutive days
    "longest_workout_streak": 23,
    "avg_workout_duration_minutes": 45.5,
    "avg_heart_rate": 142,
    "avg_calories_per_workout": 360.5,
    "max_heart_rate_recorded": 189,
    "longest_workout_minutes": 87,
    "weekly_improvement_percent": 5.2,
    "monthly_improvement_percent": 12.8,
    "form_accuracy_trend": 3.5        # Improvement/decline trend
}
```

---

## API Endpoints

### User Profile Management

#### Create User Profile

```http
POST /fitness/users/profile
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "gender": "M",
    "height_cm": 180,
    "weight_kg": 80,
    "fitness_level": "intermediate",
    "primary_goal": "muscle_gain",
    "secondary_goals": ["strength", "endurance"],
    "resting_heart_rate": 60,
    "workout_duration_minutes": 45,
    "workouts_per_week": 3
}

Response: 201 Created
{
    "success": true,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "fitness_level": "intermediate",
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### Get User Profile

```http
GET /fitness/users/{user_id}/profile

Response: 200 OK
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "weight_kg": 80,
    "fitness_level": "intermediate",
    "primary_goal": "muscle_gain",
    "resting_heart_rate": 60,
    "max_heart_rate": 190,
    "workout_duration_minutes": 45,
    "workouts_per_week": 3,
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### Update User Profile

```http
PUT /fitness/users/{user_id}/profile
Content-Type: application/json

{
    "weight_kg": 78,
    "resting_heart_rate": 58,
    "fitness_level": "advanced",
    "primary_goal": "strength"
}

Response: 200 OK
{
    "success": true,
    "message": "Profile updated",
    "updated_at": "2024-01-15T11:30:00Z"
}
```

### Workout Management

#### Start Workout

```http
POST /fitness/users/{user_id}/workouts
Content-Type: application/json

{
    "name": "Morning HIIT",
    "workout_type": "cardio",
    "intensity": "high",
    "description": "High-intensity interval training session"
}

Response: 201 Created
{
    "success": true,
    "workout_id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Morning HIIT",
    "type": "cardio",
    "intensity": "high",
    "started_at": "2024-01-15T06:00:00Z"
}
```

#### Get Workouts

```http
GET /fitness/users/{user_id}/workouts?limit=10

Response: 200 OK
[
    {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Morning HIIT",
        "type": "cardio",
        "intensity": "high",
        "started_at": "2024-01-15T06:00:00Z",
        "ended_at": "2024-01-15T06:45:00Z",
        "duration_minutes": 45,
        "total_calories_burned": 450.5,
        "average_heart_rate": 155,
        "completed": true
    },
    ...
]
```

#### Get Workout Details

```http
GET /fitness/workouts/{workout_id}

Response: 200 OK
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Morning HIIT",
    "type": "cardio",
    "intensity": "high",
    "started_at": "2024-01-15T06:00:00Z",
    "ended_at": "2024-01-15T06:45:00Z",
    "duration_minutes": 45,
    "total_calories_burned": 450.5,
    "average_heart_rate": 155,
    "max_heart_rate": 178,
    "min_heart_rate": 120,
    "mood_before": "neutral",
    "mood_after": "excellent",
    "energy_before": 6,
    "energy_after": 3,
    "ai_feedback": "Great form! Keep working on breathing consistency.",
    "completed": true,
    "exercises_count": 5,
    "exercises": [...]
}
```

#### End Workout

```http
PUT /fitness/workouts/{workout_id}/end
Content-Type: application/json

{
    "mood_after": "excellent",
    "energy_after": 3,
    "pain_level": 2,
    "notes": "Great session! Felt strong today.",
    "ai_feedback": "Outstanding performance!",
    "completed": true
}

Response: 200 OK
{
    "success": true,
    "message": "Workout ended",
    "workout_id": "660e8400-e29b-41d4-a716-446655440001",
    "duration_minutes": 45,
    "ended_at": "2024-01-15T06:45:00Z"
}
```

### Exercise Tracking

#### Add Exercise to Workout

```http
POST /fitness/workouts/{workout_id}/exercises
Content-Type: application/json

{
    "name": "Push-ups",
    "exercise_type": "strength",
    "muscle_groups": ["chest", "triceps", "shoulders"],
    "sets": 3,
    "reps": 12,
    "duration_seconds": 180
}

Response: 201 Created
{
    "success": true,
    "exercise_id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Push-ups",
    "type": "strength",
    "started_at": "2024-01-15T06:05:00Z"
}
```

### Biometric Tracking

#### Record Biometric

```http
POST /fitness/users/{user_id}/biometrics
Content-Type: application/json

{
    "biometric_type": "heart_rate",
    "value": 155,
    "unit": "bpm",
    "device_type": "smartwatch",
    "context": "workout"
}

Response: 201 Created
{
    "success": true,
    "biometric_id": "880e8400-e29b-41d4-a716-446655440003",
    "type": "heart_rate",
    "value": 155,
    "unit": "bpm",
    "recorded_at": "2024-01-15T06:15:30Z"
}
```

#### Get Biometrics

```http
GET /fitness/users/{user_id}/biometrics?biometric_type=heart_rate&limit=100

Response: 200 OK
[
    {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "type": "heart_rate",
        "value": 155,
        "unit": "bpm",
        "device_type": "smartwatch",
        "context": "workout",
        "measured_at": "2024-01-15T06:15:30Z"
    },
    ...
]
```

### AI Coaching

#### Analyze Exercise Form (Pose Analysis)

```http
POST /fitness/analyze/pose
Content-Type: application/json

{
    "exercise_name": "push_up",
    "pose_landmarks": {
        "shoulder": {"x": 0.5, "y": 0.3, "z": 0.0},
        "elbow": {"x": 0.6, "y": 0.4, "z": 0.1},
        "hip": {"x": 0.5, "y": 0.6, "z": 0.0},
        "knee": {"x": 0.5, "y": 0.75, "z": 0.0},
        "wrist": {"x": 0.65, "y": 0.35, "z": 0.0}
    },
    "confidence_scores": {
        "shoulder": 0.95,
        "elbow": 0.92,
        "hip": 0.88,
        "knee": 0.85,
        "wrist": 0.90
    }
}

Response: 200 OK
{
    "exercise": "push_up",
    "form_score": 87.5,
    "issues": [
        "Hips sagging - engage core",
        "Insufficient range of motion"
    ],
    "recommendations": [
        "Engage your core to prevent hip sagging",
        "Lower until chest nearly touches ground",
        "Keep elbows at ~45° from your body"
    ],
    "timestamp": "2024-01-15T06:15:35Z"
}
```

#### Detect Emotional State

```http
POST /fitness/analyze/emotional-state
Content-Type: application/json

{
    "pupil_size": 5.2,
    "pupil_dilation_rate": 0.15,
    "blink_rate": 18,
    "eye_gaze_stability": 75,
    "heart_rate": 145
}

Response: 200 OK
{
    "emotional_state": "focused",
    "confidence": 0.85,
    "timestamp": "2024-01-15T06:15:40Z"
}
```

#### Detect Stress Level

```http
POST /fitness/analyze/stress-level
Content-Type: application/json

{
    "heart_rate": 155,
    "heart_rate_variability": 35,
    "pupil_dilation_rate": 0.25,
    "respiratory_rate": 22
}

Response: 200 OK
{
    "stress_level": 62,
    "interpretation": "Stressed",
    "timestamp": "2024-01-15T06:15:45Z"
}
```

### Statistics

#### Get User Statistics

```http
GET /fitness/users/{user_id}/stats

Response: 200 OK
{
    "total_workouts": 52,
    "total_workout_hours": 39.5,
    "total_calories_burned": 18750,
    "total_distance_km": 245.8,
    "total_steps": 425000,
    "current_workout_streak": 8,
    "longest_workout_streak": 23,
    "avg_workout_duration_minutes": 45.5,
    "avg_heart_rate": 142,
    "avg_calories_per_workout": 360.5,
    "max_heart_rate_recorded": 189,
    "longest_workout_minutes": 87,
    "weekly_improvement_percent": 5.2,
    "monthly_improvement_percent": 12.8,
    "form_accuracy_trend": 3.5,
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### Health Check

```http
GET /fitness/health

Response: 200 OK
{
    "status": "healthy",
    "module": "fitness_training",
    "version": "1.0.0",
    "timestamp": "2024-01-15T10:00:00Z"
}
```

---

## Implementation Examples

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/fitness"

class FitnessClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    # User Profile
    def create_profile(self, user_data):
        resp = requests.post(f"{self.base_url}/users/profile", json=user_data)
        return resp.json()
    
    def get_profile(self, user_id):
        resp = requests.get(f"{self.base_url}/users/{user_id}/profile")
        return resp.json()
    
    # Workouts
    def start_workout(self, user_id, workout_data):
        resp = requests.post(f"{self.base_url}/users/{user_id}/workouts", json=workout_data)
        return resp.json()
    
    def end_workout(self, workout_id, update_data):
        resp = requests.put(f"{self.base_url}/workouts/{workout_id}/end", json=update_data)
        return resp.json()
    
    # Biometrics
    def record_biometric(self, user_id, biometric_data):
        resp = requests.post(f"{self.base_url}/users/{user_id}/biometrics", json=biometric_data)
        return resp.json()
    
    # Coaching
    def analyze_form(self, exercise_name, pose_data, confidence_scores):
        payload = {
            "exercise_name": exercise_name,
            "pose_landmarks": pose_data,
            "confidence_scores": confidence_scores
        }
        resp = requests.post(f"{self.base_url}/analyze/pose", json=payload)
        return resp.json()
    
    def detect_emotion(self, pupil_data):
        resp = requests.post(f"{self.base_url}/analyze/emotional-state", json=pupil_data)
        return resp.json()
    
    def detect_stress(self, biometric_data):
        resp = requests.post(f"{self.base_url}/analyze/stress-level", json=biometric_data)
        return resp.json()

# Usage Example
client = FitnessClient()

# Create user
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "height_cm": 180,
    "weight_kg": 80,
    "fitness_level": "intermediate",
    "primary_goal": "muscle_gain"
}
user = client.create_profile(user_data)
user_id = user["user_id"]

# Start workout
workout_data = {
    "name": "Morning Push",
    "workout_type": "strength",
    "intensity": "moderate"
}
workout = client.start_workout(user_id, workout_data)
workout_id = workout["workout_id"]

# Record biometrics during workout
for hr in [120, 130, 140, 145, 140]:
    client.record_biometric(user_id, {
        "biometric_type": "heart_rate",
        "value": hr,
        "unit": "bpm",
        "context": "workout"
    })

# Analyze form
pose_analysis = client.analyze_form(
    "push_up",
    {
        "shoulder": {"x": 0.5, "y": 0.3, "z": 0.0},
        "elbow": {"x": 0.6, "y": 0.4, "z": 0.1},
        ...
    },
    {"shoulder": 0.95, "elbow": 0.92, ...}
)
print(f"Form Score: {pose_analysis['form_score']}")

# Detect emotion
emotion = client.detect_emotion({
    "pupil_size": 5.2,
    "pupil_dilation_rate": 0.15,
    "blink_rate": 18,
    "eye_gaze_stability": 75,
    "heart_rate": 145
})
print(f"Emotional State: {emotion['emotional_state']}")

# End workout
client.end_workout(workout_id, {
    "mood_after": "excellent",
    "energy_after": 3,
    "completed": true
})
```

---

## Supported Exercises

Current pose analysis support:

- **Push-up**: Chest, triceps, shoulders
- **Squat**: Quadriceps, glutes, hamstrings
- **Deadlift**: Back, glutes, hamstrings
- **Lunge**: Quadriceps, glutes, hamstrings
- **Pull-up**: Back, biceps
- **Plank**: Core, chest, shoulders
- **Bicep Curl**: Biceps
- *(More exercises can be added)*

Each exercise includes:

- Ideal joint angles
- Form issue detection
- Personalized recommendations
- Audio coaching

---

## Emotion Detection

The system detects emotional states based on pupil tracking:

- **Relaxed**: Small pupils, low dilation rate
- **Calm**: Neutral pupils, stable gaze
- **Neutral**: Average pupil size, normal blink rate
- **Focused**: Slightly large pupils, steady gaze, low blink rate
- **Engaged**: Large pupils, active dilation, good focus
- **Stressed**: Very large pupils, rapid dilation, high blink rate
- **Anxious**: Erratic pupils, unstable gaze
- **Fatigued**: Sluggish pupil response, frequent blinking

---

## Stress Level Detection

Stress is calculated from:

- **Heart rate elevation** (40 points): HR compared to resting HR
- **Heart rate variability** (30 points): Lower HRV = more stress
- **Pupil dilation rate** (20 points): Rapid dilation indicates stress
- **Respiratory rate** (10 points): Elevated RR is stress indicator

Stress Scale:

- 0-20: Very Relaxed
- 20-40: Relaxed
- 40-60: Normal
- 60-80: Stressed
- 80-100: Very Stressed

---

## Integration with ALBA/ALBI/JONA

The fitness module integrates with existing Kloud services:

- **ALBA**: Signal collection for biometric data streams
- **ALBI**: Neural processing of workout patterns and anomalies
- **JONA**: Adaptive music synthesis based on workout intensity and biometrics

```python
# Example: Real-time streaming to ALBA
alba_payload = {
    "sensors": {
        "heart_rate": 155,
        "calories_per_min": 12.5,
        "emotional_state_confidence": 0.85,
        "form_score": 87.5,
        "stress_level": 62,
        "pupil_size": 5.2,
        "blink_rate": 18
    },
    "channels": {
        "biometrics": "smartwatch",
        "pose": "camera",
        "emotions": "camera"
    },
    "metadata": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "workout_id": "660e8400-e29b-41d4-a716-446655440001",
        "exercise": "push_up",
        "timestamp": "2024-01-15T06:15:30Z"
    }
}
```

---

## Database Setup

### Create Tables

```sql
-- Run these migrations in PostgreSQL
-- Assuming alembic/migrations are set up

alembic revision --autogenerate -m "Add fitness module tables"
alembic upgrade head
```

Or manually:

```sql
CREATE TABLE fitness_users (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    height_cm FLOAT,
    weight_kg FLOAT,
    fitness_level VARCHAR(50),
    primary_goal VARCHAR(50),
    secondary_goals JSON DEFAULT '[]',
    resting_heart_rate FLOAT,
    max_heart_rate FLOAT,
    vo2_max FLOAT,
    preferred_workout_time VARCHAR(50),
    preferred_intensity VARCHAR(50),
    workout_duration_minutes INTEGER DEFAULT 45,
    workouts_per_week INTEGER DEFAULT 3,
    linked_wearables JSON DEFAULT '{}',
    camera_enabled BOOLEAN DEFAULT FALSE,
    microphone_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE workouts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workout_type VARCHAR(50) NOT NULL,
    intensity VARCHAR(50),
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    total_calories_burned FLOAT DEFAULT 0.0,
    average_heart_rate FLOAT,
    max_heart_rate FLOAT,
    min_heart_rate FLOAT,
    total_steps INTEGER DEFAULT 0,
    distance_km FLOAT DEFAULT 0.0,
    elevation_m FLOAT DEFAULT 0.0,
    mood_before VARCHAR(20),
    mood_after VARCHAR(20),
    energy_before INTEGER,
    energy_after INTEGER,
    pain_level INTEGER,
    music_playlist_id VARCHAR(255),
    adaptive_music_bpm INTEGER,
    motivational_cues JSON DEFAULT '[]',
    form_corrections JSON DEFAULT '[]',
    ai_feedback TEXT,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    location VARCHAR(255),
    weather_conditions VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES fitness_users(id)
);

CREATE TABLE exercises (
    id VARCHAR(36) PRIMARY KEY,
    workout_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    exercise_type VARCHAR(50) NOT NULL,
    muscle_groups JSON DEFAULT '[]',
    sets INTEGER,
    reps INTEGER,
    weight_kg FLOAT,
    duration_seconds INTEGER,
    distance_m FLOAT,
    form_score FLOAT DEFAULT 0.0,
    form_issues JSON DEFAULT '[]',
    recommended_form_corrections JSON DEFAULT '[]',
    pose_detection_data JSON,
    audio_coaching TEXT,
    difficulty_rating INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workouts(id)
);

CREATE TABLE biometric_data (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    biometric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    context VARCHAR(50),
    device_type VARCHAR(50),
    device_id VARCHAR(255),
    confidence_score FLOAT DEFAULT 1.0,
    raw_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES fitness_users(id),
    INDEX (user_id, biometric_type, measurement_time)
);

-- Additional tables: coaching_sessions, user_achievements, fitness_stats
-- (See fitness_models.py for complete schema)
```

---

## Performance Optimization

- **Caching**: BiometricData readings cached in Redis (5-min TTL)
- **Batch Inserts**: BiometricData can be bulk-inserted (100 readings at a time)
- **Indexing**: Key queries indexed (user_id, measurement_time, biometric_type)
- **Aggregation**: Stats updated every 30 minutes via background job
- **Streaming**: Real-time biometrics streamed to ALBA for live analysis

---

## Security Considerations

- ✅ All endpoints require authentication
- ✅ User data isolated by user_id
- ✅ Biometric data treated as PII (encrypted at rest)
- ✅ Camera/microphone access requires explicit user consent
- ✅ Wearable device connections use OAuth 2.0
- ✅ Rate limiting on all endpoints (100 req/min per user)

---

## Future Enhancements

- [ ] Wearable integration (Apple HealthKit, Google Fit, Fitbit API)
- [ ] Advanced pose estimation (3D skeleton tracking)
- [ ] Personal trainer matching algorithm
- [ ] Social features (friend competitions, group workouts)
- [ ] Nutrition tracking integration
- [ ] Sleep quality analysis
- [ ] Recovery recommendations
- [ ] Injury prevention alerts
- [ ] Progressive overload suggestions
- [ ] Workout program generation (AI-powered)
- [ ] Mobile app (React Native)
- [ ] Voice coaching (text-to-speech)

---

## Support & Documentation

- API Docs: `http://localhost:8000/docs` (Swagger UI)
- Python SDK: `kloud_sdk.fitness`
- Postman Collection: `kloud-fitness-collection.json`
- Issues: GitHub Issues or /support@kloud.cloud

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: Kloud Cloud Team

