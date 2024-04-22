import logging


def get_logger():
    """
    Get the logger for the service

    Returns:
        logger: The logger for the service
    """
    # get logger and configure it
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    return logger
