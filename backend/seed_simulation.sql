-- Simulation Challenges Seed Data
INSERT INTO simulation_challenges (name, description, category, vulnerability_type, difficulty_level, severity, points, estimated_time_minutes, docker_image, tutorial_video_url, documentation, hints, hint_costs, official_solution, is_published)
VALUES
(
  'Classic SQL Injection',
  'A login form is vulnerable to SQL injection. The developer forgot to sanitize user input. Can you bypass authentication?',
  'web', 'sql_injection', 'beginner', 'high', 100, 30, 'findbug/academy-lab',
  'https://www.youtube.com/embed/ciNHn38EyRc',
  $doc$## SQL Injection

SQL Injection allows an attacker to interfere with database queries.

### Attack Example
The login query looks like:
```sql
SELECT * FROM users WHERE username = 'INPUT' AND password = 'INPUT'
```
By injecting `admin'--` you close the string and comment out the password check.

### OWASP Reference
OWASP Top 10: A03:2021 - Injection
https://owasp.org/Top10/A03_2021-Injection/$doc$,
  '["Try entering a single quote in the username field.", "Think about how you can close the SQL string early.", "Try the payload: admin'\''--"]'::jsonb,
  '{"0": 0, "1": 5, "2": 10}'::jsonb,
  'Use the payload admin''-- in the username field. This closes the SQL string and comments out the password check, bypassing authentication entirely.',
  true
),
(
  'Reflected Cross-Site Scripting',
  'A search feature reflects user input directly in the page without sanitization. Inject a JavaScript payload that triggers an alert box.',
  'web', 'xss', 'beginner', 'medium', 80, 25, 'findbug/academy-lab',
  'https://www.youtube.com/embed/EoaDgUgS6QA',
  $doc$## Cross-Site Scripting (XSS)

XSS allows attackers to inject malicious scripts into web pages.

### Basic Payloads
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

### OWASP Reference
OWASP Top 10: A03:2021 - Injection
https://owasp.org/Top10/A03_2021-Injection/$doc$,
  '["Look at the URL — is the search term reflected back on the page?", "Try entering HTML tags in the search box.", "Try: <script>alert(1)</script>"]'::jsonb,
  '{"0": 0, "1": 5, "2": 10}'::jsonb,
  'Enter <script>alert(1)</script> in the search box. The server reflects this directly into the HTML response without encoding.',
  true
),
(
  'JWT Algorithm Confusion Attack',
  'The API uses JWT for authentication but accepts the none algorithm. Can you forge an admin JWT token to access privileged endpoints?',
  'api', 'jwt_attack', 'intermediate', 'critical', 200, 45, 'findbug/academy-lab',
  'https://www.youtube.com/embed/7rmCB-cMBW8',
  $doc$## JWT Algorithm Confusion

JSON Web Tokens can be vulnerable when the server accepts algorithm changes.

### The Attack
1. Decode the JWT (base64)
2. Modify header: `{"alg":"none"}`
3. Modify payload: `{"role":"admin"}`
4. Remove the signature
5. Send forged token: `header.payload.`

### OWASP Reference
OWASP API Security: API2:2023 - Broken Authentication$doc$,
  '["Decode the JWT token using jwt.io or base64 decode.", "Look at the algorithm field in the header.", "Try changing alg to none and removing the signature."]'::jsonb,
  '{"0": 0, "1": 10, "2": 15}'::jsonb,
  'Decode JWT, change alg to none in header, change role to admin in payload, re-encode and send with empty signature: header.payload.',
  true
),
(
  'Server-Side Request Forgery',
  'A PDF generation feature accepts a URL parameter. Can you make the server request internal resources and expose the cloud metadata endpoint?',
  'web', 'ssrf', 'intermediate', 'high', 180, 40, 'findbug/academy-lab',
  'https://www.youtube.com/embed/o-tL9ULF0ak',
  $doc$## Server-Side Request Forgery (SSRF)

SSRF allows attackers to induce the server to make requests to unintended locations.

### Common Targets
- Internal: `http://localhost:8080/admin`
- Cloud metadata: `http://169.254.169.254/latest/meta-data/`

### OWASP Reference
OWASP Top 10: A10:2021 - SSRF
https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/$doc$,
  '["The URL parameter accepts external URLs — what about internal IPs?", "Try 127.0.0.1 or localhost instead of the external URL.", "AWS metadata endpoint: http://169.254.169.254/latest/meta-data/"]'::jsonb,
  '{"0": 0, "1": 10, "2": 15}'::jsonb,
  'Change the URL parameter to http://169.254.169.254/latest/meta-data/iam/security-credentials/ to retrieve AWS IAM credentials.',
  true
),
(
  'OAuth 2.0 Authorization Code Interception',
  'A social login has a weak redirect_uri validation. Can you intercept the authorization code and take over another account?',
  'api', 'oauth_abuse', 'advanced', 'critical', 350, 75, 'findbug/academy-lab',
  'https://www.youtube.com/embed/996OiexHze0',
  $doc$## OAuth 2.0 Authorization Code Interception

### The Flaw
Weak redirect_uri validation allows an attacker to redirect the auth code to their server.

### Attack Chain
1. Craft malicious OAuth link with manipulated redirect_uri
2. Trick victim into clicking it
3. Server redirects code to attacker server
4. Attacker exchanges code for access token

### OWASP Reference
OWASP API: API1:2023 - Broken Object Level Authorization$doc$,
  '["Study the OAuth flow — trace all redirects.", "What happens if you change the redirect_uri parameter?", "Look for open redirect vulnerabilities that can be chained."]'::jsonb,
  '{"0": 0, "1": 15, "2": 20}'::jsonb,
  'Modify redirect_uri to attacker-controlled domain. Server uses weak prefix validation. Code is delivered to attacker who exchanges it for an access token.',
  true
),
(
  'Race Condition in Payment Processing',
  'A checkout system is vulnerable to a race condition. Can you redeem the same discount code multiple times by sending concurrent requests?',
  'web', 'race_condition', 'advanced', 'high', 300, 60, 'findbug/academy-lab',
  'https://www.youtube.com/embed/tZ_tS7LyVk0',
  $doc$## Race Conditions (TOCTOU)

Race conditions occur when security decisions are based on state that changes between check and use.

### Time of Check vs Time of Use
```
Thread A: Check coupon → valid
Thread B: Check coupon → valid  (simultaneously!)
Thread A: Apply coupon → success
Thread B: Apply coupon → success  (should have failed!)
```

### Tools
- Burp Suite Turbo Intruder
- Python threading

### OWASP Reference
OWASP Top 10: A04:2021 - Insecure Design$doc$,
  '["The check and deduction happen separately — can they be exploited?", "Try sending multiple requests simultaneously using Burp Repeater.", "Use Turbo Intruder to send 10+ requests in the same millisecond."]'::jsonb,
  '{"0": 0, "1": 15, "2": 20}'::jsonb,
  'Send 20 coupon redemption requests simultaneously with Turbo Intruder. Multiple requests pass the already-used check before any marks it used.',
  true
)
ON CONFLICT DO NOTHING;
