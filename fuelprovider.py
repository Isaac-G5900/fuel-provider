from fuel_service.fuelservice import FuelService

import asyncio
import logging
import os
import signal

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def main():
    vdb_address = os.getenv("VDB_ADDRESS", "127.0.0.1:55555")
    service = FuelService(vdb_address)
    await service.main_loop()

def run():
    """Entry point for the service"""
    loop = asyncio.get_event_loop()
    
    # Handle graceful shutdown
    loop.add_signal_handler(signal.SIGTERM, loop.stop)
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

if __name__ == "__main__":
    run()

