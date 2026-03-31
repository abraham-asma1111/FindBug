"""
Pytest configuration for integration tests
"""

import pytest
import asyncio
import sys
import os

# Add paths for both main and simulation platforms
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'simulation', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def databases():
    """Setup both main and simulation databases"""
    from src.core.database import get_db, Base
    from simulation.core.database import get_db as get_sim_db
    from simulation.core.database import Base as SimBase
    
    # Setup main database
    main_db = get_db()
    Base.metadata.create_all(bind=main_db.bind)
    
    # Setup simulation database
    sim_db = get_sim_db()
    SimBase.metadata.create_all(bind=sim_db.bind)
    
    yield {
        'main_db': main_db,
        'simulation_db': sim_db
    }
    
    # Cleanup
    Base.metadata.drop_all(bind=main_db.bind)
    SimBase.metadata.drop_all(bind=sim_db.bind)

@pytest.fixture
def mock_file_storage():
    """Mock file storage for testing"""
    class MockFileStorage:
        def save_file(self, content, user_id, subfolder):
            return {
                "storage_path": f"mock_uploads/{subfolder}/{user_id}_{hash(content)}.jpg",
                "size": len(content)
            }
        
        def get_file_info(self, file_id):
            return {
                "filename": f"test_file_{file_id}.jpg",
                "size": 1024,
                "content_type": "image/jpeg"
            }
        
        def delete_file(self, file_id, user_id):
            return True
    
    return MockFileStorage()

@pytest.fixture
def mock_email_service():
    """Mock email service for testing"""
    class MockEmailService:
        def send_html_email(self, to_email, subject, html_body, text_body=None):
            return True
    
    return MockEmailService()

@pytest.fixture
def test_data():
    """Common test data"""
    return {
        'test_user': {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'full_name': 'Test User',
            'role': 'researcher'
        },
        'test_organization': {
            'email': 'org@example.com',
            'password': 'TestPass123!',
            'full_name': 'Test Organization',
            'role': 'organization',
            'company_name': 'Test Company'
        },
        'test_admin': {
            'email': 'admin@example.com',
            'password': 'AdminPass123!',
            'full_name': 'Test Admin',
            'role': 'admin'
        }
    }
