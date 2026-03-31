#!/usr/bin/env python
"""Quick test for matching endpoint"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Register and login
reg = client.post('/api/v1/auth/register/researcher', json={
    'email': 'test@test.com',
    'password': 'Test123!@#',
    'password_confirm': 'Test123!@#',
    'first_name': 'Test',
    'last_name': 'User'
})
print(f'Registration: {reg.status_code}')

login = client.post('/api/v1/auth/login', json={
    'email': 'test@test.com',
    'password': 'Test123!@#'
})
print(f'Login: {login.status_code}')
if login.status_code == 200:
    token = login.json()['access_token']
    print(f'Token: {token[:30]}...')
    
    # Try recommendations
    resp = client.get('/api/v1/matching/recommendations', headers={'Authorization': f'Bearer {token}'})
    print(f'Recommendations status: {resp.status_code}')
    print(f'Response: {resp.text[:500]}')
