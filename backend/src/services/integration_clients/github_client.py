"""
GitHub API Client for SSDLC Integration
Implements bi-directional sync with GitHub Issues
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for issue synchronization"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize GitHub client
        
        Args:
            config: GitHub configuration with token, owner, repo
        """
        self.token = config.get("token")
        self.owner = config.get("owner")
        self.repo = config.get("repo")
        self.base_url = config.get("base_url", "https://api.github.com")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def create_issue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create GitHub issue from vulnerability report
        
        Args:
            payload: Issue data (title, body, labels, assignees)
            
        Returns:
            Created issue data with issue number
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        
        issue_data = {
            "title": payload.get("title"),
            "body": payload.get("body"),
            "labels": payload.get("labels", ["vulnerability"]),
            "assignees": payload.get("assignees", [])
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=issue_data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            issue = response.json()
            logger.info(f"Created GitHub issue #{issue['number']}")
            
            return {
                "external_id": str(issue["number"]),
                "external_url": issue["html_url"],
                "state": issue["state"],
                "created_at": issue["created_at"]
            }
    
    async def update_issue(
        self,
        issue_number: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing GitHub issue
        
        Args:
            issue_number: GitHub issue number
            payload: Updated issue data
            
        Returns:
            Updated issue data
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        update_data = {}
        if "title" in payload:
            update_data["title"] = payload["title"]
        if "body" in payload:
            update_data["body"] = payload["body"]
        if "state" in payload:
            update_data["state"] = payload["state"]
        if "labels" in payload:
            update_data["labels"] = payload["labels"]
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                json=update_data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            issue = response.json()
            logger.info(f"Updated GitHub issue #{issue_number}")
            
            return {
                "external_id": str(issue["number"]),
                "external_url": issue["html_url"],
                "state": issue["state"],
                "updated_at": issue["updated_at"]
            }
    
    async def close_issue(self, issue_number: str) -> Dict[str, Any]:
        """
        Close GitHub issue
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Closed issue data
        """
        return await self.update_issue(issue_number, {"state": "closed"})
    
    async def get_issue(self, issue_number: str) -> Dict[str, Any]:
        """
        Get GitHub issue details
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Issue data
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            issue = response.json()
            return {
                "external_id": str(issue["number"]),
                "title": issue["title"],
                "body": issue["body"],
                "state": issue["state"],
                "labels": [label["name"] for label in issue.get("labels", [])],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "closed_at": issue.get("closed_at")
            }
    
    async def add_comment(
        self,
        issue_number: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add comment to GitHub issue
        
        Args:
            issue_number: GitHub issue number
            comment: Comment text
            
        Returns:
            Comment data
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"body": comment},
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            comment_data = response.json()
            logger.info(f"Added comment to GitHub issue #{issue_number}")
            
            return {
                "comment_id": str(comment_data["id"]),
                "created_at": comment_data["created_at"]
            }
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify GitHub webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: X-Hub-Signature-256 header value
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        
        if not signature or not signature.startswith("sha256="):
            return False
        
        expected_signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
