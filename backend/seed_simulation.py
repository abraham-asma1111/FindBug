"""
Seed script for simulation challenges
"""
import os, sys
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')
os.chdir('/home/abraham/Desktop/Final-year-project/backend')

from dotenv import load_dotenv
load_dotenv()

from src.core.database import SessionLocal
from sqlalchemy import text
import json, uuid
from pathlib import Path

db = SessionLocal()

THEORY_FILE = Path(__file__).resolve().parent.parent / "simulation" / "challenge_theory.json"
CHALLENGE_THEORY = {}
if THEORY_FILE.exists():
    CHALLENGE_THEORY = json.loads(THEORY_FILE.read_text(encoding="utf-8"))

challenges = [
    {
        "id": str(uuid.uuid4()),
        "name": "PayFlow HR Portal (SQL Injection)",
        "description": "PayFlow is a payroll SaaS used by Ethiopian enterprises. Bypass the employee portal login (legacy auth service) to access the HR payroll dashboard.",
        "category": "web",
        "vulnerability_type": "sql_injection",
        "difficulty_level": "beginner",
        "severity": "high",
        "points": 100,
        "estimated_time_minutes": 30,
        "docker_image": "findbug/academy-lab",
        "tutorial_video_url": "https://www.youtube.com/embed/ciNHn38EyRc",
        "documentation": """## SQL Injection\n\nSQL Injection is a web security vulnerability that allows an attacker to interfere with the queries an application makes to its database.\n\n### How it works\nWhen user input is directly concatenated into SQL queries without sanitization, an attacker can inject malicious SQL code.\n\n### Attack Example\n```sql\n-- Injected payload:\nadmin' --\n```\n\n### OWASP Reference\nOWASP Top 10: A03:2021 - Injection\nhttps://owasp.org/Top10/A03_2021-Injection/""",
        "external_resources": json.dumps([{"title": "OWASP SQL Injection Cheat Sheet", "url": "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"}]),
        "hints": json.dumps([
            "Which login fields are sent to the payroll auth service?",
            "Try a single quote in the work email field to break SQL syntax.",
            "The query likely concatenates email — use comment termination.",
            "Payload: admin'-- in the work email field.",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 10, "3": 15}),
        "official_solution": "On PayFlow portal, use `admin'--` in the work email field to bypass authentication and reach the payroll dashboard.",
        "expected_vulnerability_type": "sql_injection",
        "expected_severity": "high",
        "validation_keywords": json.dumps(["sql", "injection", "sqli", "admin"]),
        "is_published": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "TechHive Market (Reflected XSS)",
        "description": "TechHive Market is a B2C storefront. Shoppers search for products by name (headphones, keyboard, webcam, etc.). The search results page reflects the query without encoding — find reflected XSS in the product search flow.",
        "category": "web",
        "vulnerability_type": "xss",
        "difficulty_level": "beginner",
        "severity": "medium",
        "points": 80,
        "estimated_time_minutes": 25,
        "docker_image": "findbug/academy-lab",
        "exposed_port": 5050,
        "tutorial_video_url": "https://www.youtube.com/embed/EoaDgUgS6QA",
        "documentation": """## Cross-Site Scripting (XSS)\n\nXSS allows attackers to inject malicious scripts into web pages viewed by other users.\n\n### Reflected XSS\nThe malicious script comes from the current HTTP request.\n\n### Basic Payloads\n```html\n<script>alert(1)</script>\n<img src=x onerror=alert(1)>\n<svg onload=alert(1)>\n```\n\n### OWASP Reference\nhttps://owasp.org/Top10/A03_2021-Injection/""",
        "external_resources": json.dumps([{"title": "XSS Payload List", "url": "https://github.com/payloadbox/xss-payload-list"}]),
        "hints": json.dumps([
            "Use the product search bar like a real shopper.",
            "Is your search term reflected on the results page?",
            "Reflected XSS needs HTML/JS — try event handlers or script tags.",
            "Payload: <script>alert(1)</script> in the search box.",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 10, "3": 15}),
        "official_solution": "On TechHive Market, search for `<script>alert(1)</script>`. The storefront reflects the term in the results banner and empty-state HTML without encoding, executing the script.",
        "expected_vulnerability_type": "xss",
        "expected_severity": "medium",
        "validation_keywords": json.dumps(["xss", "script", "reflected", "alert"]),
        "is_published": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "NovaBank Settlement API (JWT)",
        "description": "NovaBank's open banking staging console exposes a signing key. Forge a JWT with platform_admin role to call GET /v1/settlements/export.",
        "category": "api",
        "vulnerability_type": "jwt_attack",
        "difficulty_level": "intermediate",
        "severity": "critical",
        "points": 200,
        "estimated_time_minutes": 45,
        "docker_image": "findbug/academy-lab",
        "tutorial_video_url": "https://www.youtube.com/embed/7rmCB-cMBW8",
        "documentation": """## JWT Algorithm Confusion\n\nJSON Web Tokens (JWT) can be vulnerable when the server accepts algorithm changes from the client.\n\n### The Attack\n1. Decode the JWT (base64)\n2. Modify the header: `{"alg":"none"}`\n3. Modify payload: `{"role":"admin"}`\n4. Remove the signature\n5. Send forged token\n\n### OWASP Reference\nOWASP API Security: API2:2023 - Broken Authentication""",
        "external_resources": json.dumps([{"title": "PortSwigger JWT Attacks", "url": "https://portswigger.net/web-security/jwt"}]),
        "hints": json.dumps([
            "Read the leaked staging secret on the developer console.",
            "Decode the sample merchant JWT at jwt.io.",
            "Change the role claim to platform_admin in the payload.",
            "Re-sign with HS256 using the leaked staging secret.",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 15, "3": 20}),
        "official_solution": "Forge HS256 JWT with role platform_admin using the leaked staging secret; paste into Export settlements to unlock the simulated settlement file.",
        "expected_vulnerability_type": "jwt_attack",
        "expected_severity": "critical",
        "validation_keywords": json.dumps(["jwt", "token", "platform_admin", "settlement", "novabank"]),
        "is_published": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "InvoiceFlow Supplier Verify (SSRF)",
        "description": "InvoiceFlow AP team previews supplier URLs before large wire transfers. Abuse the compliance preview worker to reach internal or cloud metadata endpoints.",
        "category": "web",
        "vulnerability_type": "ssrf",
        "difficulty_level": "intermediate",
        "severity": "high",
        "points": 180,
        "estimated_time_minutes": 40,
        "docker_image": "findbug/academy-lab",
        "exposed_port": 5050,
        "tutorial_video_url": "https://www.youtube.com/embed/o-tL9ULF0ak",
        "documentation": """## Server-Side Request Forgery (SSRF)\n\nSSRF allows attackers to induce the server to make requests to unintended locations.\n\n### Common Targets\n- Internal: `http://127.0.0.1:5050/internal` (lab sandbox only)\n- Cloud metadata: `http://169.254.169.254/latest/meta-data/`\n\n### OWASP Reference\nOWASP Top 10: A10:2021 - SSRF\nhttps://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/""",
        "external_resources": json.dumps([{"title": "PortSwigger SSRF Labs", "url": "https://portswigger.net/web-security/ssrf"}]),
        "hints": json.dumps([
            "Submit a normal supplier HTTPS URL first.",
            "The preview worker fetches whatever URL you supply server-side.",
            "Try loopback or RFC1918 hosts the worker can reach.",
            "Target: http://169.254.169.254/latest/meta-data/",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 15, "3": 20}),
        "official_solution": "In supplier URL field use internal IP or `http://169.254.169.254/latest/meta-data/` to demonstrate SSRF in the compliance preview output.",
        "expected_vulnerability_type": "ssrf",
        "expected_severity": "high",
        "validation_keywords": json.dumps(["ssrf", "169.254", "metadata", "internal"]),
        "is_published": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "CloudStack Partner Connect (OAuth)",
        "description": "CloudStack OAuth consent for InvoiceFlow CRM. Weak redirect_uri validation lets you capture the authorization code on an attacker host.",
        "category": "api",
        "vulnerability_type": "oauth_abuse",
        "difficulty_level": "advanced",
        "severity": "critical",
        "points": 350,
        "estimated_time_minutes": 75,
        "docker_image": "findbug/academy-lab",
        "tutorial_video_url": "https://www.youtube.com/embed/996OiexHze0",
        "documentation": """## OAuth 2.0 Authorization Code Interception\n\n### The Flaw\nWeak redirect_uri validation allows an attacker to redirect the authorization code to their server.\n\n### Attack Chain\n1. Craft malicious OAuth link with manipulated redirect_uri\n2. Trick victim into clicking it\n3. Server redirects code to attacker server\n4. Attacker exchanges code for access token\n\n### OWASP Reference\nOWASP API: API1:2023 - Broken Object Level Authorization""",
        "external_resources": json.dumps([{"title": "PortSwigger OAuth Attacks", "url": "https://portswigger.net/web-security/oauth"}]),
        "hints": json.dumps([
            "This mirrors Slack/Google-style B2B OAuth connect.",
            "redirect_uri is attacker-controlled in this lab.",
            "Approve and watch where the browser is sent with ?code=.",
            "Use https://attacker.example/capture as redirect_uri.",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 20, "3": 25}),
        "official_solution": "Set redirect_uri to https://attacker.example/capture — authorization code cs_auth_* is shown in the redirect to the attacker URL.",
        "expected_vulnerability_type": "oauth_abuse",
        "expected_severity": "critical",
        "validation_keywords": json.dumps(["oauth", "redirect", "authorization", "token"]),
        "is_published": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "TechHive Checkout (Race Condition)",
        "description": "TechHive flash sale checkout — promo FLASH25 should apply once. Race parallel Apply requests to stack the discount before the server locks the coupon.",
        "category": "web",
        "vulnerability_type": "race_condition",
        "difficulty_level": "advanced",
        "severity": "high",
        "points": 300,
        "estimated_time_minutes": 60,
        "docker_image": "findbug/academy-lab",
        "tutorial_video_url": "https://www.youtube.com/embed/tZ_tS7LyVk0",
        "documentation": """## Race Conditions (TOCTOU)\n\nRace conditions occur when security decisions are based on shared state that changes between check and use.\n\n### Time of Check vs Time of Use\n```\nThread A: Check coupon → valid\nThread B: Check coupon → valid (simultaneously!)\nThread A: Apply coupon → success\nThread B: Apply coupon → success (should have failed!)\n```\n\n### Tools\n- Burp Suite Turbo Intruder\n- Python threading\n\n### OWASP Reference\nOWASP Top 10: A04:2021 - Insecure Design""",
        "external_resources": json.dumps([{"title": "PortSwigger Race Conditions", "url": "https://portswigger.net/web-security/race-conditions"}]),
        "hints": json.dumps([
            "Build the cart like a real shopper (Telebirr/Chapa flow).",
            "Apply FLASH25 once — note the total change.",
            "Race window: check-then-update on promo redeem (~150ms).",
            "Burp Turbo Intruder: 30+ parallel POST /redeem with coupon=FLASH25.",
        ]),
        "hint_costs": json.dumps({"0": 0, "1": 0, "2": 20, "3": 25}),
        "official_solution": "Send 20+ parallel POST /redeem requests with coupon FLASH25 before the first completes; multiple responses may apply the 1500 ETB discount.",
        "expected_vulnerability_type": "race_condition",
        "expected_severity": "high",
        "validation_keywords": json.dumps(["race", "concurrent", "coupon", "timing"]),
        "is_published": True,
    },
]

