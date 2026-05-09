#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VIDEO GENERATOR API — FastAPI Wrapper for BLERINA Video Pipeline            ║
║  Part of Kloud Cloud Industrial Backend                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Port: 8008                                                                   ║
║  Endpoints:                                                                   ║
║  - GET  /health          - Health check                                       ║
║  - GET  /status          - Detailed status                                    ║
║  - POST /generate        - Generate a video                                   ║
║  - GET  /videos          - List generated videos                              ║
║  - GET  /videos/{id}     - Get video info                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Date: 2026-02-08
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Import the video generator
import video_generator_blerina as vg

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("PORT", "8008"))
VIDEO_OUTPUT_DIR = Path(os.getenv("VIDEO_OUTPUT_DIR", "./generated_videos"))
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)

# Track jobs
JOBS: Dict[str, Dict[str, Any]] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Video Generator BLERINA",
    description="AI-powered video generation for Kloud",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VideoRequest(BaseModel):
    """Request to generate a video."""
    topic: str = Field(..., description="Video topic/title", min_length=3, max_length=500)
    style: str = Field(
        default="educational", 
        description="Video style: educational, documentary, tutorial, presentation, social_media"
    )
    voice: str = Field(
        default="professional",
        description="Voice style: professional, friendly, narrator, energetic"
    )
    add_subtitles: bool = Field(default=True, description="Add SRT subtitles")


class VideoResponse(BaseModel):
    """Response with video generation result."""
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    """Status of a video generation job."""
    job_id: str
    status: str  # pending, processing, completed, failed
    topic: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK
# ═══════════════════════════════════════════════════════════════════════════════

async def process_video_job(job_id: str, request: VideoRequest) -> None:
    """Process video generation in background."""
    try:
        JOBS[job_id]["status"] = "processing"
        
        result = await vg.generate_video(
            topic=request.topic,
            style=request.style,
            voice=request.voice,
            add_subtitles=request.add_subtitles
        )
        
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        JOBS[job_id]["result"] = result
        
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    health_status = vg.health()
    return {
        "status": "ok" if health_status.get("ffmpeg_available") else "degraded",
        "service": "video-generator",
        "version": "1.0.0",
        "details": health_status
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    """Detailed status with job statistics."""
    health_status = vg.health()
    
    # Count jobs by status
    job_stats = {
        "pending": sum(1 for j in JOBS.values() if j["status"] == "pending"),
        "processing": sum(1 for j in JOBS.values() if j["status"] == "processing"),
        "completed": sum(1 for j in JOBS.values() if j["status"] == "completed"),
        "failed": sum(1 for j in JOBS.values() if j["status"] == "failed"),
    }
    
    # List generated videos
    videos = list(VIDEO_OUTPUT_DIR.glob("*.mp4"))
    
    return {
        "status": "ok",
        "service": "video-generator",
        "version": "1.0.0",
        "capabilities": health_status,
        "job_stats": job_stats,
        "videos_on_disk": len(videos),
        "output_directory": str(VIDEO_OUTPUT_DIR)
    }


@app.post("/generate", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """
    Generate a video from a topic.
    
    This runs in the background. Use /jobs/{job_id} to check status.
    """
    # Check if FFmpeg is available
    health_status = vg.health()
    if not health_status.get("ffmpeg_available"):
        raise HTTPException(
            status_code=503,
            detail="FFmpeg not available. Video generation disabled."
        )
    
    # Create job
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "topic": request.topic,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "result": None,
        "error": None
    }
    
    # Start background task
    background_tasks.add_task(process_video_job, job_id, request)
    
    return VideoResponse(
        job_id=job_id,
        status="pending",
        message=f"Video generation started. Check status at /jobs/{job_id}"
    )


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a video generation job."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JOBS[job_id]


@app.get("/jobs")
async def list_jobs() -> Dict[str, Any]:
    """List all video generation jobs."""
    return {
        "total": len(JOBS),
        "jobs": list(JOBS.values())
    }


@app.get("/videos")
async def list_videos() -> Dict[str, Any]:
    """List all generated videos on disk."""
    videos = []
    
    for video_path in VIDEO_OUTPUT_DIR.glob("*.mp4"):
        stat = video_path.stat()
        srt_path = video_path.with_suffix(".srt")
        
        videos.append({
            "name": video_path.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
            "has_subtitles": srt_path.exists(),
            "download_url": f"/videos/download/{video_path.stem}"
        })
    
    return {
        "total": len(videos),
        "videos": sorted(videos, key=lambda x: x["created"], reverse=True)
    }


@app.get("/videos/download/{video_name}")
async def download_video(video_name: str) -> FileResponse:
    """Download a generated video."""
    video_path = VIDEO_OUTPUT_DIR / f"{video_name}.mp4"
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found")
    
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=video_path.name
    )


@app.get("/videos/subtitles/{video_name}")
async def download_subtitles(video_name: str) -> FileResponse:
    """Download subtitles for a video."""
    srt_path = VIDEO_OUTPUT_DIR / f"{video_name}.srt"
    
    if not srt_path.exists():
        raise HTTPException(status_code=404, detail=f"Subtitles for {video_name} not found")
    
    return FileResponse(
        path=srt_path,
        media_type="application/x-subrip",
        filename=srt_path.name
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("VIDEO GENERATOR API — Starting...")
    print("=" * 70)
    
    # Check health before starting
    health_status = vg.health()
    print("\nHealth Check:")
    print(f"  FFmpeg: {'✅' if health_status['ffmpeg_available'] else '❌'}")
    print(f"  Pillow: {'✅' if health_status['pillow_available'] else '❌'}")
    print(f"  TTS Engines: {health_status['tts_engines']}")
    
    if not health_status['ffmpeg_available']:
        print("\n⚠️  WARNING: FFmpeg not available. Video generation will fail!")
    
    print(f"\n🚀 Starting server on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

