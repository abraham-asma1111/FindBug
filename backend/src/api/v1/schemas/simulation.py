"""
Simulation API Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# Challenge Schemas
class ChallengeListResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    difficulty_level: str
    severity: str
    points: int
    estimated_time_minutes: int
    total_attempts: int
    total_completions: int
    success_rate: Optional[float]
    
    class Config:
        from_attributes = True


class ChallengeDetailsResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    vulnerability_type: str
    difficulty_level: str
    severity: str
    points: int
    estimated_time_minutes: int
    tutorial_video_url: Optional[str]
    documentation: Optional[str]
    external_resources: Optional[List[Dict]]
    hints: Optional[Dict]
    hint_costs: Optional[Dict]
    total_attempts: int
    total_completions: int
    success_rate: Optional[float]
    
    class Config:
        from_attributes = True


# Instance Schemas
class StartChallengeRequest(BaseModel):
    challenge_id: str


class StartChallengeResponse(BaseModel):
    instance_id: str
    url: str
    port: int
    expires_at: str
    status: str
    message: str = "Challenge instance started successfully"


class StopChallengeResponse(BaseModel):
    instance_id: str
    status: str
    message: str


# Report Schemas
class SubmitReportRequest(BaseModel):
    challenge_id: str
    title: str = Field(..., min_length=10, max_length=500)
    description: str = Field(..., min_length=50)
    steps_to_reproduce: str = Field(..., min_length=20)
    impact_assessment: Optional[str] = None
    suggested_severity: Optional[str] = None
    proof_of_concept: Optional[str] = None


class SubmitReportResponse(BaseModel):
    report_id: str
    is_correct: bool
    feedback: str
    points_awarded: int
    status: str


class ReportDetailsResponse(BaseModel):
    id: str
    challenge_id: str
    title: str
    description: str
    steps_to_reproduce: str
    impact_assessment: Optional[str]
    suggested_severity: Optional[str]
    proof_of_concept: Optional[str]
    is_correct: Optional[bool]
    feedback: Optional[str]
    points_awarded: int
    status: str
    submitted_at: datetime
    validated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Solution Schemas
class SubmitSolutionRequest(BaseModel):
    challenge_id: str
    title: str = Field(..., min_length=10, max_length=255)
    content: str = Field(..., min_length=100)
    video_url: Optional[str] = None


class SolutionResponse(BaseModel):
    id: str
    challenge_id: str
    user_id: str
    title: str
    content: str
    video_url: Optional[str]
    likes_count: int
    views_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Progress Schemas
class ProgressResponse(BaseModel):
    challenge_id: str
    status: str
    attempts: int
    hints_used: int
    completed_at: Optional[datetime]
    time_spent_seconds: int
    
    class Config:
        from_attributes = True


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    user_id: str
    rank: int
    total_points: int
    challenges_completed: int
    last_updated: datetime
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    total_entries: int
