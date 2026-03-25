"""
Container Orchestration Service
Manages Docker containers for simulation challenges
"""
import docker
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.domain.models.simulation import SimulationInstance, SimulationChallenge


class ContainerOrchestrationService:
    """Manages Docker container lifecycle for simulation challenges"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.active_instances: Dict[str, dict] = {}
    
    async def start_challenge_instance(
        self,
        db: Session,
        user_id: str,
        challenge_id: str,
        challenge: SimulationChallenge
    ) -> dict:
        """
        Spin up a Docker container for a challenge
        Returns instance info with unique URL
        """
        # Generate unique instance ID
        instance_id = secrets.token_urlsafe(8)
        
        # Get available port
        unique_port = self._get_available_port()
        
        # Start Docker container
        try:
            container = self.docker_client.containers.run(
                image=challenge.docker_image,
                detach=True,
                name=f"sim-{challenge_id[:8]}-{instance_id}",
                ports={f'{challenge.exposed_port}/tcp': unique_port},
                environment=challenge.environment_variables or {},
                labels={
                    'type': 'simulation',
                    'user_id': str(user_id),
                    'challenge_id': str(challenge_id),
                    'instance_id': instance_id,
                    'created_at': datetime.utcnow().isoformat()
                },
                # Resource limits
                mem_limit=challenge.container_memory_limit,
                cpu_period=100000,
                cpu_quota=int(float(challenge.container_cpu_limit) * 100000),
                # Network isolation
                network_mode='bridge',
                # Auto-remove when stopped
                auto_remove=False
            )
            
            # Generate unique URL
            # Option 1: Port-based URL
            unique_url = f"http://localhost:{unique_port}"
            # Option 2: Subdomain-based (requires reverse proxy setup)
            # unique_url = f"https://sim-{instance_id}.yourdomain.com"
            
            # Calculate expiration (2 hours from now)
            expires_at = datetime.utcnow() + timedelta(hours=2)
            
            # Save instance to database
            db_instance = SimulationInstance(
                instance_id=instance_id,
                user_id=user_id,
                challenge_id=challenge_id,
                container_id=container.id,
                unique_url=unique_url,
                port=unique_port,
                status="running",
                started_at=datetime.utcnow(),
                expires_at=expires_at
            )
            db.add(db_instance)
            db.commit()
            
            # Store in memory for quick access
            self.active_instances[instance_id] = {
                'container_id': container.id,
                'user_id': str(user_id),
                'challenge_id': str(challenge_id),
                'url': unique_url,
                'port': unique_port,
                'started_at': datetime.utcnow(),
                'expires_at': expires_at
            }
            
            return {
                'instance_id': instance_id,
                'url': unique_url,
                'port': unique_port,
                'expires_at': expires_at.isoformat(),
                'status': 'running'
            }
            
        except docker.errors.ImageNotFound:
            raise Exception(f"Docker image '{challenge.docker_image}' not found")
        except docker.errors.APIError as e:
            raise Exception(f"Docker API error: {str(e)}")
    
    async def stop_challenge_instance(
        self,
        db: Session,
        instance_id: str
    ) -> dict:
        """Stop and remove a challenge container"""
        # Get instance from database
        db_instance = db.query(SimulationInstance).filter(
            SimulationInstance.instance_id == instance_id
        ).first()
        
        if not db_instance:
            raise Exception("Instance not found")
        
        try:
            # Stop and remove container
            container = self.docker_client.containers.get(db_instance.container_id)
            container.stop(timeout=10)
            container.remove()
            
            # Update database
            db_instance.status = "stopped"
            db_instance.stopped_at = datetime.utcnow()
            db.commit()
            
            # Remove from memory
            if instance_id in self.active_instances:
                del self.active_instances[instance_id]
            
            return {
                'instance_id': instance_id,
                'status': 'stopped',
                'message': 'Instance stopped successfully'
            }
            
        except docker.errors.NotFound:
            # Container already removed
            db_instance.status = "stopped"
            db_instance.stopped_at = datetime.utcnow()
            db.commit()
            return {
                'instance_id': instance_id,
                'status': 'stopped',
                'message': 'Instance already stopped'
            }
    
    async def get_user_active_instance(
        self,
        db: Session,
        user_id: str,
        challenge_id: str
    ) -> Optional[SimulationInstance]:
        """Check if user already has an active instance for this challenge"""
        return db.query(SimulationInstance).filter(
            SimulationInstance.user_id == user_id,
            SimulationInstance.challenge_id == challenge_id,
            SimulationInstance.status == "running",
            SimulationInstance.expires_at > datetime.utcnow()
        ).first()
    
    async def cleanup_expired_instances(self, db: Session):
        """Background task to cleanup expired containers"""
        now = datetime.utcnow()
        
        # Get expired instances
        expired_instances = db.query(SimulationInstance).filter(
            SimulationInstance.status == "running",
            SimulationInstance.expires_at < now
        ).all()
        
        for instance in expired_instances:
            try:
                await self.stop_challenge_instance(db, instance.instance_id)
            except Exception as e:
                print(f"Error cleaning up instance {instance.instance_id}: {e}")
    
    def _get_available_port(self) -> int:
        """Get an available port for the container"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
