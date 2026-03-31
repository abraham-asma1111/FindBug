"""
Simulation Platform API Client
Handles communication with isolated simulation platform
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SimulationAPIClient:
    """HTTP client for simulation platform API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.timeout = 30.0
        self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        use_api_base: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to simulation platform"""
        if use_api_base:
            url = f"{self.api_base}{endpoint}"
        else:
            url = f"{self.base_url}{endpoint}"
            
        client = await self._get_client()
        
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:
                return {"success": True}
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Simulation API HTTP error: {e.response.status_code} - {e.response.text}")
            error_detail = "Simulation platform error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", error_detail)
            except:
                pass
            
            raise SimulationAPIError(
                status_code=e.response.status_code,
                detail=error_detail
            )
            
        except httpx.RequestError as e:
            logger.error(f"Simulation API request error: {str(e)}")
            raise SimulationAPIError(
                status_code=503,
                detail="Simulation platform unavailable"
            )
    
    async def health_check(self) -> bool:
        """Check if simulation platform is healthy"""
        try:
            await self._make_request("GET", "/health", use_api_base=False)
            return True
        except:
            return False
    
    # Challenge Management
    async def get_challenges(
        self, 
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """Get available challenges"""
        params = {"skip": skip, "limit": limit}
        if difficulty:
            params["difficulty"] = difficulty
        if category:
            params["category"] = category
            
        return await self._make_request("GET", "/challenges/challenges/", params=params)
    
    async def get_challenge_details(self, challenge_id: str) -> Dict:
        """Get challenge details"""
        return await self._make_request("GET", f"/challenges/{challenge_id}")
    
    async def start_challenge(self, challenge_id: str, user_id: str) -> Dict:
        """Start challenge container"""
        return await self._make_request(
            "POST", 
            f"/challenges/{challenge_id}/start",
            json={"user_id": user_id}
        )
    
    async def stop_challenge(self, challenge_id: str, user_id: str) -> Dict:
        """Stop challenge container"""
        return await self._make_request(
            "POST",
            f"/challenges/{challenge_id}/stop", 
            json={"user_id": user_id}
        )
    
    # Simulation Management
    async def start_simulation(
        self, 
        user_id: str, 
        target_id: str, 
        level: str
    ) -> Dict:
        """Start simulation session"""
        return await self._make_request(
            "POST",
            "/simulation/start",
            json={
                "user_id": user_id,
                "target_id": target_id,
                "level": level
            }
        )
    
    async def get_simulation(self, simulation_id: str) -> Dict:
        """Get simulation details"""
        return await self._make_request("GET", f"/simulation/{simulation_id}")
    
    async def update_simulation_progress(
        self, 
        simulation_id: str, 
        status: str, 
        current_step: int, 
        time_spent: int
    ) -> Dict:
        """Update simulation progress"""
        return await self._make_request(
            "POST",
            f"/simulation/{simulation_id}/progress",
            json={
                "status": status,
                "current_step": current_step,
                "time_spent": time_spent
            }
        )
    
    # Report Submission
    async def submit_simulation_report(
        self, 
        challenge_id: str, 
        user_id: str,
        report_data: Dict
    ) -> Dict:
        """Submit simulation report for manual triage"""
        payload = {
            "user_id": user_id,
            **report_data
        }
        return await self._make_request(
            "POST",
            f"/challenges/{challenge_id}/submit",
            json=payload
        )
    
    # Scoring and Leaderboard
    async def get_user_scores(self, user_id: str) -> Dict:
        """Get user simulation scores"""
        return await self._make_request("GET", f"/scoring/users/{user_id}")
    
    async def get_leaderboard(
        self, 
        period: str = "weekly",
        limit: int = 100
    ) -> Dict:
        """Get simulation leaderboard"""
        params = {"period": period, "limit": limit}
        return await self._make_request("GET", "/scoring/leaderboard", params=params)
    
    # Isolation Management
    async def create_isolation_session(
        self, 
        user_id: str, 
        target_id: str
    ) -> Dict:
        """Create isolated environment session"""
        return await self._make_request(
            "POST",
            "/isolation/sessions",
            json={
                "user_id": user_id,
                "target_id": target_id
            }
        )
    
    async def get_isolation_session(self, session_id: str) -> Dict:
        """Get isolation session details"""
        return await self._make_request("GET", f"/isolation/sessions/{session_id}")
    
    async def terminate_isolation_session(self, session_id: str) -> Dict:
        """Terminate isolation session"""
        return await self._make_request("DELETE", f"/isolation/sessions/{session_id}")
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


class SimulationAPIError(Exception):
    """Simulation API error"""
    
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Simulation API Error {status_code}: {detail}")


# Global client instance
_simulation_client = None

async def get_simulation_client() -> SimulationAPIClient:
    """Get simulation API client instance"""
    global _simulation_client
    if _simulation_client is None:
        _simulation_client = SimulationAPIClient()
    return _simulation_client

async def close_simulation_client():
    """Close simulation API client"""
    global _simulation_client
    if _simulation_client:
        await _simulation_client.close()
        _simulation_client = None