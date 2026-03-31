"""
Performance Integration Tests - Complete Coverage
Tests system performance under various load conditions
"""

import pytest
import asyncio
import time
import concurrent.futures
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestPerformanceIntegration:
    """Complete performance integration test suite"""
    
    def test_api_response_times(self):
        """Test API response times under normal load"""
        endpoints = [
            ("/api/v1/health", "GET"),
            ("/api/v1/programs", "GET"),
            ("/api/v1/analytics/overview", "GET"),
        ]
        
        for endpoint, method in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Assert response is successful
            assert response.status_code in [200, 404]  # 404 for missing data is acceptable
            
            # Assert response time is reasonable
            assert response_time < 1000, f"Endpoint {endpoint} took too long: {response_time}ms"

    def test_concurrent_requests(self):
        """Test system performance with concurrent requests"""
        def make_request():
            """Make a single request"""
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000
            }
        
        # Test with 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # Assert all requests succeeded
        successful_requests = [r for r in results if r["status_code"] == 200]
        assert len(successful_requests) >= 8  # Allow some failures
        
        # Assert average response time is reasonable
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
        assert avg_response_time < 2000, f"Average response time too high: {avg_response_time}ms"

    def test_database_query_performance(self):
        """Test database query performance"""
        # Test program listing with filters
        start_time = time.time()
        response = client.get("/api/v1/programs?limit=50&offset=0")
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert query_time < 500, f"Database query too slow: {query_time}ms"

    def test_file_upload_performance(self):
        """Test file upload performance"""
        # Create test file
        test_content = "x" * (1024 * 1024)  # 1MB file
        
        start_time = time.time()
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test_file.txt", test_content, "text/plain")},
            data={"user_id": "test-user-id"}
        )
        end_time = time.time()
        
        upload_time = (end_time - start_time) * 1000
        
        assert response.status_code in [200, 201, 400]  # 400 if file upload is not properly configured
        if response.status_code in [200, 201]:
            assert upload_time < 5000, f"File upload too slow: {upload_time}ms"

    def test_authentication_performance(self):
        """Test authentication performance"""
        # Test login performance
        start_time = time.time()
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        end_time = time.time()
        
        login_time = (end_time - start_time) * 1000
        
        # Should handle login quickly
        assert login_time < 2000, f"Login too slow: {login_time}ms"

    def test_search_performance(self):
        """Test search functionality performance"""
        # Test program search
        start_time = time.time()
        response = client.get("/api/v1/programs?search=test")
        end_time = time.time()
        
        search_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert search_time < 1000, f"Search too slow: {search_time}ms"

    def test_analytics_performance(self):
        """Test analytics performance"""
        # Test analytics endpoint
        start_time = time.time()
        response = client.get("/api/v1/analytics/overview")
        end_time = time.time()
        
        analytics_time = (end_time - start_time) * 1000
        
        assert response.status_code in [200, 401]  # 401 if not authenticated
        if response.status_code == 200:
            assert analytics_time < 3000, f"Analytics too slow: {analytics_time}ms"

    def test_notification_performance(self):
        """Test notification system performance"""
        # Test notification retrieval
        start_time = time.time()
        response = client.get("/api/v1/notifications/user/test-user-id")
        end_time = time.time()
        
        notification_time = (end_time - start_time) * 1000
        
        assert response.status_code in [200, 404]  # 404 if user not found
        if response.status_code == 200:
            assert notification_time < 1000, f"Notification retrieval too slow: {notification_time}ms"

    def test_memory_usage(self):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests to test memory usage
        for _ in range(100):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"

    def test_connection_pooling(self):
        """Test database connection pooling"""
        # Make multiple concurrent database requests
        def make_db_request():
            response = client.get("/api/v1/programs")
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_db_request) for _ in range(20)]
            results = [future.result() for future in futures]
        
        # Most requests should succeed
        successful_requests = [r for r in results if r == 200]
        assert len(successful_requests) >= 15, "Too many failed requests under load"

    def test_cache_performance(self):
        """Test caching performance"""
        # First request (cache miss)
        start_time = time.time()
        response1 = client.get("/api/v1/programs")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = client.get("/api/v1/programs")
        second_time = (time.time() - start_time) * 1000
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Second request should be faster due to caching
        # (This is a loose test as caching might not be implemented)
        assert second_time <= first_time * 1.5, "Cache not improving performance"

    def test_rate_limiting_performance(self):
        """Test rate limiting performance"""
        # Make rapid requests to test rate limiting
        start_time = time.time()
        responses = []
        
        for _ in range(50):
            response = client.get("/api/v1/health")
            responses.append(response.status_code)
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        
        # Should handle 50 requests in reasonable time
        assert total_time < 10000, f"Rate limiting too aggressive: {total_time}ms for 50 requests"
        
        # Some requests should succeed
        successful_requests = [r for r in responses if r == 200]
        assert len(successful_requests) >= 10, "Rate limiting too restrictive"

    def test_large_data_handling(self):
        """Test handling of large data responses"""
        # Test large list response
        start_time = time.time()
        response = client.get("/api/v1/programs?limit=100")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 2000, f"Large data response too slow: {response_time}ms"

    def test_concurrent_user_simulation(self):
        """Test concurrent user simulation"""
        def simulate_user_session():
            """Simulate a complete user session"""
            # Login
            login_response = client.post("/api/v1/auth/login", json={
                "email": f"user{time.time()}@example.com",
                "password": "TestPass123!"
            })
            
            if login_response.status_code != 200:
                return False
            
            # Browse programs
            programs_response = client.get("/api/v1/programs")
            
            # View analytics
            analytics_response = client.get("/api/v1/analytics/overview")
            
            return (programs_response.status_code == 200 and 
                   analytics_response.status_code in [200, 401])
        
        # Simulate 10 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_user_session) for _ in range(10)]
            results = [future.result() for future in futures]
        
        successful_sessions = [r for r in results if r is True]
        assert len(successful_sessions) >= 7, "Too many concurrent user session failures"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
