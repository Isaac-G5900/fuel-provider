"""
Fuel Provider Service - reads OBD-II fuel level and publishes to KUKSA Data Broker.
"""

from .fuelservice import FuelService

__all__ = ['FuelService']
