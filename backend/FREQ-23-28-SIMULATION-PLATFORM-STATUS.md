# FREQ-23 to FREQ-28: Bug Bounty Simulation Platform

**Feature Group**: Learning & Training Platform  
**Priority**: High  
**Status**: 🚧 PLANNING

---

## Overview

A complete bug bounty simulation environment for learning and training, combining:
- **Learning Platform** (YouTube-style): Video tutorials, writeups, community solutions
- **Challenge Environment** (HackTheBox-style): Vulnerable applications to exploit
- **Reporting Workflow** (Real bug bounty): Submit reports, get triage feedback, earn reputation
- **Community Features**: Share solutions, discuss techniques, learn from others

Users can:
1. Watch training videos and read tutorials
2. Practice exploiting vulnerable challenges
3. Submit detailed vulnerability reports with PoC
4. Receive automated and manual feedback from triage
5. Build reputation and ranking through successful reports
6. Share and learn from community solutions

---

## Requirements Summary

### FREQ-23: Simulation Environment (High Priority)
**Requirement**: The system shall provide a bug bounty simulation environment with simulated vulnerable applications.

**Components**:
- Vulnerable web applications (simulated targets)
- Isolated sandbox environment
- Multiple vulnerability types (XSS, SQLi, CSRF, etc.)
- Interactive challenges

---

### FREQ-24: Mirror Real Workflows (Medium Priority)
**Requirement**: The system shall mirror real bug bounty workflows within the simulation using simulated data.

**Components**:
- Simulated programs
- Simulated organizations
- Report submission workflow
- Triage simulation
- Bounty awards (virtual points)

---

### FREQ-25: Difficulty Levels (High Priority)
**Requirement**: The system shall support beginner, intermediate, and advanced simulation levels.

**Levels**:
- **Beginner**: Basic vulnerabilities with hints
- **Intermediate**: Moderate complexity, fewer hints
- **Advanced**: Complex vulnerabilities, no hints

---

### FREQ-26: Simulated Reports (High Priority)
**Requirement**: The system shall allow users to submit simulated vulnerability reports without affecting real programs.

**Features**:
- Separate report submission flow
- Virtual bounty points
- Practice report writing
- No impact on real data

---

### FREQ-27: Data Isolation (High Priority)
**Requirement**: The system shall isolate simulation data from real crowdsourced bug bounty data.

**Implementation**:
- Separate database tables
- Clear UI distinction
- Isolated workflows
- No cross-contamination

---

### FREQ-28: Automated Feedback (High Priority)
**Requirement**: The system shall provide automated feedback and learning hints for simulation reports.

**Features**:
- Automatic validation
- Hint system
- Learning resources
- Progress tracking

---

## Architecture Design

### 1. Database Schema

```sql
-- Simulation Programs (isolated from real programs)
CREATE TABLE simulation_programs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(20), -- beginner, intermediate, advanced
    category VARCHAR(100), -- web, api, mobile, etc.
    target_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Simulation Challenges (specific vulnerabilities to find)
CREATE TABLE simulation_challenges (
    id UUID PRIMARY KEY,
    program_id UUID REFERENCES simulation_programs(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    vulnerability_type VARCHAR(100), -- xss, sqli, csrf, etc.
    difficulty_level VARCHAR(20),
    points INTEGER, -- virtual points for completion
    hint_1 TEXT,
    hint_2 TEXT,
    hint_3 TEXT,
    solution TEXT, -- hidden until completed
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
);

-- User Progress (track learning journey)
CREATE TABLE simulation_progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    challenge_id UUID REFERENCES simulation_challenges(id),
    status VARCHAR(20), -- not_started, in_progress, completed
    attempts INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    time_spent_seconds INTEGER,
    created_at TIMESTAMP,
    UNIQUE(user_id, challenge_id)
);

-- Simulation Reports (practice reports)
CREATE TABLE simulation_reports (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    challenge_id UUID REFERENCES simulation_challenges(id),
    program_id UUID REFERENCES simulation_programs(id),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    steps_to_reproduce TEXT NOT NULL,
    impact_assessment TEXT,
    suggested_severity VARCHAR(20),
    proof_of_concept TEXT,
    status VARCHAR(20), -- submitted, validated, invalid
    is_correct BOOLEAN, -- did they find the right vulnerability?
    feedback TEXT, -- automated feedback
    points_awarded INTEGER DEFAULT 0,
    submitted_at TIMESTAMP,
    validated_at TIMESTAMP
);

-- Learning Resources
CREATE TABLE simulation_resources (
    id UUID PRIMARY KEY,
    challenge_id UUID REFERENCES simulation_challenges(id),
    resource_type VARCHAR(50), -- article, video, documentation
    title VARCHAR(255),
    description TEXT,
    url VARCHAR(500),
    created_at TIMESTAMP
);

-- Leaderboard
CREATE TABLE simulation_leaderboard (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    total_points INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    rank INTEGER,
    last_updated TIMESTAMP,
    UNIQUE(user_id)
);
```

