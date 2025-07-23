from fuel_service.fuelservice import FuelService

import asyncio
import logging
import os
import signal

SERVICE_NAME = "fuel_provider"
log = logging.getLogger(SERVICE_NAME)
log.setLevel(logging.INFO)

VDB_ADDRESS = os.getenv("VDB_ADDRESS", "127.0.0.1:55555")

async def main():
    fuel_service = FuelService(VDB_ADDRESS)  # Fixed reference
    await fuel_service.main_loop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log.setLevel(logging.DEBUG)
    LOOP = asyncio.get_event_loop()
    LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
    LOOP.run_until_complete(main())
    LOOP.close()

