import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing service...")
    logger.info("Using SQLite, no explicit database creation needed.")
    logger.info("Service initialization finished.")

if __name__ == "__main__":
    asyncio.run(main())