---

### 2. Vulnerable Applications

**Option A: Embedded Challenges** (Recommended for MVP)
- Build challenges directly into the platform
- Simulated vulnerable endpoints
- Controlled environment
- Easier to maintain

**Option B: Separate Vulnerable Apps** (Future Enhancement)
- Deploy actual vulnerable applications (like Juice Shop)
- Docker containers
- More realistic
- More complex infrastructure

**MVP Approach**: Start with Option A (embedded challenges)

---

### 3. Challenge Categories

#### Web Application Vulnerabilities
1. **XSS (Cross-Site Scripting)**
   - Reflected XSS
   - Stored XSS
   - DOM-based XSS

2. **SQL Injection**
   - Classic SQLi
   - Blind SQLi
   - Time-based SQLi

3. **Authentication Flaws**
   - Weak passwords
   - Session hijacking
   - JWT vulnerabilities

4. **Authorization Issues**
   - IDOR (Insecure Direct Object Reference)
   - Privilege escalation
   - Missing access controls

5. **CSRF (Cross-Site Request Forgery)**
   - Token bypass
   - Same-site cookie issues

6. **File Upload Vulnerabilities**
   - Unrestricted file upload
   - Path traversal
   - File inclusion

7. **API Security**
   - Broken authentication
   - Excessive data exposure
   - Rate limiting bypass

8. **Business Logic Flaws**
   - Price manipulation
   - Race conditions
   - Workflow bypass

---

### 4. Difficulty Progression

#### Beginner Level
- **Hints**: 3 hints available
- **Complexity**: Single-step vulnerabilities
- **Examples**: Basic XSS, simple SQLi
- **Points**: 10-50 per challenge

#### Intermediate Level
- **Hints**: 2 hints available
- **Complexity**: Multi-step vulnerabilities
- **Examples**: Blind SQLi, chained XSS
- **Points**: 50-150 per challenge

#### Advanced Level
- **Hints**: 1 hint or none
- **Complexity**: Complex chains, real-world scenarios
- **Examples**: Advanced IDOR, race conditions
- **Points**: 150-500 per challenge

---

### 5. Automated Feedback System

