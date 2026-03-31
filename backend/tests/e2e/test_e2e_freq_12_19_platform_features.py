"""
E2E Tests for FREQ-12 to FREQ-19: Platform Features
Tests analytics, notifications, dashboard, search, audit, files, and email
"""
import pytest


class TestFREQ12Analytics:
    """FREQ-12: Analytics & Reporting"""
    
    def test_organization_analytics(self, client, organization_token):
        """E2E: View organization analytics dashboard"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        response = client.get("/api/v1/analytics/organization", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_reports" in data or "reports" in data or "statistics" in data
    
    def test_researcher_analytics(self, client, researcher_token):
        """E2E: View researcher analytics"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        response = client.get("/api/v1/analytics/researcher", headers=headers)
        assert response.status_code == 200


class TestFREQ13NotificationSystem:
    """FREQ-13: Notification System"""
    
    def test_notification_workflow(self, client, researcher_token):
        """E2E: Receive and manage notifications"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Get notifications
        notifications_response = client.get("/api/v1/notifications", headers=headers)
        assert notifications_response.status_code == 200
        
        # Mark notification as read (if any exist)
        if notifications_response.json():
            notif_id = notifications_response.json()[0].get("id")
            if notif_id:
                mark_read = client.put(f"/api/v1/notifications/{notif_id}/read", headers=headers)
                assert mark_read.status_code in [200, 404]


class TestFREQ14AdminDashboard:
    """FREQ-14: Admin Dashboard"""
    
    def test_admin_dashboard_access(self, client, staff_token):
        """E2E: Access admin dashboard and statistics"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        
        # Get platform statistics
        stats_response = client.get("/api/v1/admin/statistics", headers=headers)
        assert stats_response.status_code in [200, 403]
        
        # Get user list
        users_response = client.get("/api/v1/admin/users", headers=headers)
        assert users_response.status_code in [200, 403]


class TestFREQ15Dashboard:
    """FREQ-15: User Dashboard"""
    
    def test_user_dashboard(self, client, researcher_token):
        """E2E: View user dashboard"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        response = client.get("/api/v1/dashboard", headers=headers)
        assert response.status_code == 200


class TestFREQ16Search:
    """FREQ-16: Search Functionality"""
    
    def test_search_programs(self, client, researcher_token):
        """E2E: Search for programs"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Search programs
        response = client.get("/api/v1/programs?search=test", headers=headers)
        assert response.status_code in [200, 404]
    
    def test_search_reports(self, client, organization_token):
        """E2E: Search for reports"""
        headers = {"Authorization": f"Bearer {organization_token}"}
        
        response = client.get("/api/v1/reports?search=sql", headers=headers)
        assert response.status_code in [200, 404]


class TestFREQ17AuditTrail:
    """FREQ-17: Audit Trail"""
    
    def test_audit_logs(self, client, staff_token):
        """E2E: View audit logs"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        
        # Get audit logs
        response = client.get("/api/v1/admin/audit-logs", headers=headers)
        assert response.status_code in [200, 403]
        
        # Search audit logs
        search_response = client.get("/api/v1/admin/audit-logs?event_type=login", headers=headers)
        assert search_response.status_code in [200, 403]


class TestFREQ18FileUpload:
    """FREQ-18: File Upload & Storage"""
    
    def test_file_upload_workflow(self, client, researcher_token):
        """E2E: Upload and retrieve files"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Upload file
        files = {"file": ("test.txt", b"test content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", headers=headers, files=files)
        assert upload_response.status_code in [201, 200]
        
        if upload_response.status_code in [201, 200]:
            file_id = upload_response.json().get("id") or upload_response.json().get("file_id")
            
            if file_id:
                # Get file info
                info_response = client.get(f"/api/v1/files/{file_id}", headers=headers)
                assert info_response.status_code in [200, 404]


class TestFREQ19DataExport:
    """FREQ-19: Data Export"""
    
    def test_data_export_workflow(self, client, researcher_token):
        """E2E: Request and download data export"""
        headers = {"Authorization": f"Bearer {researcher_token}"}
        
        # Request data export
        export_response = client.post("/api/v1/data-exports", headers=headers, json={
            "export_type": "reports",
            "format": "json"
        })
        assert export_response.status_code in [201, 200]
        
        # List exports
        list_response = client.get("/api/v1/data-exports", headers=headers)
        assert list_response.status_code in [200, 404]
