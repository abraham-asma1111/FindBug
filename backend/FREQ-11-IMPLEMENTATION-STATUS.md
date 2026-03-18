# FREQ-11 Implementation Status: Researcher Reputation System

## Requirement
**FREQ-11**: The system shall track and update researcher reputation scores, signal strength, and display public leaderboards/rankings.

**Priority**: High

## Business Rules Implemented
- **BR-09**: Reputation Scoring
  - Reputation starts at 0
  - Valid reports: +10 to +50 points based on severity
    - Critical: +50 points
    - High: +30 points
    - Medium: +20 points
    - Low: +10 points
  - Invalid reports: -20 points
  - Duplicate reports (after 24h): -20 points
  - Duplicate reports (within 24h): No penalty
  - Reputation cannot go below 0

## Implementation Details

### 1. Reputation Service (`backend/src/services/reputation_service.py`)
Complete service with:
- **Point Calculation**: `calculate_points_for_report()` - BR-09 rules
- **Reputation Updates**: `update_reputation()` - Updates score and earnings
- **Ranking System**: `_update_rankings()` - Ranks all researchers
- **Leaderboard**: `get_leaderboard()` - Top researchers by reputation
- **Researcher Profile**: `get_researcher_profile()` - Public profile with stats
- **Rank Info**: `get_researcher_rank()` - Current rank and percentile
- **Top Earners**: `get_top_earners()` - Alternative leaderboard by earnings
- **Statistics**: `_get_researcher_stats()` - Comprehensive researcher stats

### 2. API Endpoints (`backend/src/api/v1/endpoints/reputation.py`)
Public and authenticated endpoints:

#### Public Endpoints (No Auth Required)
- `GET /api/v1/leaderboard` - Public leaderboard (top 10 by default)
- `GET /api/v1/leaderboard/top-earners` - Top earners leaderboard
- `GET /api/v1/researchers/{researcher_id}/profile` - Public researcher profile
- `GET /api/v1/researchers/{researcher_id}/rank` - Researcher rank and percentile

#### Authenticated Endpoints
- `GET /api/v1/my-reputation` - Current user's reputation (researchers only)
- `POST/GET /api/v1/researchers/{researcher_id}/update-reputation` - Manual update (admins/triage only)

### 3. Integration with Bounty Service
Automatic reputation updates integrated into:
- **Bounty Approval** (`approve_bounty()`) - Updates reputation when bounty approved
- **Bounty Rejection** (`reject_bounty()`) - Applies penalty for rejected reports
- **Mark as Paid** (`mark_as_paid()`) - Updates total earnings

### 4. Database Fields (Already Exists)
Researcher model already has required fields:
- `reputation_score` (Decimal) - Current reputation score
- `rank` (Integer) - Current rank among all researchers
- `total_earnings` (Decimal) - Total bounties earned

## Features

### Leaderboard System
- Top researchers by reputation score
- Pagination support (limit/offset)
- Shows: rank, username, reputation, earnings, statistics
- Public access - no authentication required

### Researcher Profile
- Public profile with reputation and rank
- Statistics:
  - Total reports submitted
  - Valid/invalid/duplicate counts
  - Success rate percentage
  - Reports by severity breakdown
- Social links (website, GitHub, Twitter, LinkedIn)
- Total earnings

### Ranking System
- Automatic ranking updates after reputation changes
- Rank based on reputation score (highest first)
- Percentile calculation (top X%)
- Total researchers count

### Statistics Tracking
- Total reports by status
- Success rate calculation
- Severity breakdown (critical/high/medium/low)
- Valid vs invalid vs duplicate counts

## API Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/leaderboard` | GET | Public | Get top researchers |
| `/api/v1/leaderboard/top-earners` | GET | Public | Get top earners |
| `/api/v1/researchers/{id}/profile` | GET | Public | Get researcher profile |
| `/api/v1/researchers/{id}/rank` | GET | Public | Get researcher rank |
| `/api/v1/my-reputation` | GET | Researcher | Get own reputation |
| `/api/v1/researchers/{id}/update-reputation` | POST/GET | Admin/Triage | Manual update |

## Reputation Point Rules (BR-09)

| Event | Points | Notes |
|-------|--------|-------|
| Critical severity report | +50 | Valid reports only |
| High severity report | +30 | Valid reports only |
| Medium severity report | +20 | Valid reports only |
| Low severity report | +10 | Valid reports only |
| Invalid report | -20 | Penalty for invalid submissions |
| Duplicate (after 24h) | -20 | Penalty for late duplicates |
| Duplicate (within 24h) | 0 | No penalty, gets 50% bounty |

## Automatic Triggers
Reputation updates automatically when:
1. Bounty is approved (valid report) → Add points based on severity
2. Bounty is rejected (invalid report) → Deduct 20 points
3. Bounty is marked as paid → Update total earnings
4. Report marked as duplicate → Apply duplicate rules

## Testing Scenarios

### Scenario 1: Valid Report Approved
1. Researcher submits report
2. Triage specialist validates and assigns severity
3. Finance officer approves bounty
4. **Result**: Reputation increases by severity points (10-50)

### Scenario 2: Invalid Report Rejected
1. Researcher submits report
2. Triage specialist marks as invalid
3. Finance officer rejects bounty
4. **Result**: Reputation decreases by 20 points (min 0)

### Scenario 3: Duplicate Within 24 Hours
1. Researcher submits duplicate within 24h
2. Triage specialist marks as duplicate
3. Finance officer approves 50% bounty
4. **Result**: No reputation penalty, gets partial bounty

### Scenario 4: Duplicate After 24 Hours
1. Researcher submits duplicate after 24h
2. Triage specialist marks as duplicate
3. Finance officer rejects bounty
4. **Result**: Reputation decreases by 20 points, no bounty

### Scenario 5: Leaderboard Display
1. Multiple researchers with different scores
2. Public accesses leaderboard
3. **Result**: Shows top 10 ranked by reputation

## Files Modified/Created

### Created
- `backend/src/api/v1/endpoints/reputation.py` - Reputation API endpoints

### Modified
- `backend/src/services/bounty_service.py` - Added reputation update calls
- `backend/src/main.py` - Registered reputation router
- `backend/src/api/v1/endpoints/__init__.py` - Added reputation export

### Existing (Used)
- `backend/src/services/reputation_service.py` - Complete reputation service
- `backend/src/domain/models/researcher.py` - Researcher model with reputation fields

## Status: ✅ COMPLETE

All FREQ-11 requirements implemented:
- ✅ Reputation tracking and scoring (BR-09)
- ✅ Automatic reputation updates
- ✅ Public leaderboard display
- ✅ Researcher rankings
- ✅ Signal strength (reputation score)
- ✅ Statistics and profiles
- ✅ Integration with bounty workflow

## Next Steps
- FREQ-12: Notification system (send notifications on reputation changes)
- FREQ-09: Messaging system (if needed)
- Testing: Create test cases for reputation scenarios
- Frontend: Build leaderboard and profile UI components
