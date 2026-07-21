#!/usr/bin/env python3
"""
Create SQL Injection Challenge for the Simulation Platform
Points to the existing lab-app at /challenges/sql-injection
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.simulation import SimulationChallenge
import json

def create_sqli_challenge():
    db: Session = SessionLocal()
    
    try:
        # Check if challenge already exists
        existing = db.query(SimulationChallenge).filter(
            SimulationChallenge.vulnerability_type == "sql-injection"
        ).first()
        
        if existing:
            print(f"✅ SQL Injection challenge already exists!")
            print(f"   ID: {existing.id}")
            print(f"   Name: {existing.name}")
            print(f"   Access at: http://localhost:3000/researcher/simulation/labs")
            return
        
        # Create the challenge
        challenge = SimulationChallenge(
            name="PayFlow HR Portal - SQL Injection",
            description="""Bypass the employee login portal using SQL injection. The PayFlow HR system uses unsafe string concatenation to build SQL queries.

**Objective:** Access the admin panel without valid credentials.

**Scenario:** You're testing a payroll SaaS application. The login form is vulnerable to SQL injection.

**Success:** You'll see "Congratulations! You solved the lab" when you successfully bypass authentication.""",
            category="web",
            vulnerability_type="sql-injection",
            difficulty_level="beginner",
            severity="critical",
            points=100,
            estimated_time_minutes=15,
            docker_image="findbug-academy-lab:latest",
            exposed_port=5050,
            documentation="""# SQL Injection Authentication Bypass

## What is SQL Injection?
SQL Injection is a code injection technique that exploits security vulnerabilities in database queries.

## The Vulnerability
The login form constructs SQL queries using string concatenation:

```sql
SELECT * FROM users WHERE username='{username}' AND password='{password}'
```

## How to Exploit
Inject SQL syntax to manipulate the query logic:

**Payload:** `admin'--` or `admin' OR '1'='1'--`

This transforms the query to:
```sql
SELECT * FROM users WHERE username='admin'--' AND password='...'
```

The `--` comments out the password check!

## Steps:
1. Enter `admin'--` in the username field
2. Enter anything in the password field  
3. Click Login
4. Success! You've bypassed authentication

## Real-World Impact
- Unauthorized access to sensitive data
- Data theft or manipulation
- Complete system compromise
- OWASP Top 10 #1 vulnerability""",
            external_resources=json.dumps([
                {"title": "OWASP SQL Injection", "url": "https://owasp.org/www-community/attacks/SQL_Injection"},
                {"title": "PortSwigger SQL Injection", "url": "https://portswigger.net/web-security/sql-injection"}
            ]),
            hints=json.dumps([
                "The login query uses string concatenation. What happens if you add a single quote (') to your input?",
                "SQL comments start with --. Can you use this to ignore the password check?",
                "Try: admin'-- as the username. The -- will comment out everything after it!"
            ]),
            hint_costs=json.dumps([0, 0, 5]),  # First 2 hints free, 3rd costs 5 XP
            validation_keywords=json.dumps([
                "sql injection",
                "authentication bypass",
                "admin'--",
                "admin' OR '1'='1'--",
                "sqli",
                "string concatenation"
            ]),
            expected_vulnerability_type="SQL Injection",
            expected_severity="critical",
            official_solution="""**Solution:**

1. In the username field, enter: `admin'--`
2. In the password field, enter anything (e.g., `test`)
3. Click "Login"

**Why it works:**
The SQL query becomes:
```sql
SELECT * FROM users WHERE username='admin'--' AND password='test'
```

The `--` comments out the password check, so the query only checks if username='admin' exists.

**Alternative payloads:**
- `admin' OR '1'='1'--`
- `' OR '1'='1'--`
- `admin'#` (MySQL comment)

**Flag:** You'll see a success message with the flag when you solve it!""",
            is_active=True,
            is_published=True,
            total_attempts=0,
            total_completions=0
        )
        
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
        print(f"✅ SQL Injection challenge created successfully!")
        print(f"   ID: {challenge.id}")
        print(f"   Name: {challenge.name}")
        print(f"   Category: {challenge.category}")
        print(f"   Difficulty: {challenge.difficulty_level}")
        print(f"   Points: {challenge.points}")
        print(f"\n🎯 How to access:")
        print(f"   1. Start the lab environment: docker compose -f simulation/docker-compose.yml up -d")
        print(f"   2. Navigate to: http://localhost:3000/researcher/simulation/labs")
        print(f"   3. Select 'PayFlow HR Portal - SQL Injection' from the menu")
        print(f"   4. Try the payload: admin'-- in the username field")
        print(f"\n🚀 The lab is already built into the academy at /challenges/sql-injection")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating challenge: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_sqli_challenge()
