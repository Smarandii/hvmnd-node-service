from loguru import logger
from hvmnd_node_service_manager.config import PATH_TO_LOG_FILE

logger.add(PATH_TO_LOG_FILE, rotation="10 MB", retention="10 days", level="INFO")
logger.info("Starting node service...")
