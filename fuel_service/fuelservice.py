import asyncio
import logging
import os
from typing import Optional
import obd
from kuksa_client.grpc import VSSClient, Datapoint

log = logging.getLogger(__name__)

class FuelService:
    def __init__(self, vdb_address: str):
        # Split address:port into components
        if ':' in vdb_address:
            address, port = vdb_address.split(':')
            port = int(port)
        else:
            address = vdb_address
            port = 55555  # Default KUKSA-val port
            
        self._vdb_client = VSSClient(address, port)
        self._obd_connection: Optional[obd.OBD] = None
        self._port = os.getenv("OBD_PORT", "/dev/rfcomm0")
        self._baudrate = int(os.getenv("OBD_BAUDRATE", "115200"))
        log.info("FuelService initialized with VDB address %s:%d", address, port)
        
    async def connect_obd(self) -> bool:
        """Try to connect to OBD device. Returns True if successful."""
        if self._obd_connection is not None:
            return True
            
        try:
            log.info("Attempting to connect to OBD device at %s", self._port)
            self._obd_connection = obd.OBD(self._port, self._baudrate,
                fast=False
            )
            if self._obd_connection.is_connected():
                log.info("Successfully connected to OBD device")
                return True
            else:
                log.warning("OBD connection failed - device reports not connected")
                self._obd_connection = None
                return False
        except Exception as e:
            log.warning(f"Failed to connect to OBD device: {e}")
            self._obd_connection = None
            return False

    async def main_loop(self):
        """Main service loop - keeps trying to connect and read fuel level."""
        log.info("Starting FuelService...")
        retry_interval = 5  # seconds between connection attempts
        
        while True:
            if not self._obd_connection or not self._obd_connection.is_connected():
                if await self.connect_obd():
                    # Reset retry interval on successful connect
                    retry_interval = 5
                else:
                    # Back off up to 30 seconds between retries
                    retry_interval = min(retry_interval * 1.5, 30)
                    log.info("Will retry connection in %.1f seconds", retry_interval)
                    await asyncio.sleep(retry_interval)
                    continue

            try:
                response = self._obd_connection.query(obd.commands.FUEL_LEVEL)
                if response.is_successful():
                    fuel_level = float(response.value.magnitude)
                    self._vdb_client.set_current_values({
                        "Vehicle.Powertrain.FuelSystem.Level": Datapoint(value=fuel_level)
                    })
                    log.info("Fuel level: %.1f%%", fuel_level)
                    await asyncio.sleep(2)  # Normal polling interval
                else:
                    log.warning("Failed to get fuel level reading")
                    await asyncio.sleep(1)  # Retry sooner on read failure
            except Exception as e:
                log.error("Error reading fuel level: %s", e)
                self._obd_connection = None  # Force reconnect
                await asyncio.sleep(1)