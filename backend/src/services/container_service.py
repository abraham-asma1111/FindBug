"""
Container Orchestration Service
Manages Docker containers for simulation challenges
"""
from __future__ import annotations

import logging
import secrets
import socket
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import docker
from sqlalchemy.orm import Session

from src.core.config import settings
from src.domain.models.simulation import SimulationChallenge, SimulationInstance

logger = logging.getLogger(__name__)

ACADEMY_LAB_IMAGE = "findbug/academy-lab"

# Ports that must never be used for labs (3000 = frontend, 8080 = legacy WebGoat)
FORBIDDEN_LAB_PORTS = frozenset({3000, 8080})


def academy_lab_port() -> int:
    return int(settings.SIMULATION_LAB_PORT or 5050)

# Per-challenge paths on the branded FindBug Academy lab app
VULNERABILITY_LAB_PATHS: Dict[str, str] = {
    "sql_injection": "/challenges/sql-injection",
    "xss": "/challenges/reflected-xss",
    "jwt_attack": "/challenges/jwt-forgery",
    "ssrf": "/challenges/ssrf-fetch",
    "oauth_abuse": "/challenges/oauth-redirect",
    "race_condition": "/challenges/race-coupon",
}

# Legacy seed images still map to the same branded lab (not third-party UIs)
LEGACY_LAB_IMAGES = frozenset(
    {
        ACADEMY_LAB_IMAGE,
        "bkimminich/juice-shop",
        "webgoat/webgoat-8.0",
    }
)

IMAGE_CONTAINER_PORTS: Dict[str, int] = {
    ACADEMY_LAB_IMAGE: academy_lab_port(),
    "bkimminich/juice-shop": academy_lab_port(),
    "webgoat/webgoat-8.0": academy_lab_port(),
}


def academy_lab_base_url() -> str:
    host = settings.SIMULATION_LAB_HOST or "127.0.0.1"
    return f"http://{host}:{academy_lab_port()}"


def challenge_lab_url(challenge: SimulationChallenge) -> str:
    path = VULNERABILITY_LAB_PATHS.get(
        challenge.vulnerability_type or "", "/"
    )
    return f"{academy_lab_base_url()}{path}"


def uses_branded_academy_lab(challenge: SimulationChallenge) -> bool:
    image_key = (challenge.docker_image or "").split(":")[0]
    return image_key in LEGACY_LAB_IMAGES


