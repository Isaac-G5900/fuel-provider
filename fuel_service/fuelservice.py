import asyncio
import logging
import os
import obd
from kuksa_client.grpc import VSSClient, Datapoint

log = logging.getLogger(__name__)

class FuelService:
    def __init__(self, vdb_address: str):
        self._vdb_client = VSSClient(vdb_address)
        try:
            self._obd_connection = obd.OBD(
                port=os.getenv("OBD_PORT", "/dev/rfcomm0"),
                baudrate=int(os.getenv("OBD_BAUDRATE", "115200")),
                fast=False
            )
            log.info("Fuelservice initialized with VDB address: %s", vdb_address)
        except Exception as e:
            log.error(f"Failed to initialize OBD connection: {e}")
            raise

    async def main_loop(self):
        log.info("Starting FuelService...")
        while True:
            try:
                response = self._obd_connection.query(obd.commands.FUEL_LEVEL)
                if response.is_successful():
                    fuel_level = float(response.value.magnitude)
                    self._vdb_client.set_current_values({
                        "Vehicle.Powertrain.FuelSystem.Level": Datapoint(value=fuel_level)
                    })
                    log.info(f"Fuel level: {fuel_level}%")
                else:
                    log.warning("Failed to get fuel level reading")
            except Exception as e:
                log.error(f"Error reading fuel level: {e}")
            
            await asyncio.sleep(2)