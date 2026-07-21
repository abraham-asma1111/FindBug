"""Test script to verify bulk action endpoint fix."""
import requests
import json

# This script demonstrates the correct way to call the bulk action endpoint
# Run this after starting the backend server

API_URL = "http://127.0.0.1:8002/api/v1"

def test_bulk_action_endpoint():
    """
    Test the bulk action endpoint with correct request format.
    
    The endpoint expects:
    - researcher_id: in URL path
    - action: as query parameter
    - duplicate_of: as query parameter (optional)
    - report_ids: as JSON array in request body
    """
    
    # Example request
    researcher_id = "some-uuid-here"
    report_ids = [
        "report-uuid-1",
        "report-uuid-2",
        "report-uuid-3"
    ]
    
    # Build URL with query parameters
    url = f"{API_URL}/triage/researchers/{researcher_id}/reports/bulk-action"
    params = {
        "action": "mark_invalid"
    }
    
    # Send report IDs as JSON array in body
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN_HERE"
    }
    
    print("Request URL:", url)
    print("Query params:", params)
    print("Request body:", json.dumps(report_ids, indent=2))
    print("\nExpected backend signature:")
    print("  - researcher_id: UUID (path parameter)")
    print("  - action: str (query parameter)")
    print("  - duplicate_of: Optional[UUID] (query parameter)")
    print("  - report_ids: List[UUID] = Body(...) (request body)")
    
    # Uncomment to actually make the request:
    # response = requests.post(url, params=params, json=report_ids, headers=headers)
    # print("\nResponse:", response.status_code)
    # print(response.json())

if __name__ == "__main__":
    test_bulk_action_endpoint()