class ContainerOrchestrationService:
    """Manages Docker container lifecycle for simulation challenges"""

    def __init__(self):
        self.docker_client = None
        self.docker_available = False
        self.active_instances: Dict[str, dict] = {}
        self._last_error: Optional[str] = None
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            self.docker_available = True
        except Exception as exc:
            self.docker_client = None
            self.docker_available = False
            self._last_error = str(exc)

    def container_port_for(self, challenge: SimulationChallenge) -> int:
        image = (challenge.docker_image or "").split(":")[0]
        if uses_branded_academy_lab(challenge):
            return academy_lab_port()
        port = int(challenge.exposed_port) if challenge.exposed_port else None
        if port in FORBIDDEN_LAB_PORTS:
            return academy_lab_port()
        if port:
            return port
        return IMAGE_CONTAINER_PORTS.get(image, academy_lab_port())

    def _lab_base_url(self, host_port: int) -> str:
        host = settings.SIMULATION_LAB_HOST or "127.0.0.1"
        return f"http://{host}:{host_port}"

    def _wait_for_port(self, host: str, port: int, timeout: int) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection((host, port), timeout=2):
                    return True
            except OSError:
                time.sleep(1)
        return False

    def _resolve_host_port(self, container, container_port: int) -> int:
        container.reload()
        ports = container.attrs.get("NetworkSettings", {}).get("Ports") or {}
        binding = ports.get(f"{container_port}/tcp")
        if binding and binding[0].get("HostPort"):
            return int(binding[0]["HostPort"])
        raise RuntimeError(
            f"Docker did not publish port {container_port}/tcp. "
            f"Published ports: {list(ports.keys())}"
        )

    def _port_is_open(self, host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            return False

    def try_shared_lab(
        self, challenge: SimulationChallenge
    ) -> Optional[Tuple[str, str]]:
        """Use shared FindBug Academy lab (docker compose) when port 5050 is up."""
        if not settings.SIMULATION_USE_SHARED_LABS:
            return None
        if not uses_branded_academy_lab(challenge):
            return None
        host = settings.SIMULATION_LAB_HOST or "127.0.0.1"
        if self._port_is_open(host, academy_lab_port()):
            return challenge_lab_url(challenge), "academy_lab"
        return None

    def resolve_embed_url(
        self, challenge: SimulationChallenge, instance: Optional[SimulationInstance] = None
    ) -> Optional[str]:
        """Stable lab URL for iframes — prefer shared stack on 5050."""
        shared = self.try_shared_lab(challenge)
        if shared:
            return shared[0]
        if instance and instance.unique_url:
            from urllib.parse import urlparse

            parsed = urlparse(instance.unique_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or academy_lab_port()
            if self._port_is_open(host, port):
                return instance.unique_url
        return None

    async def start_challenge_instance(
        self,
        db: Session,
        user_id,
        challenge_id,
        challenge: SimulationChallenge,
    ) -> dict:
        instance_id = secrets.token_urlsafe(8)

        shared = self.try_shared_lab(challenge)
        if shared:
            url, mode = shared
            return self._persist_instance(
                db,
                user_id,
                challenge_id,
                instance_id,
                url,
                None,
                mode,
                host_port=academy_lab_port(),
            )

        if getattr(settings, "SIMULATION_FORCE_SHARED_LAB", True):
            raise RuntimeError(
                f"Academy lab is not running on port {academy_lab_port()}. "
                "From the project root run: "
                "docker compose -f simulation/docker-compose.yml up -d"
            )

        if not self.docker_available or not self.docker_client:
            raise RuntimeError(
                f"Docker is not available ({self._last_error or 'daemon not running'}). "
                "Start Docker, then run: docker compose -f simulation/docker-compose.yml up -d "
                f"(FindBug Academy lab on port {academy_lab_port()}, not 3000)"
            )

        container_port = self.container_port_for(challenge)
        host = settings.SIMULATION_LAB_HOST or "127.0.0.1"

        try:
            cid = str(challenge_id).replace("-", "")[:8]
            name = f"sim-{cid}-{instance_id}".lower().replace("_", "-")[:63]
            container = self.docker_client.containers.run(
                image=challenge.docker_image,
                detach=True,
                name=name,
                ports={f"{container_port}/tcp": None},
                environment=challenge.environment_variables or {},
                labels={
                    "type": "simulation",
                    "user_id": str(user_id),
                    "challenge_id": str(challenge_id),
                    "instance_id": instance_id,
                },
                mem_limit=challenge.container_memory_limit or "512m",
                cpu_period=100000,
                cpu_quota=int(float(challenge.container_cpu_limit or "0.5") * 100000),
                remove=False,
            )
            host_port = self._resolve_host_port(container, container_port)
            timeout = settings.SIMULATION_CONTAINER_START_TIMEOUT
            if not self._wait_for_port(host, host_port, timeout):
                container.stop(timeout=5)
                container.remove(force=True)
                raise RuntimeError(
                    f"Lab container started but port {host_port} did not become reachable "
                    f"within {timeout}s. Try: docker pull {challenge.docker_image}"
                )

            if uses_branded_academy_lab(challenge):
                path = VULNERABILITY_LAB_PATHS.get(
                    challenge.vulnerability_type or "", "/"
                )
                unique_url = f"{self._lab_base_url(host_port)}{path}"
            else:
                unique_url = self._lab_base_url(host_port)

            return self._persist_instance(
                db,
                user_id,
                challenge_id,
                instance_id,
                unique_url,
                container.id,
                "docker",
                host_port=host_port,
            )

        except docker.errors.ImageNotFound:
            shared = self.try_shared_lab(challenge)
            if shared:
                url, mode = shared
                return self._persist_instance(
                    db, user_id, challenge_id, instance_id, url, None, mode
                )
            raise RuntimeError(
                f"Docker image not found: {challenge.docker_image}. "
                f"Run: docker pull {challenge.docker_image}"
            )
        except docker.errors.APIError as e:
            shared = self.try_shared_lab(challenge)
            if shared:
                url, mode = shared
                return self._persist_instance(
                    db, user_id, challenge_id, instance_id, url, None, mode
                )
            raise RuntimeError(f"Docker error: {e}") from e

    def _persist_instance(
        self,
        db: Session,
        user_id,
        challenge_id,
        instance_id: str,
        unique_url: str,
        container_id: Optional[str],
        mode: str,
        host_port: Optional[int] = None,
    ) -> dict:
        expires_at = datetime.utcnow() + timedelta(hours=2)
        db_instance = SimulationInstance(
            instance_id=instance_id,
            user_id=user_id,
            challenge_id=challenge_id,
            container_id=container_id,
            unique_url=unique_url,
            port=host_port,
            status="running",
            started_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        db.add(db_instance)
        db.commit()
        return {
            "instance_id": instance_id,
            "url": unique_url,
            "port": host_port,
            "expires_at": expires_at.isoformat(),
            "status": "running",
            "mode": mode,
            "reachable": True,
        }

    async def stop_challenge_instance(self, db: Session, instance_id: str) -> dict:
        db_instance = db.query(SimulationInstance).filter(
            SimulationInstance.instance_id == instance_id
        ).first()

        if not db_instance:
            raise Exception("Instance not found")

        if db_instance.container_id and self.docker_available and self.docker_client:
            try:
                container = self.docker_client.containers.get(db_instance.container_id)
                container.stop(timeout=10)
                container.remove(force=True)
            except docker.errors.NotFound:
                pass

        db_instance.status = "stopped"
        db_instance.stopped_at = datetime.utcnow()
        db.commit()

        if instance_id in self.active_instances:
            del self.active_instances[instance_id]

        return {
            "instance_id": instance_id,
            "status": "stopped",
            "message": "Instance stopped successfully",
        }
