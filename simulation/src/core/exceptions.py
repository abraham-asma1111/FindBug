"""
Core Exceptions for Simulation Platform
"""

class SimulationException(Exception):
    """Base exception for simulation platform"""
    pass

class NotFoundException(SimulationException):
    """Resource not found exception"""
    pass

class ForbiddenException(SimulationException):
    """Access forbidden exception"""
    pass

class ValidationException(SimulationException):
    """Validation error exception"""
    pass

class ContainerException(SimulationException):
    """Container management exception"""
    pass