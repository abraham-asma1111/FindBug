"""
Jira API Client for SSDLC Integration
Implements bi-directional sync with Jira Issues
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class JiraClient:
    """Jira API client for issue synchronization"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Jira client
        
        Args:
            config: Jira configuration with url, email, api_token, project_key
        """
        self.base_url = config.get("url")
        self.email = config.get("email")
        self.api_token = config.get("api_token")
        self.project_key = config.get("project_key")
        
        # Basic auth for Jira Cloud
        auth_string = f"{self.email}:{self.api_token}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def create_issue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Jira issue from vulnerability report
        
        Args:
            payload: Issue data (summary, description, priority, issue_type)
            
        Returns:
            Created issue data with issue key
        """
        url = f"{self.base_url}/rest/api/3/issue"
        
        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": payload.get("summary"),
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": payload.get("description", "")
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": payload.get("issue_type", "Bug")},
                "priority": {"name": payload.get("priority", "Medium")},
                "labels": payload.get("labels", ["vulnerability"])
            }
        }
        
        # Add assignee if provided
        if payload.get("assignee"):
            issue_data["fields"]["assignee"] = {"accountId": payload["assignee"]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=issue_data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            issue = response.json()
            logger.info(f"Created Jira issue {issue['key']}")
            
            return {
                "external_id": issue["key"],
                "external_url": f"{self.base_url}/browse/{issue['key']}",
                "issue_id": issue["id"]
            }
    
    async def update_issue(
        self,
        issue_key: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing Jira issue
        
        Args:
            issue_key: Jira issue key (e.g., PROJ-123)
            payload: Updated issue data
            
        Returns:
            Updated issue data
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        update_data = {"fields": {}}
        
        if "summary" in payload:
            update_data["fields"]["summary"] = payload["summary"]
        
        if "description" in payload:
            update_data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": payload["description"]
                            }
                        ]
                    }
                ]
            }
        
        if "priority" in payload:
            update_data["fields"]["priority"] = {"name": payload["priority"]}
        
        if "labels" in payload:
            update_data["fields"]["labels"] = payload["labels"]
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=update_data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            logger.info(f"Updated Jira issue {issue_key}")
            
            return {
                "external_id": issue_key,
                "external_url": f"{self.base_url}/browse/{issue_key}"
            }
    
    async def transition_issue(
        self,
        issue_key: str,
        transition_name: str
    ) -> Dict[str, Any]:
        """
        Transition Jira issue to new status
        
        Args:
            issue_key: Jira issue key
            transition_name: Transition name (e.g., "Done", "In Progress")
            
        Returns:
            Transition result
        """
        # Get available transitions
        transitions_url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                transitions_url,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            transitions = response.json()["transitions"]
            transition_id = None
            
            for transition in transitions:
                if transition["name"].lower() == transition_name.lower():
                    transition_id = transition["id"]
                    break
            
            if not transition_id:
                raise ValueError(f"Transition '{transition_name}' not found")
            
            # Execute transition
            response = await client.post(
                transitions_url,
                json={"transition": {"id": transition_id}},
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            logger.info(f"Transitioned Jira issue {issue_key} to {transition_name}")
            
            return {
                "external_id": issue_key,
                "status": transition_name
            }
    
    async def close_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Close Jira issue
        
        Args:
            issue_key: Jira issue key
            
        Returns:
            Closed issue data
        """
        return await self.transition_issue(issue_key, "Done")
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get Jira issue details
        
        Args:
            issue_key: Jira issue key
            
        Returns:
            Issue data
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            issue = response.json()
            fields = issue["fields"]
            
            return {
                "external_id": issue["key"],
                "summary": fields.get("summary"),
                "description": self._extract_description(fields.get("description")),
                "status": fields.get("status", {}).get("name"),
                "priority": fields.get("priority", {}).get("name"),
                "labels": fields.get("labels", []),
                "created": fields.get("created"),
                "updated": fields.get("updated")
            }
    
    async def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add comment to Jira issue
        
        Args:
            issue_key: Jira issue key
            comment: Comment text
            
        Returns:
            Comment data
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=comment_data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            comment_result = response.json()
            logger.info(f"Added comment to Jira issue {issue_key}")
            
            return {
                "comment_id": comment_result["id"],
                "created": comment_result["created"]
            }
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify Jira webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        
        if not signature or not secret:
            return False
        
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _extract_description(self, description: Optional[Dict]) -> str:
        """Extract plain text from Jira ADF description"""
        if not description:
            return ""
        
        text_parts = []
        for content in description.get("content", []):
            if content.get("type") == "paragraph":
                for item in content.get("content", []):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
        
        return " ".join(text_parts)
