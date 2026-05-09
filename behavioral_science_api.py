"""
BEHAVIORAL SCIENCE API - Kloud Research Engine

This API collects and analyzes behavioral data from frontend modules:
- Mood patterns and emotional trends
- Habit formation and adherence curves
- Focus/attention span analytics
- Circadian productivity patterns

Research Methodologies:
- Time-series analysis for trend detection
- Correlation mapping (weather, time, activity)
- Machine learning for pattern prediction
- Anonymized cohort comparisons
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import hashlib
import statistics

app = FastAPI(
    title="Kloud Behavioral Science API",
    description="Research-grade behavioral analytics engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (production would use PostgreSQL/TimescaleDB)
mood_data: Dict[str, List[dict]] = {}
habit_data: Dict[str, List[dict]] = {}
focus_data: Dict[str, List[dict]] = {}
behavioral_insights: Dict[str, dict] = {}

# ============== MODELS ==============

class MoodEntry(BaseModel):
    id: str
    mood: int  # 1-5
    emoji: str
    note: Optional[str] = None
    timestamp: str
    timeOfDay: str
    factors: List[str] = []

class MoodLogRequest(BaseModel):
    entry: MoodEntry
    deviceId: str
    userAgent: Optional[str] = None
    screenSize: Optional[str] = None
    timezone: Optional[str] = None

class MoodSyncRequest(BaseModel):
    entries: List[dict]
    deviceId: str
    timezone: Optional[str] = None

class HabitLogRequest(BaseModel):
    habitId: str
    date: str
    action: str
    deviceId: str
    timestamp: str

class HabitSyncRequest(BaseModel):
    habits: List[dict]
    logs: List[dict]
    deviceId: str
    timezone: Optional[str] = None

class FocusSession(BaseModel):
    id: str
    type: str  # 'focus' or 'break'
    duration: int
    completed: bool
    startedAt: str
    endedAt: Optional[str] = None
    task: Optional[str] = None
    interrupted: bool = False

class FocusLogRequest(BaseModel):
    action: str
    session: FocusSession
    deviceId: str
    timezone: Optional[str] = None

# ============== UTILITY FUNCTIONS ==============

def anonymize_device_id(device_id: str) -> str:
    """Create anonymous but consistent user identifier"""
    return hashlib.sha256(f"kloud_{device_id}".encode()).hexdigest()[:16]

def get_circadian_phase(hour: int) -> str:
    """Classify hour into circadian phase"""
    if 5 <= hour < 9:
        return "early_morning"
    elif 9 <= hour < 12:
        return "late_morning"
    elif 12 <= hour < 14:
        return "midday"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def calculate_trend(values: List[float], window: int = 7) -> str:
    """Determine if trend is improving, declining, or stable"""
    if len(values) < window * 2:
        return "insufficient_data"
    
    recent = values[-window:]
    previous = values[-window*2:-window]
    
    recent_avg = statistics.mean(recent)
    previous_avg = statistics.mean(previous)
    
    diff = recent_avg - previous_avg
    threshold = 0.15 * statistics.mean(values) if values else 0.3
    
    if diff > threshold:
        return "improving"
    elif diff < -threshold:
        return "declining"
    return "stable"

def calculate_habit_formation_stage(completions: List[bool]) -> dict:
    """
    Research shows habit formation takes 18-254 days (avg 66).
    Track which stage user is in.
    """
    consecutive = 0
    max_consecutive = 0
    
    for completed in reversed(completions):
        if completed:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            break
    
    if consecutive < 7:
        stage = "initiation"
        message = "Building foundation - focus on showing up"
    elif consecutive < 21:
        stage = "formation"
        message = "Habit forming - resistance is normal"
    elif consecutive < 66:
        stage = "consolidation"
        message = "Getting easier - don't break the chain"
    else:
        stage = "automaticity"
        message = "Habit is automatic - maintenance mode"
    
    return {
        "stage": stage,
        "currentStreak": consecutive,
        "longestStreak": max_consecutive,
        "daysToNextStage": {
            "initiation": 7 - consecutive,
            "formation": 21 - consecutive,
            "consolidation": 66 - consecutive,
            "automaticity": 0
        }.get(stage, 0),
        "message": message
    }

def analyze_focus_patterns(sessions: List[dict]) -> dict:
    """
    Analyze focus session data for productivity insights.
    Based on ultradian rhythm research (90-120 min cycles).
    """
    if not sessions:
        return {"insight": "No data yet"}
    
    completed = [s for s in sessions if s.get("completed")]
    interrupted = [s for s in sessions if s.get("interrupted")]
    
    # Optimal duration analysis
    durations = [s["duration"] for s in completed]
    optimal_duration = statistics.median(durations) if durations else 25
    
    # Hour analysis
    hour_success = {}
    for s in sessions:
        try:
            hour = datetime.fromisoformat(s["startedAt"].replace("Z", "+00:00")).hour
        except:
            continue
        
        if hour not in hour_success:
            hour_success[hour] = {"completed": 0, "total": 0}
        hour_success[hour]["total"] += 1
        if s.get("completed"):
            hour_success[hour]["completed"] += 1
    
    best_hour = None
    best_rate = 0
    for hour, data in hour_success.items():
        if data["total"] >= 3:  # Minimum sample size
            rate = data["completed"] / data["total"]
            if rate > best_rate:
                best_rate = rate
                best_hour = hour
    
    # Completion rate trend
    completion_rate = len(completed) / len(sessions) if sessions else 0
    
    return {
        "totalSessions": len(sessions),
        "completedSessions": len(completed),
        "completionRate": round(completion_rate, 2),
        "optimalDuration": optimal_duration,
        "bestHour": best_hour,
        "bestHourSuccessRate": round(best_rate, 2) if best_hour else None,
        "circadianPattern": get_circadian_phase(best_hour) if best_hour else None,
        "interruptionRate": round(len(interrupted) / len(sessions), 2) if sessions else 0,
        "recommendation": _get_focus_recommendation(completion_rate, optimal_duration)
    }

def _get_focus_recommendation(completion_rate: float, optimal_duration: int) -> str:
    if completion_rate < 0.5:
        return f"Try shorter sessions ({max(10, optimal_duration - 10)} min) to build consistency"
    elif completion_rate < 0.8:
        return f"Good progress! {optimal_duration} min seems optimal for you"
    else:
        return f"Excellent focus! Consider trying {optimal_duration + 10} min sessions"

# ============== MOOD ENDPOINTS ==============

@app.post("/api/behavioral/mood/log")
async def log_mood(request: MoodLogRequest):
    """
    Log a mood entry with full context.
    Collects: mood level, factors, time, device info for research.
    """
    anon_id = anonymize_device_id(request.deviceId)
    
    if anon_id not in mood_data:
        mood_data[anon_id] = []
    
    # Enrich with research metadata
    entry_data = request.entry.dict()
    entry_data["_research"] = {
        "circadianPhase": get_circadian_phase(datetime.fromisoformat(request.entry.timestamp.replace("Z", "+00:00")).hour),
        "dayOfWeek": datetime.fromisoformat(request.entry.timestamp.replace("Z", "+00:00")).strftime("%A"),
        "isMobile": "Mobile" in (request.userAgent or ""),
        "timezone": request.timezone
    }
    
    mood_data[anon_id].append(entry_data)
    
    # Trigger analysis if enough data
    if len(mood_data[anon_id]) % 5 == 0:
        _analyze_mood_patterns(anon_id)
    
    return {
        "success": True,
        "message": "Mood logged for research",
        "entryId": request.entry.id,
        "totalEntries": len(mood_data[anon_id])
    }

@app.post("/api/behavioral/mood/sync")
async def sync_mood(request: MoodSyncRequest):
    """
    Sync mood entries from device and return analytics.
    """
    anon_id = anonymize_device_id(request.deviceId)
    
    # Merge entries
    existing_ids = {e.get("id") for e in mood_data.get(anon_id, [])}
    for entry in request.entries:
        if entry.get("id") not in existing_ids:
            if anon_id not in mood_data:
                mood_data[anon_id] = []
            mood_data[anon_id].append(entry)
    
    # Calculate stats
    entries = mood_data.get(anon_id, [])
    stats = _calculate_mood_stats(entries)
    
    return {
        "success": True,
        "synced": len(entries),
        "stats": stats
    }

def _analyze_mood_patterns(anon_id: str):
    """Background analysis of mood patterns"""
    entries = mood_data.get(anon_id, [])
    if len(entries) < 10:
        return
    
    # Time-of-day analysis
    time_moods = {}
    for e in entries:
        tod = e.get("timeOfDay", "unknown")
        if tod not in time_moods:
            time_moods[tod] = []
        time_moods[tod].append(e.get("mood", 3))
    
    best_time = max(time_moods.items(), key=lambda x: statistics.mean(x[1]))[0] if time_moods else None
    
    # Factor correlation
    factor_moods = {}
    for e in entries:
        mood = e.get("mood", 3)
        for factor in e.get("factors", []):
            if factor not in factor_moods:
                factor_moods[factor] = []
            factor_moods[factor].append(mood)
    
    positive_factors = []
    negative_factors = []
    baseline = statistics.mean([e.get("mood", 3) for e in entries])
    
    for factor, moods in factor_moods.items():
        if len(moods) >= 3:
            avg = statistics.mean(moods)
            if avg > baseline + 0.3:
                positive_factors.append(factor)
            elif avg < baseline - 0.3:
                negative_factors.append(factor)
    
    behavioral_insights[anon_id] = {
        "moodAnalysis": {
            "bestTimeOfDay": best_time,
            "avgMood": round(baseline, 2),
            "positiveFactors": positive_factors,
            "negativeFactors": negative_factors,
            "trend": calculate_trend([e.get("mood", 3) for e in entries[-30:]])
        },
        "analyzedAt": datetime.now().isoformat()
    }

def _calculate_mood_stats(entries: List[dict]) -> dict:
    if not entries:
        return None
    
    moods = [e.get("mood", 3) for e in entries]
    
    # Streak calculation
    dates = sorted(set(e.get("timestamp", "")[:10] for e in entries), reverse=True)
    streak = 0
    for i, date in enumerate(dates):
        expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if date == expected:
            streak += 1
        else:
            break
    
    return {
        "avgMood": round(statistics.mean(moods), 2),
        "totalEntries": len(entries),
        "streak": streak,
        "trend": calculate_trend(moods[-14:]) if len(moods) >= 14 else "building_data"
    }

# ============== HABIT ENDPOINTS ==============

@app.post("/api/behavioral/habits/log")
async def log_habit(request: HabitLogRequest):
    """
    Log habit completion event.
    Tracks: habit ID, completion time, action type for formation analysis.
    """
    anon_id = anonymize_device_id(request.deviceId)
    
    if anon_id not in habit_data:
        habit_data[anon_id] = []
    
    habit_data[anon_id].append({
        "habitId": request.habitId,
        "date": request.date,
        "action": request.action,
        "timestamp": request.timestamp,
        "_research": {
            "hour": datetime.fromisoformat(request.timestamp.replace("Z", "+00:00")).hour,
            "dayOfWeek": datetime.fromisoformat(request.timestamp.replace("Z", "+00:00")).strftime("%A")
        }
    })
    
    return {
        "success": True,
        "message": "Habit logged",
        "totalLogs": len(habit_data[anon_id])
    }

@app.post("/api/behavioral/habits/sync")
async def sync_habits(request: HabitSyncRequest):
    """
    Sync habit data and return formation analysis.
    """
    anon_id = anonymize_device_id(request.deviceId)
    
    # Store habits and logs
    habit_info = {h.get("id"): h for h in request.habits}
    
    # Analyze each habit's formation stage
    formation_analysis = {}
    for habit in request.habits:
        habit_id = habit.get("id")
        habit_logs = [l for l in request.logs if l.get("habitId") == habit_id]
        
        # Get completion sequence
        dates_completed = set()
        for log in habit_logs:
            if log.get("completed", 0) >= habit.get("targetPerDay", 1):
                dates_completed.add(log.get("date"))
        
        # Build daily completion array for last 90 days
        completions = []
        for i in range(90):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            completions.append(date in dates_completed)
        
        formation_analysis[habit_id] = calculate_habit_formation_stage(completions)
    
    return {
        "success": True,
        "formationAnalysis": formation_analysis,
        "totalHabits": len(request.habits),
        "researchNote": "Habit formation averages 66 days (range: 18-254)"
    }

# ============== FOCUS ENDPOINTS ==============

@app.post("/api/behavioral/focus/log")
async def log_focus(request: FocusLogRequest):
    """
    Log focus session event.
    Tracks: session duration, completion, interruptions, task for productivity research.
    """
    anon_id = anonymize_device_id(request.deviceId)
    
    if anon_id not in focus_data:
        focus_data[anon_id] = []
    
    session_data = request.session.dict()
    session_data["_action"] = request.action
    session_data["_research"] = {
        "circadianPhase": get_circadian_phase(
            datetime.fromisoformat(request.session.startedAt.replace("Z", "+00:00")).hour
        ),
        "hasTask": bool(request.session.task),
        "timezone": request.timezone
    }
    
    focus_data[anon_id].append(session_data)
    
    # Analyze if action is complete or interrupt
    analysis = None
    if request.action in ["complete", "interrupt"]:
        analysis = analyze_focus_patterns(focus_data[anon_id])
    
    return {
        "success": True,
        "action": request.action,
        "analysis": analysis
    }

@app.get("/api/behavioral/focus/analysis/{device_id}")
async def get_focus_analysis(device_id: str):
    """Get focus pattern analysis for a device"""
    anon_id = anonymize_device_id(device_id)
    sessions = focus_data.get(anon_id, [])
    
    return {
        "success": True,
        "analysis": analyze_focus_patterns(sessions),
        "sessionCount": len(sessions)
    }

# ============== RESEARCH ENDPOINTS ==============

@app.get("/api/behavioral/insights/{device_id}")
async def get_behavioral_insights(device_id: str):
    """
    Get comprehensive behavioral insights for a user.
    Combines mood, habit, and focus analysis.
    """
    anon_id = anonymize_device_id(device_id)
    
    insights = {
        "mood": _calculate_mood_stats(mood_data.get(anon_id, [])),
        "habits": None,
        "focus": analyze_focus_patterns(focus_data.get(anon_id, [])),
        "crossAnalysis": None
    }
    
    # Cross-analysis: mood vs productivity correlation
    moods = mood_data.get(anon_id, [])
    focuses = focus_data.get(anon_id, [])
    
    if len(moods) >= 5 and len(focuses) >= 5:
        # Simple correlation: do high mood days have better focus?
        mood_by_date = {}
        for m in moods:
            date = m.get("timestamp", "")[:10]
            if date not in mood_by_date:
                mood_by_date[date] = []
            mood_by_date[date].append(m.get("mood", 3))
        
        focus_by_date = {}
        for f in focuses:
            date = f.get("startedAt", "")[:10]
            if date not in focus_by_date:
                focus_by_date[date] = {"completed": 0, "total": 0}
            focus_by_date[date]["total"] += 1
            if f.get("completed"):
                focus_by_date[date]["completed"] += 1
        
        # Compare overlapping dates
        high_mood_focus = []
        low_mood_focus = []
        
        for date, focus in focus_by_date.items():
            if date in mood_by_date and focus["total"] > 0:
                avg_mood = statistics.mean(mood_by_date[date])
                completion_rate = focus["completed"] / focus["total"]
                
                if avg_mood >= 4:
                    high_mood_focus.append(completion_rate)
                elif avg_mood <= 2:
                    low_mood_focus.append(completion_rate)
        
        if high_mood_focus and low_mood_focus:
            insights["crossAnalysis"] = {
                "moodFocusCorrelation": {
                    "highMoodCompletionRate": round(statistics.mean(high_mood_focus), 2),
                    "lowMoodCompletionRate": round(statistics.mean(low_mood_focus), 2),
                    "insight": "Your mood significantly affects focus" 
                        if abs(statistics.mean(high_mood_focus) - statistics.mean(low_mood_focus)) > 0.2
                        else "Your focus is consistent regardless of mood"
                }
            }
    
    return {
        "success": True,
        "insights": insights,
        "dataPoints": {
            "mood": len(moods),
            "focus": len(focuses),
            "habits": len(habit_data.get(anon_id, []))
        }
    }

@app.get("/api/behavioral/research/aggregate")
async def get_aggregate_research():
    """
    Anonymous aggregate research data.
    Used for population-level insights.
    """
    total_users = len(set(list(mood_data.keys()) + list(focus_data.keys()) + list(habit_data.keys())))
    total_mood_entries = sum(len(v) for v in mood_data.values())
    total_focus_sessions = sum(len(v) for v in focus_data.values())
    total_habit_logs = sum(len(v) for v in habit_data.values())
    
    # Aggregate mood by time of day
    time_of_day_moods = {}
    for entries in mood_data.values():
        for e in entries:
            tod = e.get("timeOfDay", "unknown")
            if tod not in time_of_day_moods:
                time_of_day_moods[tod] = []
            time_of_day_moods[tod].append(e.get("mood", 3))
    
    avg_by_time = {
        k: round(statistics.mean(v), 2) 
        for k, v in time_of_day_moods.items() 
        if len(v) >= 10
    }
    
    return {
        "success": True,
        "aggregateStats": {
            "totalAnonymousUsers": total_users,
            "totalMoodEntries": total_mood_entries,
            "totalFocusSessions": total_focus_sessions,
            "totalHabitLogs": total_habit_logs,
            "avgMoodByTimeOfDay": avg_by_time
        },
        "researchNote": "All data is anonymized and used only for behavioral research"
    }

# ============== HEALTH CHECK ==============

@app.get("/")
async def root():
    return {
        "service": "Behavioral Science API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /health": "Health check",
            "GET /api/status": "Service status",
            "POST /api/behavioral/mood/sync": "Sync mood data",
            "POST /api/behavioral/habits/sync": "Sync habit data",
            "GET /api/behavioral/insights/{device_id}": "Get insights"
        }
    }

@app.get("/health")
@app.get("/api/behavioral/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Behavioral Science API",
        "version": "1.0.0",
        "capabilities": [
            "mood_tracking",
            "habit_formation_analysis",
            "focus_pattern_detection",
            "circadian_productivity_mapping",
            "cross_domain_correlation"
        ],
        "dataPoints": {
            "moodEntries": sum(len(v) for v in mood_data.values()),
            "focusSessions": sum(len(v) for v in focus_data.values()),
            "habitLogs": sum(len(v) for v in habit_data.values())
        }
    }

@app.get("/api/status")
@app.get("/status")
async def api_status():
    return {
        "status": "operational",
        "service": "Behavioral Science API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dataPoints": {
            "moodEntries": sum(len(v) for v in mood_data.values()),
            "focusSessions": sum(len(v) for v in focus_data.values()),
            "habitLogs": sum(len(v) for v in habit_data.values())
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