**Validation Logic**:
```python
def validate_simulation_report(report, challenge):
    feedback = []
    is_correct = False
    points = 0
    
    # Check if vulnerability type matches
    if challenge.vulnerability_type in report.description.lower():
        feedback.append("✓ Correct vulnerability type identified")
        points += 20
    else:
        feedback.append("✗ Vulnerability type not correctly identified")
    
    # Check if PoC is provided
    if report.proof_of_concept:
        feedback.append("✓ Proof of concept provided")
        points += 30
    else:
        feedback.append("⚠ Consider adding proof of concept")
    
    # Check severity assessment
    if report.suggested_severity == challenge.expected_severity:
        feedback.append("✓ Correct severity assessment")
        points += 20
    else:
        feedback.append(f"⚠ Expected severity: {challenge.expected_severity}")
    
    # Check impact assessment
    if len(report.impact_assessment) > 100:
        feedback.append("✓ Detailed impact assessment")
        points += 15
    else:
        feedback.append("⚠ Impact assessment could be more detailed")
    
    # Check steps to reproduce
    if len(report.steps_to_reproduce) > 50:
        feedback.append("✓ Clear reproduction steps")
        points += 15
    else:
        feedback.append("⚠ Reproduction steps need more detail")
    
    # Determine if correct
    is_correct = points >= 70  # 70% threshold
    
    return {
        "is_correct": is_correct,
        "points_awarded": points if is_correct else 0,
        "feedback": "\n".join(feedback),
        "hints_for_improvement": generate_hints(report, challenge)
    }
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Create database models
- [ ] Create simulation service
- [ ] Build challenge management
- [ ] Implement data isolation

### Phase 2: Challenge System (Week 3-4)
- [ ] Create 10 beginner challenges
- [ ] Create 10 intermediate challenges
- [ ] Create 5 advanced challenges
- [ ] Implement hint system

### Phase 3: Report Validation (Week 5)
- [ ] Build automated validation
- [ ] Implement feedback system
- [ ] Create learning resources
- [ ] Progress tracking

### Phase 4: Gamification (Week 6)
- [ ] Points system
- [ ] Leaderboard
- [ ] Badges/achievements
- [ ] User dashboard

### Phase 5: UI/UX (Week 7-8)
- [ ] Simulation mode toggle
- [ ] Challenge browser
- [ ] Progress dashboard
- [ ] Learning resources page

---

## API Endpoints

### Simulation Programs
- `GET /api/v1/simulation/programs` - List all simulation programs
- `GET /api/v1/simulation/programs/{id}` - Get program details
- `GET /api/v1/simulation/programs/{id}/challenges` - List challenges

### Challenges
- `GET /api/v1/simulation/challenges` - List all challenges
- `GET /api/v1/simulation/challenges/{id}` - Get challenge details
- `POST /api/v1/simulation/challenges/{id}/start` - Start a challenge
- `POST /api/v1/simulation/challenges/{id}/hint` - Request a hint

### Reports
- `POST /api/v1/simulation/reports` - Submit simulation report
- `GET /api/v1/simulation/reports/{id}` - Get report with feedback
- `GET /api/v1/simulation/my-reports` - List user's simulation reports

### Progress
- `GET /api/v1/simulation/progress` - Get user progress
- `GET /api/v1/simulation/leaderboard` - Get leaderboard
- `GET /api/v1/simulation/stats` - Get user statistics

---

## Sample Challenges

### Challenge 1: Reflected XSS (Beginner)
**Title**: "Cookie Stealer"  
**Description**: Find and exploit a reflected XSS vulnerability in the search feature.  
**Difficulty**: Beginner  
**Points**: 25  
**Hint 1**: Look at how the search parameter is displayed on the page  
**Hint 2**: Try injecting HTML tags in the search box  
**Hint 3**: Use `<script>alert(document.cookie)</script>`

### Challenge 2: SQL Injection (Intermediate)
**Title**: "Database Dumper"  
**Description**: Extract sensitive data using SQL injection in the login form.  
**Difficulty**: Intermediate  
**Points**: 100  
**Hint 1**: The login form doesn't properly sanitize inputs  
**Hint 2**: Try using `' OR '1'='1` in the username field

### Challenge 3: IDOR (Advanced)
**Title**: "Account Takeover"  
**Description**: Access another user's account by exploiting an IDOR vulnerability.  
**Difficulty**: Advanced  
**Points**: 250  
**Hint 1**: Look at how user IDs are passed in API requests

---

## UI/UX Considerations

### Clear Distinction from Real Platform
- **Visual Indicator**: Orange/yellow banner "SIMULATION MODE"
- **Separate Navigation**: Dedicated "Learning Lab" section
- **Virtual Currency**: Display "Learning Points" instead of real money
- **No Real Impact**: Clear messaging that this is practice

### User Experience
- **Onboarding**: Tutorial for first-time users
- **Progress Tracking**: Visual progress bars
- **Achievements**: Badges for milestones
- **Community**: Discussion forums for challenges

---

## Security Considerations

### Data Isolation
- Separate database tables with `simulation_` prefix
- No foreign keys to real program tables
- Clear API endpoint separation (`/simulation/*`)
- Separate service layer

### Vulnerable Code Safety
- Sandboxed execution
- No access to real user data
- Rate limiting on challenge attempts
- Input validation (even for vulnerable endpoints)

---

## Success Metrics

### User Engagement
- Number of active learners
- Challenges completed per user
- Time spent in simulation mode
- Return rate

### Learning Effectiveness
- Improvement in report quality
- Progression through difficulty levels
- Hint usage patterns
- Success rate per challenge

---

## Future Enhancements

### Phase 2 Features
- [ ] Mobile app challenges
- [ ] API security challenges
- [ ] Cloud security scenarios
- [ ] Social engineering simulations

### Phase 3 Features
- [ ] Custom challenge creation (by admins)
- [ ] Community-contributed challenges
- [ ] Team competitions
- [ ] Certification program

---

## Related FREQs

- **FREQ-01**: Authentication (users need accounts)
- **FREQ-11**: Reputation System (can integrate with learning points)
- **FREQ-13**: Dashboards (simulation progress dashboard)
- **FREQ-15**: Analytics (learning analytics)

---

**Next Steps**: 
1. Review and approve architecture
2. Create database migration
3. Implement core models and services
4. Build first 5 challenges as MVP
5. Create API endpoints
6. Build UI components

---

**Estimated Effort**: 8-10 weeks for full implementation  
**MVP Effort**: 3-4 weeks (10 challenges, basic feedback)
