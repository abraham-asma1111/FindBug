"""
Simulation Subplatform Integration Tests - Complete Coverage
Tests all simulation FREQs with comprehensive validation
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
import sys
import os

# Add simulation src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'simulation', 'src'))

from simulation.core.database import get_db as get_sim_db
from simulation.domain.models.simulation import Simulation, SimulationTarget, SimulationChallenge
from simulation.services.simulation_service import SimulationService

class TestSimulationIntegration:
    """Complete simulation integration test suite"""
    
    @pytest.fixture(autouse=True)
    def setup_simulation_database(self):
        """Setup simulation test database"""
        from simulation.core.database import Base
        Base.metadata.create_all(bind=get_sim_db().bind)
        yield
        Base.metadata.drop_all(bind=get_sim_db().bind)
    
    @pytest.fixture
    def simulation_user(self):
        """Create simulation test user"""
        return {
            "id": str(uuid4()),
            "email": "sim@test.com",
            "full_name": "Simulation Test User"
        }
    
    # FREQ-23: Simulation Environment
    @pytest.mark.asyncio
    async def test_freq23_simulation_environment_complete(self, setup_simulation_database, simulation_user):
        """Test complete simulation environment"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create simulation target
        target = sim_service.create_target(
            name="Test Target",
            description="Integration test target",
            category="web",
            difficulty="intermediate",
            technology_stack=["React", "Node.js", "PostgreSQL"],
            vulnerabilities=[
                {"type": "xss", "endpoint": "/search", "severity": "medium"},
                {"type": "sql_injection", "endpoint": "/api/users", "severity": "high"}
            ]
        )
        
        assert target.id is not None
        assert target.name == "Test Target"
        assert len(target.vulnerabilities) == 2
        
        # Test simulation start
        simulation = sim_service.start_simulation(
            user_id=simulation_user["id"],
            level="intermediate",
            target_id=str(target.id)
        )
        
        assert simulation.id is not None
        assert simulation.level == "intermediate"
        assert simulation.status == "active"
        assert simulation.max_hints == 2  # Intermediate level

    # FREQ-24: Simulation Workflow Mirroring
    @pytest.mark.asyncio
    async def test_freq24_simulation_workflow_complete(self, setup_simulation_database, simulation_user):
        """Test complete simulation workflow mirroring"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create and start simulation
        target = sim_service.create_target(
            name="Workflow Test Target",
            description="Workflow test target",
            category="web",
            difficulty="beginner",
            technology_stack=["React"],
            vulnerabilities=[{"type": "xss", "endpoint": "/test"}]
        )
        
        simulation = sim_service.start_simulation(
            user_id=simulation_user["id"],
            level="beginner",
            target_id=str(target.id)
        )
        
        # Test progress updates
        progress_steps = [
            {"status": "reconnaissance", "current_step": 1, "time_spent": 300},
            {"status": "scanning", "current_step": 3, "time_spent": 600},
            {"status": "exploitation", "current_step": 6, "time_spent": 900},
            {"status": "post_exploitation", "current_step": 8, "time_spent": 1200}
        ]
        
        for step in progress_steps:
            progress = sim_service.update_progress(
                simulation_id=str(simulation.id),
                **step
            )
            assert progress.current_step == step["current_step"]
            assert progress.status == step["status"]

    # FREQ-25: Simulation Difficulty Levels
    @pytest.mark.asyncio
    async def test_freq25_difficulty_levels_complete(self, setup_simulation_database, simulation_user):
        """Test all simulation difficulty levels"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Test all difficulty levels
        levels = sim_service.get_available_levels()
        expected_levels = ["beginner", "intermediate", "advanced", "expert"]
        
        assert len(levels) == 4
        for level in levels:
            assert level["level"] in expected_levels
            assert "time_limit" in level
            assert "max_hints" in level
        
        # Test each difficulty level
        target = sim_service.create_target(
            name="Difficulty Test Target",
            description="Test all difficulties",
            category="web",
            difficulty="beginner",
            technology_stack=["React"],
            vulnerabilities=[{"type": "test", "severity": "low"}]
        )
        
        for level_config in levels:
            simulation = sim_service.start_simulation(
                user_id=simulation_user["id"],
                level=level_config["level"],
                target_id=str(target.id)
            )
            
            assert simulation.level == level_config["level"]
            assert simulation.max_hints == level_config["max_hints"]
            assert simulation.expires_at > simulation.started_at

    # FREQ-26: Simulation Reporting
    @pytest.mark.asyncio
    async def test_freq26_simulation_reporting_complete(self, setup_simulation_database, simulation_user):
        """Test complete simulation reporting"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create and complete simulation
        target = sim_service.create_target(
            name="Reporting Test Target",
            description="Test reporting functionality",
            category="web",
            difficulty="intermediate",
            technology_stack=["React"],
            vulnerabilities=[
                {"type": "xss", "endpoint": "/test", "severity": "high", "valid": True},
                {"type": "sql_injection", "endpoint": "/api/users", "severity": "critical", "valid": True},
                {"type": "csrf", "endpoint": "/admin", "severity": "medium", "valid": False}  # False positive
            ]
        )
        
        simulation = sim_service.start_simulation(
            user_id=simulation_user["id"],
            level="intermediate",
            target_id=str(target.id)
        )
        
        # Submit simulation results
        findings = [
            {
                "type": "xss",
                "endpoint": "/test",
                "severity": "high",
                "valid": True,
                "description": "Cross-site scripting vulnerability"
            },
            {
                "type": "sql_injection",
                "endpoint": "/api/users",
                "severity": "critical",
                "valid": True,
                "description": "SQL injection vulnerability"
            },
            {
                "type": "csrf",
                "endpoint": "/admin",
                "severity": "medium",
                "valid": False,
                "description": "False positive - not a vulnerability"
            }
        ]
        
        result = sim_service.submit_result(
            simulation_id=str(simulation.id),
            findings=findings,
            time_taken=3600,  # 1 hour
            hints_used=1
        )
        
        assert result.score > 0
        assert result.accuracy == 2/3  # 2 out of 3 valid findings
        assert result.severity_accuracy > 0.8  # Good severity assessment
        
        # Test feedback generation
        feedback = sim_service.get_feedback(str(simulation.id))
        
        assert "feedback_points" in feedback
        assert "improvement_tips" in feedback
        assert len(feedback["feedback_points"]) > 0

    # FREQ-27: Simulation Data Isolation
    @pytest.mark.asyncio
    async def test_freq27_data_isolation_complete(self, setup_simulation_database, simulation_user):
        """Test complete simulation data isolation"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create isolated simulation
        target = sim_service.create_target(
            name="Isolation Test Target",
            description="Test data isolation",
            category="web",
            difficulty="advanced",
            technology_stack=["React"],
            vulnerabilities=[{"type": "rce", "endpoint": "/admin", "severity": "critical"}]
        )
        
        simulation = sim_service.start_simulation(
            user_id=simulation_user["id"],
            level="advanced",
            target_id=str(target.id)
        )
        
        # Test isolation features
        from simulation.services.isolation_service import IsolationService
        isolation_service = IsolationService(db)
        
        # Create isolation session
        isolation = isolation_service.create_isolation_session({
            "user_id": simulation_user["id"],
            "target_id": str(target.id),
            "simulation_type": "web",
            "duration": 7200  # 2 hours
        })
        
        assert isolation.id is not None
        assert isolation.isolation_type == "container"
        assert isolation.status == "active"
        assert isolation.cpu_limit == 1
        assert isolation.memory_limit == 1024
        
        # Test isolation termination
        terminated = isolation_service.terminate_session(str(isolation.id))
        assert terminated["success"] is True
        
        # Test isolation cleanup
        cleaned = isolation_service.cleanup_session(str(isolation.id))
        assert cleaned["success"] is True

    # FREQ-28: Simulation Feedback
    @pytest.mark.asyncio
    async def test_freq28_simulation_feedback_complete(self, setup_simulation_database, simulation_user):
        """Test complete simulation feedback system"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create simulation with different performance levels
        target = sim_service.create_target(
            name="Feedback Test Target",
            description="Test feedback system",
            category="web",
            difficulty="intermediate",
            technology_stack=["React"],
            vulnerabilities=[{"type": "xss", "endpoint": "/feedback", "severity": "medium"}]
        )
        
        # Test different performance scenarios
        scenarios = [
            {"time_taken": 1800, "hints_used": 0, "accuracy": 1.0},  # Perfect
            {"time_taken": 3600, "hints_used": 1, "accuracy": 0.8},  # Good
            {"time_taken": 5400, "hints_used": 2, "accuracy": 0.6},  # Needs improvement
        ]
        
        for i, scenario in enumerate(scenarios):
            simulation = sim_service.start_simulation(
                user_id=simulation_user["id"],
                level="intermediate",
                target_id=str(target.id)
            )
            
            result = sim_service.submit_result(
                simulation_id=str(simulation.id),
                findings=[{"type": "xss", "valid": True, "severity": "medium"}],
                time_taken=scenario["time_taken"],
                hints_used=scenario["hints_used"]
            )
            
            feedback = sim_service.get_feedback(str(simulation.id))
            
            # Verify feedback content
            assert "feedback_points" in feedback
            assert "improvement_tips" in feedback
            
            # Perfect performance should have positive feedback
            if scenario["accuracy"] == 1.0 and scenario["hints_used"] == 0:
                assert any("excellent" in point.lower() for point in feedback["feedback_points"])
            
            # Poor performance should have improvement tips
            if scenario["accuracy"] < 0.7:
                assert len(feedback["improvement_tips"]) >= 2

    # Business Rule BR-13: Simulation Privacy
    @pytest.mark.asyncio
    async def test_br13_simulation_privacy(self, setup_simulation_database, simulation_user):
        """Test BR-13: Simulation scores are private"""
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create multiple simulations for user
        target = sim_service.create_target(
            name="Privacy Test Target",
            description="Test privacy rules",
            category="web",
            difficulty="beginner",
            technology_stack=["React"],
            vulnerabilities=[{"type": "test", "severity": "low"}]
        )
        
        simulations = []
        for i in range(3):
            sim = sim_service.start_simulation(
                user_id=simulation_user["id"],
                level="beginner",
                target_id=str(target.id)
            )
            
            result = sim_service.submit_result(
                simulation_id=str(sim.id),
                findings=[{"type": "test", "valid": True}],
                time_taken=1800,
                hints_used=0
            )
            
            simulations.append(result)
        
        # Test leaderboard privacy
        leaderboard = sim_service.get_user_scores(simulation_user["id"])
        
        # All scores should be private to user
        for score in leaderboard:
            assert score.user_id == simulation_user["id"]
        
        # Test public leaderboard returns empty
        public_leaderboard = sim_service.get_score_leaderboard()
        assert public_leaderboard["leaderboard"] == []
        assert "private" in public_leaderboard["message"].lower()
        assert "business_rule" in public_leaderboard["message"].lower()

    # Cross-Platform Integration Tests
    @pytest.mark.asyncio
    async def test_main_simulation_integration(self, setup_simulation_database, simulation_user):
        """Test integration between main platform and simulation"""
        # Test that simulation progress affects main platform recommendations
        db = get_sim_db()
        sim_service = SimulationService(db)
        
        # Create simulation with specific skill focus
        target = sim_service.create_target(
            name="Integration Test Target",
            description="Test cross-platform integration",
            category="web",
            difficulty="advanced",
            technology_stack=["React", "Node.js", "PostgreSQL"],
            vulnerabilities=[
                {"type": "sql_injection", "severity": "high"},
                {"type": "xss", "severity": "medium"},
                {"type": "csrf", "severity": "low"}
            ]
        )
        
        simulation = sim_service.start_simulation(
            user_id=simulation_user["id"],
            level="advanced",
            target_id=str(target.id)
        )
        
        # Submit result showing SQL injection expertise
        result = sim_service.submit_result(
            simulation_id=str(simulation.id),
            findings=[
                {"type": "sql_injection", "valid": True, "severity": "high"},
                {"type": "xss", "valid": True, "severity": "medium"}
            ],
            time_taken=3600,
            hints_used=1
        )
        
        # Verify that simulation performance would be reflected in main platform
        # This would test the integration between simulation and main platform
        assert result.accuracy > 0.8  # Good performance
        assert result.score > 0
        
        # The main platform should use this data for recommendations
        # (This would be tested in the main platform integration tests)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