for c in challenges:
    c.setdefault("exposed_port", 5050)
    c.setdefault("is_active", True)
    theory = CHALLENGE_THEORY.get(c.get("vulnerability_type"), {})
    if theory.get("description"):
        c["description"] = theory["description"]
    if theory.get("documentation"):
        c["documentation"] = theory["documentation"]

for c in challenges:
    db.execute(text("""
        INSERT INTO simulation_challenges 
        (id, name, description, category, vulnerability_type, difficulty_level, severity, points, 
         estimated_time_minutes, docker_image, exposed_port, tutorial_video_url, documentation, external_resources,
         hints, hint_costs, official_solution, expected_vulnerability_type, expected_severity,
         validation_keywords, is_published, is_active)
        VALUES 
        (:id, :name, :description, :category, :vulnerability_type, :difficulty_level, :severity, :points,
         :estimated_time_minutes, :docker_image, :exposed_port, :tutorial_video_url, :documentation, CAST(:external_resources AS jsonb),
         CAST(:hints AS jsonb), CAST(:hint_costs AS jsonb), :official_solution, :expected_vulnerability_type, :expected_severity,
         CAST(:validation_keywords AS jsonb), :is_published, true)
        ON CONFLICT DO NOTHING
    """), c)

db.commit()
db.close()
print(f"Seeded {len(challenges)} simulation challenges successfully!")
